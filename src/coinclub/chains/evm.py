"""EVM adapter for XDC, Flare, Filecoin (FEVM) and Ethereum, built on web3.py."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from eth_account import Account
from web3 import Web3
from web3.exceptions import ContractLogicError, TimeExhausted, TransactionNotFound, Web3Exception
from web3.middleware import ExtraDataToPOAMiddleware

from ..errors import (
    NetworkError,
    NotFoundError,
    TransactionFailedError,
    ValidationError,
)
from ..models import CONFIRMED, FAILED, PENDING, Asset, Balance, Receipt, Wallet, to_positive
from .base import Chain, NetworkConfig

NATIVE_DECIMALS = 18
RECEIPT_TIMEOUT_SECONDS = 180
ERC20_ABI: list[dict[str, Any]] = [
    {
        "name": "balanceOf",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "owner", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "decimals",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint8"}],
    },
    {
        "name": "transfer",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}],
        "outputs": [{"name": "", "type": "bool"}],
    },
]


def _to_base_units(amount: Decimal, decimals: int) -> int:
    scaled = amount.scaleb(decimals)
    if scaled != scaled.to_integral_value():
        raise ValidationError(f"amount has more than {decimals} decimal places")
    return int(scaled)


class EvmChain(Chain):
    """Shared behaviour for account-based EVM chains. Subclasses declare their networks."""

    chain_ids: dict[str, int] = {}
    poa = False

    def __init__(
        self,
        network: str | None = None,
        *,
        url: str | None = None,
        allow_mainnet: bool = False,
        provider: Any = None,
        receipt_timeout: int = RECEIPT_TIMEOUT_SECONDS,
    ):
        super().__init__(network, url=url, allow_mainnet=allow_mainnet)
        self.web3 = Web3(provider or Web3.HTTPProvider(self.url, request_kwargs={"timeout": 30}))
        if self.poa:
            self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.receipt_timeout = receipt_timeout
        self.expected_chain_id = None if provider else self.chain_ids[self.network]

    # Addresses and wallets

    @staticmethod
    def normalize_address(address: str) -> str:
        """Accept 0x addresses and XDC's xdc-prefixed form."""
        if address[:3].lower() == "xdc":
            return "0x" + address[3:]
        return address

    def is_valid_address(self, address: str) -> bool:
        return Web3.is_address(self.normalize_address(address))

    def _checksum(self, address: str) -> str:
        self._require_address(address)
        return Web3.to_checksum_address(self.normalize_address(address))

    def create_wallet(self) -> Wallet:
        account = Account.create()
        return Wallet(self.name, account.address, account.key.hex())

    def wallet_from_secret(self, secret: str) -> Wallet:
        try:
            account = Account.from_key(secret)
        except Exception:
            raise ValidationError("not a valid private key") from None
        return Wallet(self.name, account.address, secret)

    # Reads

    def balances(self, address: str) -> list[Balance]:
        """Return the native balance. EVM has no account token index: see token_balance."""
        wei = self._rpc(lambda: self.web3.eth.get_balance(self._checksum(address)))
        return [Balance(self.native, Decimal(wei).scaleb(-NATIVE_DECIMALS))]

    def balance(self, address: str, asset: Asset | None = None) -> Decimal:
        if asset is not None and not asset.is_native:
            assert asset.issuer is not None
            return self.token_balance(address, asset.issuer)
        return self.balances(address)[0].amount

    def token_balance(self, address: str, token: str) -> Decimal:
        contract = self.erc20(token)
        raw = self._rpc(lambda: contract.functions.balanceOf(self._checksum(address)).call())
        decimals = self._rpc(lambda: contract.functions.decimals().call())
        return Decimal(raw).scaleb(-decimals)

    def erc20(self, token: str) -> Any:
        return self.contract(token, ERC20_ABI)

    def contract(self, address: str, abi: list[dict[str, Any]]) -> Any:
        """Return a web3 contract. Read with .functions.x().call() and write with transact()."""
        return self.web3.eth.contract(address=self._checksum(address), abi=abi)

    def transaction(self, tx_id: str) -> Receipt:
        try:
            return self._receipt(self.web3.eth.get_transaction_receipt(tx_id), tx_id)
        except TransactionNotFound:
            pass
        except Web3Exception as exc:
            raise NetworkError(str(exc)) from exc
        try:
            pending = self.web3.eth.get_transaction(tx_id)
        except TransactionNotFound as exc:
            raise NotFoundError(f"no transaction {tx_id}") from exc
        return Receipt(self.name, self.network, tx_id, PENDING, dict(pending))

    def _receipt(self, data: Any, tx_id: str) -> Receipt:
        status = CONFIRMED if data["status"] == 1 else FAILED
        return Receipt(self.name, self.network, tx_id, status, dict(data))

    @staticmethod
    def _rpc(call: Any) -> Any:
        try:
            return call()
        except (Web3Exception, OSError) as exc:
            raise NetworkError(str(exc)) from exc

    # Writes

    def _verify_chain_id(self) -> None:
        """Stop a wrong url from signing a transaction meant for another chain."""
        if self.expected_chain_id is None:
            return
        actual = self._rpc(lambda: self.web3.eth.chain_id)
        if actual != self.expected_chain_id:
            raise NetworkError(
                f"{self.url} is chain {actual}, expected {self.name}:{self.network} "
                f"({self.expected_chain_id})"
            )

    def _fee_fields(self) -> dict[str, int]:
        latest = self._rpc(lambda: self.web3.eth.get_block("latest"))
        base_fee = latest.get("baseFeePerGas")
        if base_fee is None:
            return {"gasPrice": self._rpc(lambda: self.web3.eth.gas_price)}
        tip = self._rpc(lambda: self.web3.eth.max_priority_fee)
        return {"maxFeePerGas": base_fee * 2 + tip, "maxPriorityFeePerGas": tip}

    def _send(self, wallet: Wallet, tx: dict[str, Any], wait: bool) -> Receipt:
        self._require_write()
        self._require_wallet(wallet)
        self._verify_chain_id()
        sender = Web3.to_checksum_address(wallet.address)
        tx.setdefault("from", sender)
        tx.setdefault("chainId", self._rpc(lambda: self.web3.eth.chain_id))
        tx.setdefault(
            "nonce", self._rpc(lambda: self.web3.eth.get_transaction_count(sender, "pending"))
        )
        for key, value in self._fee_fields().items():
            tx.setdefault(key, value)
        try:
            tx.setdefault("gas", self.web3.eth.estimate_gas(tx))
        except ContractLogicError as exc:
            raise TransactionFailedError(f"execution would revert: {exc}") from exc
        except (Web3Exception, OSError, ValueError) as exc:
            raise NetworkError(f"gas estimation failed: {exc}") from exc
        signed = Account.sign_transaction(tx, wallet.secret)
        tx_hash = self._rpc(lambda: self.web3.eth.send_raw_transaction(signed.raw_transaction))
        tx_id = Web3.to_hex(tx_hash)
        if not wait:
            return Receipt(self.name, self.network, tx_id, PENDING)
        try:
            data = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=self.receipt_timeout)
        except TimeExhausted:
            return Receipt(self.name, self.network, tx_id, PENDING)
        receipt = self._receipt(data, tx_id)
        if receipt.status == FAILED:
            raise TransactionFailedError("transaction reverted", tx_id=tx_id)
        return receipt

    def transfer(
        self,
        wallet: Wallet,
        to: str,
        amount: Decimal | str | int,
        *,
        asset: Asset | None = None,
        reference: str | None = None,
        wait: bool = True,
    ) -> Receipt:
        value = to_positive(amount)
        recipient = self._checksum(to)
        if asset is not None and not asset.is_native:
            if reference is not None:
                raise ValidationError("an ERC-20 transfer cannot carry a reference")
            assert asset.issuer is not None
            contract = self.erc20(asset.issuer)
            decimals = self._rpc(lambda: contract.functions.decimals().call())
            call = contract.functions.transfer(recipient, _to_base_units(value, decimals))
            return self.transact(wallet, call, wait=wait)
        tx: dict[str, Any] = {"to": recipient, "value": _to_base_units(value, NATIVE_DECIMALS)}
        if reference is not None:
            tx["data"] = Web3.to_hex(text=reference)
        return self._send(wallet, tx, wait)

    def transact(self, wallet: Wallet, call: Any, *, value: int = 0, wait: bool = True) -> Receipt:
        """Send a contract call, from contract(...).functions.name(...). value is in wei."""
        sender = Web3.to_checksum_address(wallet.address)
        try:
            tx = call.build_transaction({"from": sender, "value": value, "gas": 0})
        except ContractLogicError as exc:
            raise TransactionFailedError(f"execution would revert: {exc}") from exc
        except (Web3Exception, OSError) as exc:
            raise NetworkError(str(exc)) from exc
        tx.pop("gas", None)
        tx.pop("maxFeePerGas", None)
        tx.pop("maxPriorityFeePerGas", None)
        tx.pop("gasPrice", None)
        return self._send(wallet, dict(tx), wait)


