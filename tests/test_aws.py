from decimal import Decimal

import boto3
import pytest
from conftest import FakeChain
from moto import mock_aws

from coinclub import Asset, NetworkError
from coinclub.aws import (
    DynamoApiKeys,
    DynamoInvoiceStore,
    wallet_from_secrets_manager,
    wallet_from_ssm,
)
from coinclub.gateway import PAID, PaymentGateway


@pytest.fixture
def aws(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    with mock_aws():
        yield


@pytest.fixture
def table(aws):
    return boto3.resource("dynamodb").create_table(
        TableName="t",
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


def test_wallet_from_secrets_manager(aws):
    boto3.client("secretsmanager").create_secret(Name="w", SecretString="the-secret")
    assert wallet_from_secrets_manager(FakeChain(), "w").secret == "the-secret"


def test_missing_secret_raises_without_quoting_values(aws):
    with pytest.raises(NetworkError, match="could not read"):
        wallet_from_secrets_manager(FakeChain(), "missing")


def test_wallet_from_ssm(aws):
    boto3.client("ssm").put_parameter(Name="/w", Value="the-secret", Type="SecureString")
    assert wallet_from_ssm(FakeChain(), "/w").secret == "the-secret"


def test_missing_parameter_raises(aws):
    with pytest.raises(NetworkError):
        wallet_from_ssm(FakeChain(), "/missing")


def test_invoice_round_trip_keeps_exact_values(table):
    store = DynamoInvoiceStore(table)
    gateway = PaymentGateway(FakeChain(), "addr", store)
    invoice = gateway.create_invoice("1.10", asset=Asset("USD", "issuer"))
    loaded = store.get(invoice.id)
    assert loaded == invoice
    assert loaded.amount == Decimal("1.10")


def test_paid_invoice_persists(table):
    from coinclub import Payment

    chain = FakeChain()
    store = DynamoInvoiceStore(table)
    gateway = PaymentGateway(chain, "addr", store)
    invoice = gateway.create_invoice("1")
    chain.payments.append(
        Payment("T", "s", "addr", chain.native, Decimal(1), invoice.reference, invoice.created_at)
    )
    gateway.check(invoice.id)
    loaded = store.get(invoice.id)
    assert loaded.status == PAID
    assert loaded.tx_id == "T"
    assert loaded.paid_amount == 1


def test_missing_invoice_is_none(table):
    assert DynamoInvoiceStore(table).get("nope") is None


def test_reference_lookup(table):
    store = DynamoInvoiceStore(table)
    invoice = PaymentGateway(FakeChain(), "addr", store).create_invoice("1")
    assert store.reference_in_use("fake", "testnet", "addr", invoice.reference)
    assert not store.reference_in_use("fake", "testnet", "addr", "nope")


def test_api_keys_authorize_count_and_revoke(table):
    keys = DynamoApiKeys(table)
    key = keys.create_key("customer-1")
    assert keys.usage(key) == 0
    assert keys.authorize(key)
    assert keys.authorize(key)
    assert keys.usage(key) == 2
    keys.revoke_key(key)
    assert not keys.authorize(key)
    assert keys.usage(key) == 2


def test_unknown_key_is_refused_and_not_counted(table):
    keys = DynamoApiKeys(table)
    assert not keys.authorize("made-up")
    assert keys.usage("made-up") == 0


def test_plaintext_key_is_never_stored(table):
    key = DynamoApiKeys(table).create_key("c")
    assert key not in str(table.scan()["Items"])
