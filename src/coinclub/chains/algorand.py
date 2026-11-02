"""Algorand adapter, built on py-algorand-sdk."""

from __future__ import annotations

import base64
from decimal import Decimal
from typing import Any

from algosdk import account, encoding, mnemonic, transaction
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    sign_transaction_with_signer,
)
from algosdk.error import AlgodHTTPError, IndexerHTTPError, WrongMnemonicLengthError
from algosdk.transaction import SuggestedParams
from algosdk.v2client import algod, indexer

from ..errors import NetworkError, NotFoundError, TransactionFailedError, ValidationError
from ..models import (
    CONFIRMED,
    FAILED,
    PENDING,
    Asset,
    Balance,
    Payment,
    Receipt,
    Wallet,
    to_positive,
)
from .base import Chain, NetworkConfig

MICRO = 6
CONFIRMATION_ROUNDS = 8
MAX_NOTE_BYTES = 1024
INDEXERS = {
    "mainnet": "https://mainnet-idx.algonode.cloud",
    "testnet": "https://testnet-idx.algonode.cloud",
}


def _to_base_units(amount: Decimal, decimals: int) -> int:
    scaled = amount.scaleb(decimals)
    if scaled != scaled.to_integral_value():
        raise ValidationError(f"amount has more than {decimals} decimal places")
    return int(scaled)


