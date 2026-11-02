from decimal import Decimal

import pytest
import responses

from coinclub import NetworkError, NotFoundError, UnsupportedOperationError, Wallet, connect

URL = "https://jungle4.greymass.com"


@responses.activate
def test_balance_parses_the_asset_string():
    responses.post(f"{URL}/v1/chain/get_currency_balance", json=["12.3400 EOS"])
    assert connect("eos").balances("someaccount1")[0].amount == Decimal("12.34")


@responses.activate
def test_empty_balance_is_zero():
    responses.post(f"{URL}/v1/chain/get_currency_balance", json=[])
    assert connect("eos").balances("someaccount1")[0].amount == 0


@responses.activate
def test_unknown_account_raises_not_found():
    responses.post(
        f"{URL}/v1/chain/get_account",
        status=500,
        json={"error": {"name": "account_query_exception", "what": "missing"}},
    )
    with pytest.raises(NotFoundError):
        connect("eos").account("someaccount1")


@responses.activate
def test_server_failure_raises_network_error():
    responses.post(f"{URL}/v1/chain/get_info", status=503)
    with pytest.raises(NetworkError):
        connect("eos").info()


@pytest.mark.parametrize("good", ["eosio", "a1b2c3d4e5", "eosio.token"])
def test_valid_account_names(good):
    assert connect("eos").is_valid_address(good)


@pytest.mark.parametrize("bad", ["UPPER", "has6", "toolongaccountname", "", "ends."])
def test_invalid_account_names(bad):
    assert not connect("eos").is_valid_address(bad)


def test_writes_are_explicitly_unsupported():
    chain = connect("eos")
    with pytest.raises(UnsupportedOperationError, match="read-only"):
        chain.transfer(Wallet("eos", "a", "b"), "eosio", "1")
    with pytest.raises(UnsupportedOperationError):
        chain.create_wallet()
    with pytest.raises(UnsupportedOperationError):
        chain.wallet_from_secret("x")
