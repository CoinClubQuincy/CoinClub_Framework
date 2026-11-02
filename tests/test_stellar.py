from decimal import Decimal

import pytest
from stellar_sdk.memo import IdMemo, TextMemo

from coinclub import Asset, MainnetNotAllowedError, ValidationError, connect
from coinclub.chains.stellar import StellarChain, _memo


def record(**overrides):
    base = {
        "type": "payment",
        "transaction_successful": True,
        "transaction_hash": "HASH",
        "asset_type": "native",
        "amount": "2.5000000",
        "from": "GFROM",
        "to": "GTO",
        "created_at": "2026-01-01T00:00:00Z",
        "transaction": {"memo_type": "id", "memo": "42"},
    }
    base.update(overrides)
    return base


def test_wallet_round_trip():
    chain = connect("stellar")
    wallet = chain.create_wallet()
    assert chain.is_valid_address(wallet.address)
    assert chain.wallet_from_secret(wallet.secret).address == wallet.address


def test_bad_secret_is_rejected_without_quoting_it():
    with pytest.raises(ValidationError) as caught:
        connect("stellar").wallet_from_secret("SBADSECRET")
    assert "SBADSECRET" not in str(caught.value)


def test_mainnet_write_is_blocked_before_any_network_use():
    chain = connect("stellar", "mainnet")
    with pytest.raises(MainnetNotAllowedError):
        chain.transfer(chain.create_wallet(), chain.create_wallet().address, "1")


def test_numeric_reference_becomes_id_memo_and_text_becomes_text_memo():
    assert isinstance(_memo("42"), IdMemo)
    assert isinstance(_memo("order-7"), TextMemo)
    assert _memo(None) is None


def test_memo_over_the_limit_is_rejected():
    with pytest.raises(ValidationError):
        _memo("x" * 29)


def test_payment_record_parses():
    payment = StellarChain._payment_from_record(record())
    assert payment.amount == Decimal("2.5")
    assert payment.asset == StellarChain.native
    assert payment.reference == "42"
    assert payment.timestamp == 1767225600.0


def test_token_payment_record_parses():
    payment = StellarChain._payment_from_record(
        record(asset_type="credit_alphanum4", asset_code="USD", asset_issuer="GISSUER")
    )
    assert payment.asset == Asset("USD", "GISSUER")


def test_create_account_counts_as_a_payment():
    payment = StellarChain._payment_from_record(
        record(type="create_account", starting_balance="10", funder="GF", account="GA")
    )
    assert payment.amount == 10
    assert payment.sender == "GF"
    assert payment.destination == "GA"


def test_failed_transaction_is_ignored():
    assert StellarChain._payment_from_record(record(transaction_successful=False)) is None


def test_other_operations_are_ignored():
    assert StellarChain._payment_from_record(record(type="manage_sell_offer")) is None


def test_hash_memo_is_not_used_as_a_reference():
    payment = StellarChain._payment_from_record(
        record(transaction={"memo_type": "hash", "memo": "abc"})
    )
    assert payment.reference is None


def test_cancel_needs_both_assets():
    chain = connect("stellar")
    with pytest.raises(ValidationError):
        chain.cancel_offer(chain.create_wallet(), 1)
