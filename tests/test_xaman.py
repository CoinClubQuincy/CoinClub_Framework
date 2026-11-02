import json

import pytest
import responses

from coinclub import NetworkError, NotFoundError, ValidationError
from coinclub.xaman import BASE_URL, XamanClient


@pytest.fixture
def client():
    return XamanClient("the-key", "the-secret")


def test_credentials_are_required():
    with pytest.raises(ValidationError):
        XamanClient("", "secret")


def test_secret_stays_out_of_repr(client):
    assert "the-secret" not in repr(client)


@responses.activate
def test_requests_are_authenticated(client):
    responses.get(f"{BASE_URL}/ping", json={"pong": True})
    client.ping()
    headers = responses.calls[0].request.headers
    assert headers["X-API-Key"] == "the-key"
    assert headers["X-API-Secret"] == "the-secret"


@responses.activate
def test_create_payload_sends_transaction_and_options(client):
    responses.post(f"{BASE_URL}/payload", json={"uuid": "u1"})
    tx = {"TransactionType": "SignIn"}
    result = client.create_payload(tx, expire_minutes=5, custom_id="order-7", instruction="Sign")
    body = json.loads(responses.calls[0].request.body)
    assert result["uuid"] == "u1"
    assert body["txjson"] == tx
    assert body["options"] == {"submit": True, "multisign": False, "expire": 5}
    assert body["custom_meta"] == {"identifier": "order-7", "instruction": "Sign"}


@responses.activate
@pytest.mark.parametrize(
    ("call", "method", "path"),
    [
        (lambda c: c.get_payload("u1"), "GET", "payload/u1"),
        (lambda c: c.get_payload_by_custom_id("x"), "GET", "payload/ci/x"),
        (lambda c: c.cancel_payload("u1"), "DELETE", "payload/u1"),
        (lambda c: c.curated_assets(), "GET", "curated-assets"),
        (lambda c: c.kyc_status("rA"), "GET", "kyc-status/rA"),
        (lambda c: c.transaction("H"), "GET", "xrpl-tx/H"),
        (lambda c: c.rates("USD"), "GET", "rates/USD"),
        (lambda c: c.push("t", "b"), "POST", "xapp/push"),
        (lambda c: c.event("t", "b"), "POST", "xapp/event"),
    ],
)
def test_endpoints(client, call, method, path):
    responses.add(method, f"{BASE_URL}/{path}", json={"ok": True})
    assert call(client) == {"ok": True}


@responses.activate
def test_not_found_raises(client):
    responses.get(f"{BASE_URL}/payload/u1", status=404)
    with pytest.raises(NotFoundError):
        client.get_payload("u1")


@responses.activate
def test_server_error_raises_without_exposing_the_secret(client):
    responses.get(f"{BASE_URL}/ping", status=500, body="boom")
    with pytest.raises(NetworkError) as caught:
        client.ping()
    assert "the-secret" not in str(caught.value)
