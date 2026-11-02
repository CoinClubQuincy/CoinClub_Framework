from decimal import Decimal

import pytest

from coinclub import Asset, MainnetNotAllowedError, ValidationError, connect
from coinclub.chains.xrpl import XrplChain, decode_currency, encode_currency


def payment_entry(**overrides):
    entry = {
        "validated": True,
        "hash": "ABC",
        "close_time_iso": "2026-01-01T00:00:00Z",
        "meta": {"TransactionResult": "tesSUCCESS", "delivered_amount": "1000000"},
        "tx_json": {
            "TransactionType": "Payment",
            "Account": "rSender",
            "Destination": "rDest",
            "DestinationTag": 42,
            "DeliverMax": "1000000",
        },
    }
    entry.update(overrides)
    return entry


def test_wallet_round_trip():
    chain = connect("xrpl")
    wallet = chain.create_wallet()
    assert chain.is_valid_address(wallet.address)
    assert chain.wallet_from_secret(wallet.secret).address == wallet.address


def test_bad_seed_is_rejected_without_quoting_it():
    with pytest.raises(ValidationError) as caught:
        connect("xrpl").wallet_from_secret("not-a-real-seed")
    assert "not-a-real-seed" not in str(caught.value)


def test_invalid_address_is_rejected_before_the_network():
    chain = connect("xrpl")
    with pytest.raises(ValidationError):
        chain.transfer(chain.create_wallet(), "rNotAnAddress", "1")
    with pytest.raises(ValidationError):
        chain.balances("rNotAnAddress")


def test_mainnet_write_is_blocked_before_any_network_use():
    chain = connect("xrpl", "mainnet")
    with pytest.raises(MainnetNotAllowedError):
        chain.transfer(chain.create_wallet(), chain.create_wallet().address, "1")
    with pytest.raises(MainnetNotAllowedError):
        chain.submit(chain.create_wallet(), "AccountSet")


def test_payment_counts_delivered_amount_not_requested_amount():
    """The partial payment exploit: a huge Amount that delivers almost nothing."""
    entry = payment_entry()
    entry["tx_json"]["Amount"] = "999999999999"
    entry["meta"]["delivered_amount"] = "1"
    payment = XrplChain._payment_from_entry(entry)
    assert payment.amount == Decimal("0.000001")


@pytest.mark.parametrize("delivered", [None, "unavailable"])
def test_payment_without_a_trustworthy_delivered_amount_is_ignored(delivered):
    entry = payment_entry()
    entry["meta"]["delivered_amount"] = delivered
    assert XrplChain._payment_from_entry(entry) is None


def test_failed_payment_is_ignored():
    entry = payment_entry()
    entry["meta"]["TransactionResult"] = "tecUNFUNDED_PAYMENT"
    assert XrplChain._payment_from_entry(entry) is None


def test_unvalidated_payment_is_ignored():
    assert XrplChain._payment_from_entry(payment_entry(validated=False)) is None


def test_other_transaction_types_are_ignored():
    entry = payment_entry()
    entry["tx_json"]["TransactionType"] = "OfferCreate"
    assert XrplChain._payment_from_entry(entry) is None


def test_payment_reads_tag_timestamp_and_identifiers():
    payment = XrplChain._payment_from_entry(payment_entry())
    assert payment.reference == "42"
    assert payment.tx_id == "ABC"
    assert payment.sender == "rSender"
    assert payment.asset == XrplChain.native
    assert payment.timestamp == 1767225600.0


def test_payment_reads_ripple_epoch_date_on_older_api_rows():
    entry = payment_entry(close_time_iso=None)
    entry["tx_json"]["date"] = 0
    assert XrplChain._payment_from_entry(entry).timestamp == 946684800.0


def test_payment_reads_issued_currency_and_memo():
    entry = payment_entry()
    del entry["tx_json"]["DestinationTag"]
    entry["tx_json"]["Memos"] = [{"Memo": {"MemoData": b"order-7".hex()}}]
    entry["meta"]["delivered_amount"] = {"currency": "USD", "issuer": "rIssuer", "value": "2.5"}
    payment = XrplChain._payment_from_entry(entry)
    assert payment.asset == Asset("USD", "rIssuer")
    assert payment.amount == Decimal("2.5")
    assert payment.reference == "order-7"


def test_currency_codes_round_trip():
    assert encode_currency("USD") == "USD"
    long = encode_currency("COINCLUB")
    assert len(long) == 40
    assert decode_currency(long) == "COINCLUB"
    assert decode_currency("USD") == "USD"


@pytest.mark.parametrize("bad", ["XRP", "AB", "x" * 21])
def test_invalid_currency_codes_are_rejected(bad):
    with pytest.raises(ValidationError):
        encode_currency(bad)


def test_unknown_transaction_type_is_rejected():
    chain = connect("xrpl")
    with pytest.raises(ValidationError, match="unknown XRPL transaction"):
        chain.submit(chain.create_wallet(), "NotATransaction")


def test_invalid_transaction_fields_are_rejected():
    chain = connect("xrpl")
    with pytest.raises(ValidationError, match="invalid Payment"):
        chain.build(chain.create_wallet(), "Payment", amount="1")


@pytest.mark.parametrize(
    "name",
    ["AccountSet", "AccountDelete", "CheckCancel", "CheckCash", "CheckCreate", "DepositPreauth",
     "EscrowCancel", "EscrowCreate", "EscrowFinish", "OfferCancel", "OfferCreate", "Payment",
     "PaymentChannelClaim", "PaymentChannelCreate", "PaymentChannelFund", "SetRegularKey",
     "SignerListSet", "TicketCreate", "TrustSet"],
)
def test_every_transaction_type_from_the_old_framework_is_buildable(name):
    from xrpl.models import transactions

    assert isinstance(getattr(transactions, name), type)


def test_old_read_commands_exist_as_methods():
    for name in ["account_channels", "account_currencies", "account_info", "account_lines",
                 "account_objects", "account_offers", "account_tx", "book_offers",
                 "channel_verify", "deposit_authorized", "gateway_balances", "ledger",
                 "ripple_path_find", "feature"]:
        assert callable(getattr(XrplChain, name))


def test_trustline_on_native_asset_is_rejected():
    chain = connect("xrpl")
    with pytest.raises(ValidationError):
        chain.add_trustline(chain.create_wallet(), chain.native)
