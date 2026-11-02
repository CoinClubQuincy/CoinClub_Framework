from decimal import Decimal

import pytest
from conftest import FakeChain

from coinclub import Asset, NotFoundError, Payment, ValidationError
from coinclub.gateway import EXPIRED, OPEN, PAID, PaymentGateway


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.fixture
def setup():
    chain, clock = FakeChain(), Clock()
    return chain, PaymentGateway(chain, "addr", clock=clock), clock


def pay(invoice, **overrides):
    fields = dict(
        tx_id="T1", sender="s", destination=invoice.address, asset=invoice.asset,
        amount=invoice.amount, reference=invoice.reference, timestamp=invoice.created_at + 1,
    )
    fields.update(overrides)
    return Payment(**fields)


def test_invoice_starts_open_with_a_numeric_reference(setup):
    _, gateway, _ = setup
    invoice = gateway.create_invoice("5")
    assert invoice.status == OPEN
    assert invoice.reference.isdigit()
    assert int(invoice.reference) < 2**32


def test_invalid_address_is_rejected():
    with pytest.raises(ValidationError):
        PaymentGateway(FakeChain(), "bad")


@pytest.mark.parametrize("amount", ["0", "-1", 1.5])
def test_bad_amounts_are_rejected(setup, amount):
    with pytest.raises(ValidationError):
        setup[1].create_invoice(amount)


def test_exact_payment_settles(setup):
    chain, gateway, _ = setup
    invoice = gateway.create_invoice("5")
    chain.payments.append(pay(invoice))
    checked = gateway.check(invoice.id)
    assert checked.status == PAID
    assert checked.tx_id == "T1"
    assert checked.paid_amount == 5


def test_overpayment_settles(setup):
    chain, gateway, _ = setup
    invoice = gateway.create_invoice("5")
    chain.payments.append(pay(invoice, amount=Decimal("6")))
    assert gateway.check(invoice.id).status == PAID


@pytest.mark.parametrize(
    "overrides",
    [
        {"amount": Decimal("4.999999")},
        {"reference": "other"},
        {"reference": None},
        {"destination": "addr-other"},
        {"asset": Asset("OTHER", "issuer")},
        {"timestamp": None},
        {"timestamp": 100.0},
        {"timestamp": 9_999_999.0},
    ],
    ids=["underpaid", "wrong-reference", "no-reference", "wrong-destination", "wrong-asset",
         "no-timestamp", "before-invoice", "after-expiry"],
)
def test_non_matching_payments_do_not_settle(setup, overrides):
    chain, gateway, _ = setup
    invoice = gateway.create_invoice("5")
    chain.payments.append(pay(invoice, **overrides))
    assert gateway.check(invoice.id).status == OPEN


def test_token_with_same_code_but_other_issuer_does_not_settle(setup):
    chain, gateway, _ = setup
    invoice = gateway.create_invoice("5", asset=Asset("USD", "real-issuer"))
    chain.payments.append(pay(invoice, asset=Asset("USD", "fake-issuer")))
    assert gateway.check(invoice.id).status == OPEN


def test_invoice_expires(setup):
    _, gateway, clock = setup
    invoice = gateway.create_invoice("5", ttl_seconds=60)
    clock.now += 61
    assert gateway.check(invoice.id).status == EXPIRED


def test_payment_made_before_expiry_settles_even_if_checked_later(setup):
    chain, gateway, clock = setup
    invoice = gateway.create_invoice("5", ttl_seconds=60)
    chain.payments.append(pay(invoice))
    clock.now += 600
    assert gateway.check(invoice.id).status == PAID


def test_paid_invoice_stays_paid_without_rescanning(setup):
    chain, gateway, _ = setup
    invoice = gateway.create_invoice("5")
    chain.payments.append(pay(invoice))
    gateway.check(invoice.id)
    chain.payments.clear()
    assert gateway.check(invoice.id).status == PAID


def test_unknown_invoice_raises(setup):
    with pytest.raises(NotFoundError):
        setup[1].check("nope")


def test_references_never_repeat_on_collision(setup, monkeypatch):
    _, gateway, _ = setup
    first = gateway.create_invoice("5")
    values = iter([int(first.reference), int(first.reference), 123])
    monkeypatch.setattr("secrets.randbelow", lambda _limit: next(values))
    assert gateway.create_invoice("5").reference == "123"
