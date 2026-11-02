from decimal import Decimal

import pytest
from conftest import FakeChain

import coinclub
from coinclub import (
    Asset,
    MainnetNotAllowedError,
    UnsupportedOperationError,
    ValidationError,
    Wallet,
    connect,
)
from coinclub.models import to_decimal, to_positive
from coinclub.registry import chain_class


@pytest.mark.parametrize("bad", [1.5, True, None, [], "abc", "NaN", "Infinity"])
def test_to_decimal_rejects_anything_inexact_or_not_a_number(bad):
    with pytest.raises(ValidationError):
        to_decimal(bad)


@pytest.mark.parametrize("good", ["1.5", 1, Decimal("1.5")])
def test_to_decimal_accepts_exact_values(good):
    assert to_decimal(good) == Decimal(good)


@pytest.mark.parametrize("bad", ["0", "-1", 0])
def test_to_positive_rejects_zero_and_negative(bad):
    with pytest.raises(ValidationError):
        to_positive(bad)


def test_wallet_secret_stays_out_of_repr_and_str():
    wallet = Wallet("xrpl", "rAddress", "very-secret-seed")
    assert "very-secret-seed" not in repr(wallet)
    assert "very-secret-seed" not in str(wallet)
    assert "rAddress" in repr(wallet)


def test_mainnet_write_is_blocked_by_default():
    chain = FakeChain("mainnet")
    with pytest.raises(MainnetNotAllowedError):
        chain.transfer(chain.create_wallet(), "addr2", "1")


def test_mainnet_write_works_when_explicitly_allowed():
    chain = FakeChain("mainnet", allow_mainnet=True)
    assert chain.transfer(chain.create_wallet(), "addr2", "1").confirmed


def test_test_network_write_needs_no_permission():
    chain = FakeChain("testnet")
    assert chain.transfer(chain.create_wallet(), "addr2", "1").confirmed


def test_wallet_from_another_chain_is_refused():
    with pytest.raises(ValidationError):
        FakeChain()._require_wallet(Wallet("xrpl", "r", "s"))


def test_unknown_network_is_refused():
    with pytest.raises(ValidationError, match="no network"):
        FakeChain("nope")


def test_unsupported_operations_raise_a_clear_error():
    chain = FakeChain()
    with pytest.raises(UnsupportedOperationError):
        chain.order_book(Asset("A"), Asset("B"))
    with pytest.raises(UnsupportedOperationError):
        chain.cancel_offer(chain.create_wallet(), 1)
    with pytest.raises(UnsupportedOperationError):
        chain.add_trustline(chain.create_wallet(), Asset("A", "i"))
    with pytest.raises(UnsupportedOperationError):
        chain.request_test_funds(chain.create_wallet())


def test_balance_of_an_asset_not_held_is_zero():
    assert FakeChain().balance("addr", Asset("OTHER", "issuer")) == 0


def test_unknown_chain_is_refused():
    with pytest.raises(ValidationError, match="unknown chain"):
        connect("dogecoin")


@pytest.mark.parametrize(
    ("alias", "name"),
    [("xrp", "xrpl"), ("XLM", "stellar"), ("fil", "filecoin"), ("flr", "flare"),
     ("algo", "algorand"), ("ada", "cardano"), ("eth", "ethereum")],
)
def test_ticker_aliases_resolve(alias, name):
    assert chain_class(alias).name == name


@pytest.mark.parametrize("name", coinclub.available_chains())
def test_every_chain_defaults_to_a_test_network(name):
    cls = chain_class(name)
    assert not cls.networks[cls.default_network].mainnet


@pytest.mark.parametrize("name", coinclub.available_chains())
def test_every_chain_has_exactly_one_default_and_a_mainnet(name):
    cls = chain_class(name)
    assert cls.default_network in cls.networks
    assert any(config.mainnet for config in cls.networks.values())