class XdcChain(EvmChain):
    name = "xdc"
    native = Asset("XDC")
    default_network = "apothem"
    poa = True
    chain_ids = {"mainnet": 50, "apothem": 51}
    networks = {
        "mainnet": NetworkConfig("https://rpc.xinfin.network", mainnet=True),
        "apothem": NetworkConfig("https://rpc.apothem.network"),
    }


class FlareChain(EvmChain):
    name = "flare"
    native = Asset("FLR")
    default_network = "coston2"
    chain_ids = {"mainnet": 14, "songbird": 19, "coston": 16, "coston2": 114}
    networks = {
        "mainnet": NetworkConfig("https://flare-api.flare.network/ext/C/rpc", mainnet=True),
        "songbird": NetworkConfig("https://songbird-api.flare.network/ext/C/rpc", mainnet=True),
        "coston": NetworkConfig("https://coston-api.flare.network/ext/C/rpc"),
        "coston2": NetworkConfig("https://coston2-api.flare.network/ext/C/rpc"),
    }


class FilecoinChain(EvmChain):
    """Filecoin through its EVM runtime. This uses 0x addresses, not native f1 or f3 addresses."""

    name = "filecoin"
    native = Asset("FIL")
    default_network = "calibration"
    chain_ids = {"mainnet": 314, "calibration": 314159}
    networks = {
        "mainnet": NetworkConfig("https://api.node.glif.io/rpc/v1", mainnet=True),
        "calibration": NetworkConfig("https://api.calibration.node.glif.io/rpc/v1"),
    }


class EthereumChain(EvmChain):
    name = "ethereum"
    native = Asset("ETH")
    default_network = "sepolia"
    chain_ids = {"mainnet": 1, "sepolia": 11155111}
    networks = {
        "mainnet": NetworkConfig("https://ethereum-rpc.publicnode.com", mainnet=True),
        "sepolia": NetworkConfig("https://ethereum-sepolia-rpc.publicnode.com"),
    }
