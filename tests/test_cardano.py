"""Real transaction building and signing against a fake chain context."""

from decimal import Decimal
from fractions import Fraction

import pytest
from pycardano import (
    Address,
    ChainContext,
    GenesisParameters,
    Network,
    ProtocolParameters,
    TransactionId,
    TransactionInput,
    TransactionOutput,
    UTxO,
    Value,
)
from pycardano import MultiAsset as PyMultiAsset

from coinclub import Asset, CoinClubError, MainnetNotAllowedError, ValidationError, connect
from coinclub.chains.cardano import _chunks

POLICY = "ab" * 28
NAME = "cd" * 4


class FakeContext(ChainContext):
    def __init__(self):
        self.funds: dict[str, list[UTxO]] = {}
        self.submitted = []

    @property
    def protocol_param(self):
        return ProtocolParameters(
            min_fee_constant=155381, min_fee_coefficient=44, max_block_size=90112,
            max_tx_size=16384, max_block_header_size=1100, key_deposit=2000000,
            pool_deposit=500000000, pool_influence=Fraction(3, 10),
            monetary_expansion=Fraction(3, 1000), treasury_expansion=Fraction(2, 10),
            decentralization_param=Fraction(0), extra_entropy="", protocol_major_version=9,
            protocol_minor_version=0, min_utxo=1000000, min_pool_cost=340000000,
            price_mem=Fraction(577, 10000), price_step=Fraction(721, 10000000),
            max_tx_ex_mem=14000000, max_tx_ex_steps=10000000000, max_block_ex_mem=62000000,
            max_block_ex_steps=20000000000, max_val_size=5000, collateral_percent=150,
            max_collateral_inputs=3, coins_per_utxo_word=34482, coins_per_utxo_byte=4310,
            cost_models={},
        )

    @property
    def genesis_param(self):
        return GenesisParameters(
            active_slots_coefficient=Fraction(1, 20), update_quorum=5,
            max_lovelace_supply=45 * 10**15, network_magic=1, epoch_length=432000,
            system_start=1654041600, slots_per_kes_period=129600,
            slot_length=1, max_kes_evolutions=62, security_param=2160,
        )

    @property
    def network(self):
        return Network.TESTNET

    @property
    def epoch(self):
        return 100

    @property
    def last_block_slot(self):
        return 5000

    def utxos(self, address):
        return self.funds.get(str(address), [])

    def submit_tx(self, tx):
        self.submitted.append(tx)
        return str(tx.id)

    def fund(self, address, lovelace, tokens=None):
        value = Value(lovelace, PyMultiAsset.from_primitive(tokens) if tokens else PyMultiAsset())
        index = len(self.funds.get(address, []))
        tx_in = TransactionInput(TransactionId(b"\x01" * 32), index)
        utxo = UTxO(tx_in, TransactionOutput(Address.from_primitive(address), value))
        self.funds.setdefault(address, []).append(utxo)


@pytest.fixture
def chain():
    return connect("cardano", context=FakeContext())


def test_wallet_round_trip(chain):
    wallet = chain.create_wallet()
    assert chain.is_valid_address(wallet.address)
    assert wallet.address.startswith("addr_test")
    assert chain.wallet_from_secret(wallet.secret).address == wallet.address


def test_mainnet_address_is_not_valid_on_a_test_network(chain):
    mainnet = connect("cardano", "mainnet", context=FakeContext())
    assert not chain.is_valid_address(mainnet.create_wallet().address)


@pytest.mark.parametrize("bad", ["zz", "ab" * 31])
def test_bad_key_is_rejected_without_quoting_it(chain, bad):
    with pytest.raises(ValidationError) as caught:
        chain.wallet_from_secret(bad)
    assert bad not in str(caught.value)


def test_missing_api_key_gives_a_clear_error(monkeypatch):
    monkeypatch.delenv("BLOCKFROST_PROJECT_ID", raising=False)
    chain = connect("cardano")
    with pytest.raises(CoinClubError, match="Blockfrost"):
        chain.balances(chain.create_wallet().address)


def test_balances_sum_across_utxos(chain):
    wallet = chain.create_wallet()
    tokens = {bytes.fromhex(POLICY): {bytes.fromhex(NAME): 5}}
    chain.context.fund(wallet.address, 1_500_000)
    chain.context.fund(wallet.address, 2_000_000, tokens)
    balances = chain.balances(wallet.address)
    assert balances[0].amount == Decimal("3.5")
    assert balances[1].asset == Asset(NAME, POLICY)
    assert balances[1].amount == 5


def test_transfer_builds_signs_and_submits(chain):
    wallet, to = chain.create_wallet(), chain.create_wallet().address
    chain.context.fund(wallet.address, 50_000_000)
    receipt = chain.transfer(wallet, to, "5", reference="order-7", wait=False)
    tx = chain.context.submitted[0]
    assert receipt.tx_id == str(tx.id)
    outputs = tx.transaction_body.outputs
    assert any(o.amount.coin == 5_000_000 and str(o.address) == to for o in outputs)
    assert len(tx.transaction_witness_set.vkey_witnesses) == 1
    assert tx.auxiliary_data is not None


def test_token_transfer_includes_minimum_ada(chain):
    wallet, to = chain.create_wallet(), chain.create_wallet().address
    tokens = {bytes.fromhex(POLICY): {bytes.fromhex(NAME): 9}}
    chain.context.fund(wallet.address, 50_000_000, tokens)
    chain.transfer(wallet, to, "4", asset=Asset(NAME, POLICY), wait=False)
    outputs = chain.context.submitted[0].transaction_body.outputs
    sent = next(o for o in outputs if str(o.address) == to)
    assert sent.amount.coin > 0
    assert sent.amount.multi_asset.to_primitive()[bytes.fromhex(POLICY)][bytes.fromhex(NAME)] == 4


def test_fractional_token_amount_is_rejected(chain):
    wallet, to = chain.create_wallet(), chain.create_wallet().address
    with pytest.raises(ValidationError):
        chain.transfer(wallet, to, "1.5", asset=Asset(NAME, POLICY), wait=False)


def test_insufficient_funds_raises(chain):
    from coinclub import TransactionFailedError

    wallet, to = chain.create_wallet(), chain.create_wallet().address
    with pytest.raises(TransactionFailedError):
        chain.transfer(wallet, to, "5", wait=False)


def test_mainnet_write_is_blocked():
    chain = connect("cardano", "mainnet", context=FakeContext())
    wallet = chain.create_wallet()
    with pytest.raises(MainnetNotAllowedError):
        chain.transfer(wallet, wallet.address, "1")


def test_metadata_chunks_fit_cip20_and_keep_characters_whole():
    text = "é" * 100
    chunks = _chunks(text)
    assert all(len(chunk.encode()) <= 64 for chunk in chunks)
    assert "".join(chunks) == text
