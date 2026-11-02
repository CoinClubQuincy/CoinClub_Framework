"""XRP Ledger adapter, built on xrpl-py."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import xrpl.core.addresscodec as addresscodec
import xrpl.models.transactions as tx_models
from xrpl.clients import JsonRpcClient
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import GenericRequest
from xrpl.models.transactions.transaction import Transaction
from xrpl.transaction import (
    XRPLReliableSubmissionException,
    autofill,
    multisign,
    sign,
    submit_and_wait,
)
from xrpl.utils import drops_to_xrp, xrp_to_drops
from xrpl.wallet import Wallet as XrplWallet
from xrpl.wallet import generate_faucet_wallet

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
    PENDING,
    Asset,
    Balance,
    BookOffer,
    Payment,
    Receipt,
    Wallet,
    to_positive,
)
from .base import Chain, NetworkConfig

RIPPLE_EPOCH = 946684800
MAX_DESTINATION_TAG = 2**32 - 1

# Read methods of the rippled API, exposed as chain.<name>(**params). Admin methods on your own
# node, such as log_level or validation_create, go through chain.rpc(method, **params).
RPC_METHODS = (
    "account_channels",
    "account_currencies",
    "account_info",
    "account_lines",
    "account_nfts",
    "account_objects",
    "account_offers",
    "account_tx",
    "book_offers",
    "channel_verify",
    "deposit_authorized",
    "fee",
    "feature",
    "gateway_balances",
    "ledger",
    "ledger_closed",
    "ledger_current",
    "ledger_entry",
    "noripple_check",
    "ripple_path_find",
    "server_info",
    "server_state",
)


def encode_currency(code: str) -> str:
    """Three-letter codes pass through. Longer ones become the 160-bit hex form the ledger uses."""
    if len(code) == 3 and code.upper() != "XRP":
        return code
    if len(code) == 40:
        return code.upper()
    raw = code.encode()
    if not 3 < len(raw) <= 20:
        raise ValidationError(f"XRPL currency code must be 3 to 20 bytes: {code!r}")
    return raw.hex().upper().ljust(40, "0")


def decode_currency(code: str) -> str:
    if len(code) != 40:
        return code
    try:
        text = bytes.fromhex(code).rstrip(b"\x00").decode()
    except (ValueError, UnicodeDecodeError):
        return code
    return text if text.isprintable() and text else code


def _parse_amount(value: Any) -> tuple[Asset, Decimal]:
    if isinstance(value, dict):
        return Asset(decode_currency(value["currency"]), value["issuer"]), Decimal(value["value"])
    return XrplChain.native, drops_to_xrp(str(value))


def _decode_memos(tx: dict[str, Any]) -> str | None:
    for item in tx.get("Memos") or []:
        data = item.get("Memo", {}).get("MemoData")
        if data:
            try:
                return bytes.fromhex(data).decode()
            except (ValueError, UnicodeDecodeError):
                return data
    return None


class XrplChain(Chain):
    name = "xrpl"
    native = Asset("XRP")
    default_network = "testnet"
    networks = {
        "mainnet": NetworkConfig("https://xrplcluster.com", mainnet=True),
        "testnet": NetworkConfig("https://s.altnet.rippletest.net:51234"),
        "devnet": NetworkConfig("https://s.devnet.rippletest.net:51234"),
    }

    def __init__(
        self, network: str | None = None, *, url: str | None = None, allow_mainnet: bool = False
    ):
        super().__init__(network, url=url, allow_mainnet=allow_mainnet)
        self.client = JsonRpcClient(self.url)

    # Wallets

    def create_wallet(self) -> Wallet:
        created = XrplWallet.create()
        if created.seed is None:
            raise ValidationError("xrpl-py returned a wallet with no seed")
        return Wallet(self.name, created.address, created.seed)

    def wallet_from_secret(self, secret: str) -> Wallet:
        try:
            loaded = XrplWallet.from_seed(secret)
        except Exception:
            # The original exception is dropped because its text can quote the seed.
            raise ValidationError("not a valid XRPL seed") from None
        return Wallet(self.name, loaded.address, secret)

    def is_valid_address(self, address: str) -> bool:
        return addresscodec.is_valid_classic_address(address)

    def request_test_funds(self, wallet: Wallet) -> None:
        if self.is_mainnet:
            raise UnsupportedOperationError("mainnet has no faucet")
        self._require_wallet(wallet)
        generate_faucet_wallet(self.client, XrplWallet.from_seed(wallet.secret))

    # Raw API

    def rpc(self, method: str, **params: Any) -> dict[str, Any]:
        """Call any rippled method and return its result. Errors raise."""
        try:
            response = self.client.request(GenericRequest(method=method, **params))
        except Exception as exc:
            raise NetworkError(f"{method} failed: {exc}") from exc
        if not response.is_successful():
            error = response.result.get("error", "unknown")
            if error in ("actNotFound", "txnNotFound", "objectNotFound", "entryNotFound"):
                raise NotFoundError(f"{method}: {error}")
            detail = response.result.get("error_message", error)
            raise NetworkError(f"{method} returned {error}: {detail}")
        return response.result

    # Reads

    def balances(self, address: str) -> list[Balance]:
        self._require_address(address)
        try:
            info = self.rpc("account_info", account=address, ledger_index="validated")
        except NotFoundError:
            return [Balance(self.native, Decimal(0))]
        result = [Balance(self.native, drops_to_xrp(info["account_data"]["Balance"]))]
        params: dict[str, Any] = {"account": address, "ledger_index": "validated"}
        while True:
            page = self.rpc("account_lines", **params)
            for line in page.get("lines", []):
                asset = Asset(decode_currency(line["currency"]), line["account"])
                result.append(Balance(asset, Decimal(line["balance"])))
            if "marker" not in page:
                return result
            params["marker"] = page["marker"]

    def transaction(self, tx_id: str) -> Receipt:
        result = self.rpc("tx", transaction=tx_id)
        return self._receipt_from_result(result, tx_id)

    def _receipt_from_result(self, result: dict[str, Any], tx_id: str | None = None) -> Receipt:
        identifier = tx_id or result.get("hash") or result.get("tx_json", {}).get("hash", "")
        if not result.get("validated"):
            return Receipt(self.name, self.network, identifier, PENDING, result)
        outcome = (result.get("meta") or {}).get("TransactionResult")
        status = CONFIRMED if outcome == "tesSUCCESS" else FAILED
        return Receipt(self.name, self.network, identifier, status, result)

    def incoming_payments(self, address: str, *, limit: int = 100) -> list[Payment]:
        self._require_address(address)
        result = self.rpc(
            "account_tx", account=address, limit=limit, ledger_index_min=-1, ledger_index_max=-1
        )
        return [p for p in map(self._payment_from_entry, result.get("transactions", [])) if p
                and p.destination == address]

    @staticmethod
    def _payment_from_entry(entry: dict[str, Any]) -> Payment | None:
        """Read one account_tx row, counting only what the ledger actually delivered.

        Using the transaction's Amount field would allow the partial payment exploit, where the
        Amount is large but tfPartialPayment delivers almost nothing. Only meta.delivered_amount
        is trusted, and a row without it is skipped.
        """
        tx = entry.get("tx_json") or entry.get("tx") or {}
        meta = entry.get("meta") or {}
        if not isinstance(meta, dict) or not entry.get("validated"):
            return None
        if tx.get("TransactionType") != "Payment" or meta.get("TransactionResult") != "tesSUCCESS":
            return None
        delivered = meta.get("delivered_amount")
        if delivered in (None, "unavailable"):
            return None
        asset, amount = _parse_amount(delivered)
        tag = tx.get("DestinationTag")
        timestamp = None
        if tx.get("date") is not None:
            timestamp = float(tx["date"] + RIPPLE_EPOCH)
        elif entry.get("close_time_iso"):
            from datetime import datetime

            timestamp = datetime.fromisoformat(
                entry["close_time_iso"].replace("Z", "+00:00")
            ).timestamp()
        return Payment(
            tx_id=entry.get("hash") or tx.get("hash", ""),
            sender=tx["Account"],
            destination=tx["Destination"],
            asset=asset,
            amount=amount,
            reference=str(tag) if tag is not None else _decode_memos(tx),
            timestamp=timestamp,
        )

    # Writes

    def _amount(self, asset: Asset, amount: Decimal) -> str | IssuedCurrencyAmount:
        if asset.is_native:
            return xrp_to_drops(amount)
        assert asset.issuer is not None
        return IssuedCurrencyAmount(
            currency=encode_currency(asset.code), issuer=asset.issuer, value=str(amount)
        )

    def build(self, wallet: Wallet, transaction: str, **fields: Any) -> Transaction:
        """Build any XRPL transaction by type name, such as AccountSet or EscrowCreate."""
        model = getattr(tx_models, transaction, None)
        if not (isinstance(model, type) and issubclass(model, Transaction)):
            raise ValidationError(f"unknown XRPL transaction type: {transaction!r}")
        fields.setdefault("account", wallet.address)
        try:
            return model(**fields)
        except Exception as exc:
            raise ValidationError(f"invalid {transaction}: {exc}") from exc

    def submit(self, wallet: Wallet, transaction: Transaction | str, **fields: Any) -> Receipt:
        """Sign, submit and wait for validation. Accepts every XRPL transaction type.

        >>> chain.submit(wallet, "AccountSet", domain="6578616d706c652e636f6d")
        """
        self._require_write()
        self._require_wallet(wallet)
        if isinstance(transaction, str):
            transaction = self.build(wallet, transaction, **fields)
        signer = XrplWallet.from_seed(wallet.secret)
        return self._submit_and_wait(lambda: submit_and_wait(transaction, self.client, signer))

    def _submit_and_wait(self, send: Any) -> Receipt:
        try:
            response = send()
        except XRPLReliableSubmissionException as exc:
            raise TransactionFailedError(str(exc)) from exc
        except TransactionFailedError:
            raise
        except Exception as exc:
            raise NetworkError(f"submission failed: {exc}") from exc
        receipt = self._receipt_from_result(response.result)
        if receipt.status == FAILED:
            code = (receipt.raw.get("meta") or {}).get("TransactionResult")
            raise TransactionFailedError(f"ledger result {code}", code=code, tx_id=receipt.tx_id)
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
        self._require_write()
        self._require_wallet(wallet)
        self._require_address(to)
        value = to_positive(amount)
        fields: dict[str, Any] = {
            "destination": to,
            "amount": self._amount(asset or self.native, value),
        }
        if reference is not None:
            if reference.isdigit() and int(reference) <= MAX_DESTINATION_TAG:
                fields["destination_tag"] = int(reference)
            else:
                fields["memos"] = [tx_models.Memo(memo_data=reference.encode().hex())]
        if not wait:
            raise ValidationError("XRPL transfers always wait for validation")
        return self.submit(wallet, "Payment", **fields)

    def add_trustline(
        self, wallet: Wallet, asset: Asset, limit: Decimal | str | int | None = None
    ) -> Receipt:
        if asset.is_native:
            raise ValidationError("XRP does not use trust lines")
        ceiling = to_positive(limit if limit is not None else "1000000000", name="limit")
        limit_amount = self._amount(asset, ceiling)
        return self.submit(wallet, "TrustSet", limit_amount=limit_amount)

    # DEX

    def order_book(self, base: Asset, quote: Asset, *, limit: int = 20) -> list[BookOffer]:
        result = self.rpc(
            "book_offers",
            taker_gets=self._book_side(base),
            taker_pays=self._book_side(quote),
            limit=limit,
            ledger_index="validated",
        )
        book = []
        for offer in result.get("offers", []):
            _, amount = _parse_amount(offer["TakerGets"])
            _, cost = _parse_amount(offer["TakerPays"])
            if amount > 0:
                book.append(BookOffer(cost / amount, amount))
        return book

    @staticmethod
    def _book_side(asset: Asset) -> dict[str, str]:
        if asset.is_native:
            return {"currency": "XRP"}
        assert asset.issuer is not None
        return {"currency": encode_currency(asset.code), "issuer": asset.issuer}

    def place_offer(
        self,
        wallet: Wallet,
        *,
        selling: Asset,
        buying: Asset,
        amount: Decimal | str | int,
        price: Decimal | str | int,
    ) -> Receipt:
        quantity = to_positive(amount)
        rate = to_positive(price, name="price")
        total = quantity * rate
        if buying.is_native:
            # XRP has six decimal places, and xrp_to_drops rejects anything finer.
            total = total.quantize(Decimal("0.000001"))
        return self.submit(
            wallet,
            "OfferCreate",
            taker_gets=self._amount(selling, quantity),
            taker_pays=self._amount(buying, total),
        )

    def cancel_offer(
        self,
        wallet: Wallet,
        offer_id: int,
        *,
        selling: Asset | None = None,
        buying: Asset | None = None,
    ) -> Receipt:
        return self.submit(wallet, "OfferCancel", offer_sequence=offer_id)

    # Multi-signing

    def prepare_multisigned(
        self, account: str, transaction: str, signers: int, **fields: Any
    ) -> Transaction:
        """Build and autofill a transaction that signers will sign separately."""
        placeholder = Wallet(self.name, account, "")
        built = self.build(placeholder, transaction, **fields)
        return autofill(built, self.client, signers)

    def sign_for(self, wallet: Wallet, transaction: Transaction) -> Transaction:
        """Add one signer's signature. The result goes to submit_multisigned."""
        self._require_wallet(wallet)
        return sign(transaction, XrplWallet.from_seed(wallet.secret), multisign=True)

    def submit_multisigned(
        self, transaction: Transaction, signed: list[Transaction]
    ) -> Receipt:
        self._require_write()
        combined = multisign(transaction, signed)
        return self._submit_and_wait(lambda: submit_and_wait(combined, self.client))


def _rpc_method(method: str) -> Any:
    def call(self: XrplChain, **params: Any) -> dict[str, Any]:
        return self.rpc(method, **params)

    call.__name__ = method
    call.__doc__ = f"Call the rippled {method} method."
    return call


for _method in RPC_METHODS:
    setattr(XrplChain, _method, _rpc_method(_method))
