"""Real signing with a fake node, since the Algorand test faucet needs a browser."""

import base64
from decimal import Decimal

import pytest
from algosdk import mnemonic
from algosdk.transaction import SuggestedParams

from coinclub import Asset, MainnetNotAllowedError, ValidationError, connect


class FakeAlgod:
    def __init__(self):
        self.sent = []

    def suggested_params(self):
        genesis = base64.b64encode(b"\x01" * 32).decode()
        return SuggestedParams(1000, 1, 1000, genesis, "testnet", True)

    def send_transaction(self, signed):
        self.sent.append(signed)
        return signed.transaction.get_txid()

    def account_info(self, address):
        return {"amount": 2500000, "assets": [{"asset-id": 7, "amount": 1234}]}

    def asset_info(self, asset_id):
        return {"params": {"unit-name": "TOK", "decimals": 2}}


@pytest.fixture
def chain():
    return connect("algorand", algod_client=FakeAlgod(), indexer_client=object())


def test_wallet_round_trip(chain):
    wallet = chain.create_wallet()
    assert chain.is_valid_address(wallet.address)
    assert chain.wallet_from_secret(wallet.secret).address == wallet.address


def test_bad_mnemonic_is_rejected_without_quoting_it(chain):
    with pytest.raises(ValidationError) as caught:
        chain.wallet_from_secret("not a real mnemonic")
    assert "not a real" not in str(caught.value)


def test_balances_scale_by_decimals(chain):
    balances = chain.balances(chain.create_wallet().address)
    assert balances[0].amount == Decimal("2.5")
    assert balances[1].asset == Asset("TOK", "7")
    assert balances[1].amount == Decimal("12.34")


def test_transfer_signs_a_correct_payment(chain):
    wallet, to = chain.create_wallet(), chain.create_wallet().address
    receipt = chain.transfer(wallet, to, "1.5", reference="42", wait=False)
    signed = chain.algod.sent[0]
    assert signed.transaction.amt == 1_500_000
    assert signed.transaction.receiver == to
    assert signed.transaction.note == b"42"
    assert receipt.tx_id == signed.transaction.get_txid()
    assert signed.signature


def test_token_transfer_scales_by_asset_decimals(chain):
    wallet, to = chain.create_wallet(), chain.create_wallet().address
    chain.transfer(wallet, to, "1.5", asset=Asset("TOK", "7"), wait=False)
    signed = chain.algod.sent[0]
    assert signed.transaction.amount == 150
    assert signed.transaction.index == 7


def test_too_much_precision_is_rejected(chain):
    wallet, to = chain.create_wallet(), chain.create_wallet().address
    with pytest.raises(ValidationError, match="decimal places"):
        chain.transfer(wallet, to, "0.0000001", wait=False)


def test_oversized_note_is_rejected(chain):
    wallet, to = chain.create_wallet(), chain.create_wallet().address
    with pytest.raises(ValidationError):
        chain.transfer(wallet, to, "1", reference="x" * 1025, wait=False)


def test_mainnet_write_is_blocked():
    chain = connect("algorand", "mainnet", algod_client=FakeAlgod(), indexer_client=object())
    wallet = chain.create_wallet()
    with pytest.raises(MainnetNotAllowedError):
        chain.transfer(wallet, wallet.address, "1")


def test_payment_record_reads_the_note(chain):
    payment = chain._payment_from_record(
        {
            "tx-type": "pay",
            "id": "TX",
            "sender": "S",
            "round-time": 100,
            "note": base64.b64encode(b"42").decode(),
            "payment-transaction": {"receiver": "R", "amount": 2_000_000},
        }
    )
    assert payment.amount == 2
    assert payment.reference == "42"
    assert payment.timestamp == 100.0


def test_asset_payment_record_scales(chain):
    payment = chain._payment_from_record(
        {
            "tx-type": "axfer",
            "id": "TX",
            "sender": "S",
            "asset-transfer-transaction": {"asset-id": 7, "receiver": "R", "amount": 250},
        }
    )
    assert payment.asset == Asset("TOK", "7")
    assert payment.amount == Decimal("2.5")


def test_other_transaction_types_are_ignored(chain):
    assert chain._payment_from_record({"tx-type": "appl"}) is None


def test_secret_is_a_valid_mnemonic(chain):
    assert len(mnemonic.to_private_key(chain.create_wallet().secret)) > 0
