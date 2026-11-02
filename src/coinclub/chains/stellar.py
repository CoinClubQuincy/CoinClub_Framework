"""Stellar adapter, built on stellar-sdk."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal
from typing import Any

import requests
from stellar_sdk import (
    Asset as StellarAsset,
)
from stellar_sdk import (
    ChangeTrust,
    CreateAccount,
    Keypair,
    ManageSellOffer,
    Network,
    Server,
    StrKey,
    TransactionBuilder,
)
from stellar_sdk import (
    Payment as PaymentOp,
)
from stellar_sdk.exceptions import (
    BadRequestError,
    BaseHorizonError,
    ConnectionError,
    Ed25519SecretSeedInvalidError,
)
from stellar_sdk.exceptions import (
    NotFoundError as HorizonNotFoundError,
)
from stellar_sdk.memo import IdMemo, Memo, TextMemo
from stellar_sdk.operation import Operation

from ..errors import (
    NetworkError,
    NotFoundError,
    TransactionFailedError,
    UnsupportedOperationError,
    ValidationError,
)
from ..models import (
    CONFIRMED,
    FAILED,
    Asset,
    Balance,
    BookOffer,
    Payment,
    Receipt,
    Wallet,
    to_positive,
)
from .base import Chain, NetworkConfig

FRIENDBOT = "https://friendbot.stellar.org"
MAX_MEMO_ID = 2**64 - 1
MAX_MEMO_TEXT_BYTES = 28
TX_TIMEOUT_SECONDS = 60


def _memo(reference: str | None) -> Memo | None:
    if reference is None:
        return None
    if reference.isdigit() and int(reference) <= MAX_MEMO_ID:
        return IdMemo(int(reference))
    if len(reference.encode()) <= MAX_MEMO_TEXT_BYTES:
        return TextMemo(reference)
    raise ValidationError(f"a Stellar memo holds {MAX_MEMO_TEXT_BYTES} bytes at most")


def _sdk_asset(asset: Asset) -> StellarAsset:
    if asset.is_native:
        return StellarAsset.native()
    return StellarAsset(asset.code, asset.issuer)


def _asset_from_record(record: dict[str, Any]) -> Asset:
    if record.get("asset_type") == "native":
        return StellarChain.native
    return Asset(record["asset_code"], record["asset_issuer"])


class StellarChain(Chain):
    name = "stellar"
    native = Asset("XLM")
    default_network = "testnet"
    networks = {
        "mainnet": NetworkConfig("https://horizon.stellar.org", mainnet=True),
        "testnet": NetworkConfig("https://horizon-testnet.stellar.org"),
    }

    def __init__(
        self, network: str | None = None, *, url: str | None = None, allow_mainnet: bool = False
    ):
        super().__init__(network, url=url, allow_mainnet=allow_mainnet)
        self.server = Server(self.url)
        self.passphrase = (
            Network.PUBLIC_NETWORK_PASSPHRASE
            if self.is_mainnet
            else Network.TESTNET_NETWORK_PASSPHRASE
        )

    # Wallets

    def create_wallet(self) -> Wallet:
        keypair = Keypair.random()
        return Wallet(self.name, keypair.public_key, keypair.secret)

    def wallet_from_secret(self, secret: str) -> Wallet:
        try:
            keypair = Keypair.from_secret(secret)
        except Ed25519SecretSeedInvalidError:
            raise ValidationError("not a valid Stellar secret") from None
        return Wallet(self.name, keypair.public_key, secret)

    def is_valid_address(self, address: str) -> bool:
        return StrKey.is_valid_ed25519_public_key(address)

    def request_test_funds(self, wallet: Wallet) -> None:
        if self.is_mainnet:
            raise UnsupportedOperationError("mainnet has no faucet")
        self._require_wallet(wallet)
        response = requests.get(FRIENDBOT, params={"addr": wallet.address}, timeout=60)
        if not response.ok:
            raise NetworkError(f"friendbot returned {response.status_code}")

    # Reads

    def _call(self, builder: Any) -> dict[str, Any]:
        try:
            return builder.call()
        except HorizonNotFoundError as exc:
            raise NotFoundError(str(exc)) from exc
        except (BaseHorizonError, ConnectionError) as exc:
            raise NetworkError(str(exc)) from exc

    def balances(self, address: str) -> list[Balance]:
        self._require_address(address)
        try:
            account = self._call(self.server.accounts().account_id(address))
        except NotFoundError:
            return [Balance(self.native, Decimal(0))]
        items = [Balance(_asset_from_record(b), Decimal(b["balance"])) for b in account["balances"]
                 if b["asset_type"] != "liquidity_pool_shares"]
        return sorted(items, key=lambda b: not b.asset.is_native)

    def transaction(self, tx_id: str) -> Receipt:
        record = self._call(self.server.transactions().transaction(tx_id))
        status = CONFIRMED if record.get("successful") else FAILED
        return Receipt(self.name, self.network, tx_id, status, record)

    def incoming_payments(self, address: str, *, limit: int = 100) -> list[Payment]:
        self._require_address(address)
        builder = (
            self.server.payments()
            .for_account(address)
            .order(desc=True)
            .limit(limit)
            .include_failed(False)
            .join("transactions")
        )
        records = self._call(builder)["_embedded"]["records"]
        payments = map(self._payment_from_record, records)
        return [p for p in payments if p and p.destination == address]

    @staticmethod
    def _payment_from_record(record: dict[str, Any]) -> Payment | None:
        if not record.get("transaction_successful", True):
            return None
        kind = record.get("type")
        if kind == "create_account":
            asset, amount = StellarChain.native, Decimal(record["starting_balance"])
            sender, destination = record["funder"], record["account"]
        elif kind in ("payment", "path_payment_strict_send", "path_payment_strict_receive"):
            # For path payments, amount is what the destination received.
            asset, amount = _asset_from_record(record), Decimal(record["amount"])
            sender, destination = record["from"], record["to"]
        else:
            return None
        tx = record.get("transaction") or {}
        memo = tx.get("memo") if tx.get("memo_type") in ("id", "text") else None
        created = record.get("created_at")
        timestamp = (
            datetime.fromisoformat(created.replace("Z", "+00:00")).timestamp() if created else None
        )
        return Payment(
            tx_id=record["transaction_hash"],
            sender=sender,
            destination=destination,
            asset=asset,
            amount=amount,
            reference=str(memo) if memo is not None else None,
            timestamp=timestamp,
        )

    # Writes

    def submit(
        self, wallet: Wallet, operations: Iterable[Operation], *, memo: Memo | None = None
    ) -> Receipt:
        """Sign and submit any Stellar operations in one transaction. Horizon waits for the ledger.

        >>> chain.submit(wallet, [ManageData("key", "value")])
        """
        self._require_write()
        self._require_wallet(wallet)
        try:
            account = self.server.load_account(wallet.address)
            builder = TransactionBuilder(
                account, self.passphrase, base_fee=self.server.fetch_base_fee()
            ).set_timeout(TX_TIMEOUT_SECONDS)
            for operation in operations:
                builder.append_operation(operation)
            if memo is not None:
                builder.add_memo(memo)
            envelope = builder.build()
            envelope.sign(Keypair.from_secret(wallet.secret))
            result = self.server.submit_transaction(envelope)
        except HorizonNotFoundError as exc:
            raise NotFoundError(f"account not found: {wallet.address}") from exc
        except BadRequestError as exc:
            codes = (exc.extras or {}).get("result_codes", {})
            raise TransactionFailedError(f"rejected: {codes}", code=str(codes)) from exc
        except (BaseHorizonError, ConnectionError) as exc:
            raise NetworkError(str(exc)) from exc
        status = CONFIRMED if result.get("successful", True) else FAILED
        receipt = Receipt(self.name, self.network, result["hash"], status, result)
        if status == FAILED:
            raise TransactionFailedError("transaction failed", tx_id=receipt.tx_id)
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
        self._require_address(to)
        value = to_positive(amount)
        operation = PaymentOp(to, _sdk_asset(asset or self.native), value)
        return self.submit(wallet, [operation], memo=_memo(reference))

    def create_account(
        self, wallet: Wallet, to: str, starting_balance: Decimal | str | int
    ) -> Receipt:
        """Create and fund a new account. A plain transfer to a missing account is rejected."""
        self._require_address(to)
        value = to_positive(starting_balance, name="starting_balance")
        return self.submit(wallet, [CreateAccount(to, value)])

    def add_trustline(
        self, wallet: Wallet, asset: Asset, limit: Decimal | str | int | None = None
    ) -> Receipt:
        if asset.is_native:
            raise ValidationError("XLM does not use trust lines")
        ceiling = to_positive(limit, name="limit") if limit is not None else None
        return self.submit(wallet, [ChangeTrust(_sdk_asset(asset), ceiling)])

    # DEX

    def order_book(self, base: Asset, quote: Asset, *, limit: int = 20) -> list[BookOffer]:
        book = self._call(
            self.server.orderbook(_sdk_asset(base), _sdk_asset(quote)).limit(limit)
        )
        return [BookOffer(Decimal(a["price"]), Decimal(a["amount"])) for a in book.get("asks", [])]

    def place_offer(
        self,
        wallet: Wallet,
        *,
        selling: Asset,
        buying: Asset,
        amount: Decimal | str | int,
        price: Decimal | str | int,
    ) -> Receipt:
        operation = ManageSellOffer(
            _sdk_asset(selling),
            _sdk_asset(buying),
            to_positive(amount),
            to_positive(price, name="price"),
        )
        return self.submit(wallet, [operation])

    def cancel_offer(
        self,
        wallet: Wallet,
        offer_id: int,
        *,
        selling: Asset | None = None,
        buying: Asset | None = None,
    ) -> Receipt:
        if selling is None or buying is None:
            raise ValidationError("cancelling a Stellar offer needs its selling and buying assets")
        operation = ManageSellOffer(
            _sdk_asset(selling), _sdk_asset(buying), Decimal(0), Decimal(1), offer_id=offer_id
        )
        return self.submit(wallet, [operation])

    def offers(self, address: str) -> list[dict[str, Any]]:
        """Return an account's open offers as Horizon records."""
        self._require_address(address)
        return self._call(self.server.offers().for_seller(address))["_embedded"]["records"]