class AlgorandChain(Chain):
    """Tokens are Algorand Standard Assets: Asset(code, issuer=<asset ID as a string>)."""

    name = "algorand"
    native = Asset("ALGO")
    default_network = "testnet"
    networks = {
        "mainnet": NetworkConfig("https://mainnet-api.algonode.cloud", mainnet=True),
        "testnet": NetworkConfig("https://testnet-api.algonode.cloud"),
    }

    def __init__(
        self,
        network: str | None = None,
        *,
        url: str | None = None,
        allow_mainnet: bool = False,
        indexer_url: str | None = None,
        api_token: str = "",
        algod_client: Any = None,
        indexer_client: Any = None,
    ):
        super().__init__(network, url=url, allow_mainnet=allow_mainnet)
        self.algod = algod_client or algod.AlgodClient(api_token, self.url)
        self.indexer = indexer_client or indexer.IndexerClient(
            api_token, indexer_url or INDEXERS[self.network]
        )

    # Wallets. The secret is the 25-word mnemonic.

    def create_wallet(self) -> Wallet:
        private_key, address = account.generate_account()
        return Wallet(self.name, address, mnemonic.from_private_key(private_key))

    def wallet_from_secret(self, secret: str) -> Wallet:
        try:
            private_key = mnemonic.to_private_key(secret)
        except (WrongMnemonicLengthError, ValueError, KeyError):
            raise ValidationError("not a valid Algorand mnemonic") from None
        return Wallet(self.name, account.address_from_private_key(private_key), secret)

    def is_valid_address(self, address: str) -> bool:
        return encoding.is_valid_address(address)

    # Reads

    def balances(self, address: str) -> list[Balance]:
        self._require_address(address)
        try:
            info = self.algod.account_info(address)
            result = [Balance(self.native, Decimal(info["amount"]).scaleb(-MICRO))]
            for holding in info.get("assets", []):
                asset_id = holding["asset-id"]
                params = self.algod.asset_info(asset_id)["params"]
                code = params.get("unit-name") or str(asset_id)
                amount = Decimal(holding["amount"]).scaleb(-params.get("decimals", 0))
                result.append(Balance(Asset(code, str(asset_id)), amount))
            return result
        except AlgodHTTPError as exc:
            raise NetworkError(str(exc)) from exc

    def transaction(self, tx_id: str) -> Receipt:
        try:
            record = self.indexer.transaction(tx_id)["transaction"]
            return Receipt(self.name, self.network, tx_id, CONFIRMED, record)
        except IndexerHTTPError:
            pass
        try:
            pending = self.algod.pending_transaction_info(tx_id)
        except AlgodHTTPError as exc:
            raise NotFoundError(f"no transaction {tx_id}") from exc
        if pending.get("pool-error"):
            return Receipt(self.name, self.network, tx_id, FAILED, pending)
        status = CONFIRMED if pending.get("confirmed-round") else PENDING
        return Receipt(self.name, self.network, tx_id, status, pending)

    def incoming_payments(self, address: str, *, limit: int = 100) -> list[Payment]:
        self._require_address(address)
        try:
            result = self.indexer.search_transactions(
                address=address, address_role="receiver", limit=limit
            )
        except IndexerHTTPError as exc:
            raise NetworkError(str(exc)) from exc
        return [p for p in map(self._payment_from_record, result.get("transactions", [])) if p]

    def _payment_from_record(self, record: dict[str, Any]) -> Payment | None:
        if record.get("tx-type") == "pay":
            detail = record["payment-transaction"]
            destination, asset = detail["receiver"], self.native
            amount = Decimal(detail["amount"]).scaleb(-MICRO)
        elif record.get("tx-type") == "axfer":
            detail = record["asset-transfer-transaction"]
            asset_id = detail["asset-id"]
            params = self.algod.asset_info(asset_id)["params"]
            destination = detail["receiver"]
            asset = Asset(params.get("unit-name") or str(asset_id), str(asset_id))
            amount = Decimal(detail["amount"]).scaleb(-params.get("decimals", 0))
        else:
            return None
        note = record.get("note")
        reference = base64.b64decode(note).decode(errors="replace") if note else None
        return Payment(
            tx_id=record["id"],
            sender=record["sender"],
            destination=destination,
            asset=asset,
            amount=amount,
            reference=reference,
            timestamp=float(record["round-time"]) if record.get("round-time") else None,
        )

    def _suggested_params(self) -> SuggestedParams:
        try:
            return self.algod.suggested_params()
        except AlgodHTTPError as exc:
            raise NetworkError(str(exc)) from exc

    # Writes

    def submit(self, wallet: Wallet, txn: Any, *, wait: bool = True) -> Receipt:
        """Sign and send any algosdk transaction, including application calls."""
        self._require_write()
        self._require_wallet(wallet)
        signer = AccountTransactionSigner(mnemonic.to_private_key(wallet.secret))
        signed = sign_transaction_with_signer(txn, signer)
        try:
            tx_id = self.algod.send_transaction(signed)
            if not wait:
                return Receipt(self.name, self.network, tx_id, PENDING)
            result = transaction.wait_for_confirmation(self.algod, tx_id, CONFIRMATION_ROUNDS)
        except AlgodHTTPError as exc:
            raise TransactionFailedError(f"rejected: {exc}") from exc
        except Exception as exc:
            raise NetworkError(f"no confirmation: {exc}") from exc
        return Receipt(self.name, self.network, tx_id, CONFIRMED, result)

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
        self._require_write()
        self._require_wallet(wallet)
        self._require_address(to)
        value = to_positive(amount)
        note = reference.encode() if reference is not None else None
        if note is not None and len(note) > MAX_NOTE_BYTES:
            raise ValidationError(f"an Algorand note holds {MAX_NOTE_BYTES} bytes at most")
        params = self._suggested_params()
        if asset is None or asset.is_native:
            txn = transaction.PaymentTxn(
                wallet.address, params, to, _to_base_units(value, MICRO), note=note
            )
        else:
            assert asset.issuer is not None
            asset_id = int(asset.issuer)
            decimals = self.algod.asset_info(asset_id)["params"].get("decimals", 0)
            txn = transaction.AssetTransferTxn(
                wallet.address, params, to, _to_base_units(value, decimals), asset_id, note=note
            )
        return self.submit(wallet, txn, wait=wait)

    def add_trustline(
        self, wallet: Wallet, asset: Asset, limit: Decimal | str | int | None = None
    ) -> Receipt:
        """Opt in to an asset, which Algorand requires before a wallet can hold it."""
        if asset.is_native:
            raise ValidationError("ALGO needs no opt-in")
        if limit is not None:
            raise ValidationError("an Algorand opt-in has no limit")
        self._require_write()
        self._require_wallet(wallet)
        assert asset.issuer is not None
        txn = transaction.AssetOptInTxn(wallet.address, self._suggested_params(), int(asset.issuer))
        return self.submit(wallet, txn)
