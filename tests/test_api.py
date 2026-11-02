import json

import pytest
from conftest import FakeChain

from coinclub import NetworkError, NotFoundError
from coinclub.api import make_handler


def event(path, key="good", method="GET"):
    headers = {"X-Api-Key": key} if key else {}
    return {
        "rawPath": path,
        "headers": headers,
        "requestContext": {"http": {"method": method}},
    }


@pytest.fixture
def handler():
    return make_handler(lambda key: key == "good", lambda chain, network: FakeChain(network))


def test_missing_and_bad_keys_are_refused(handler):
    assert handler(event("/v1/chains", key=None))["statusCode"] == 401
    assert handler(event("/v1/chains", key="bad"))["statusCode"] == 401


def test_chains(handler):
    response = handler(event("/v1/chains"))
    assert response["statusCode"] == 200
    assert "xrpl" in json.loads(response["body"])["chains"]


def test_balances_are_strings_so_no_precision_is_lost(handler):
    body = json.loads(handler(event("/v1/fake/testnet/balances/addr"))["body"])
    assert body["balances"] == [{"code": "FAKE", "issuer": None, "amount": "5"}]


def test_transaction(handler):
    body = json.loads(handler(event("/v1/fake/testnet/transactions/T1"))["body"])
    assert body["status"] == "confirmed"
    assert body["tx_id"] == "T1"


@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE"])
def test_writes_are_refused(handler, method):
    assert handler(event("/v1/chains", method=method))["statusCode"] == 405


@pytest.mark.parametrize("path", ["/", "/v1", "/v2/chains", "/v1/a/b/nope/c", "/v1/a/b/c"])
def test_unknown_routes_are_404(handler, path):
    assert handler(event(path))["statusCode"] == 404


def raising(exc):
    def connector(chain, network):
        raise exc

    return make_handler(lambda key: True, connector)


def test_upstream_details_are_not_exposed():
    response = raising(NetworkError("http://internal-node:5005 refused"))(
        event("/v1/a/b/balances/c")
    )
    assert response["statusCode"] == 502
    assert "internal-node" not in response["body"]


def test_not_found_maps_to_404():
    assert raising(NotFoundError("x"))(event("/v1/a/b/balances/c"))["statusCode"] == 404


def test_real_connector_rejects_unknown_chain_with_400():
    handler = make_handler(lambda key: True)
    response = handler(event("/v1/dogecoin/mainnet/balances/x"))
    assert response["statusCode"] == 400
