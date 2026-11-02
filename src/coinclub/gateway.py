"""Accept crypto payments: create an invoice, share its address and reference, then check it.

The gateway is non-custodial. It only reads the chain, and funds go straight to your address. Each
invoice gets a random numeric reference, carried as a destination tag on XRPL, a memo on Stellar
and a note on Algorand. Those are the chains that can list incoming payments.
"""

from __future__ import annotations

import secrets
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Protocol

from .chains.base import Chain
from .errors import NotFoundError
from .models import Asset, Payment, to_positive

OPEN = "open"
PAID = "paid"
EXPIRED = "expired"
MAX_REFERENCE = 2**32
SCAN_LIMIT = 200


@dataclass(frozen=True)
class Invoice:
    id: str
    chain: str
    network: str
    address: str
    asset: Asset
    amount: Decimal
    reference: str
    created_at: float
    expires_at: float
    status: str = OPEN
    tx_id: str | None = None
    paid_amount: Decimal | None = None


class InvoiceStore(Protocol):
    def save(self, invoice: Invoice) -> None: ...

    def get(self, invoice_id: str) -> Invoice | None: ...

    def reference_in_use(self, chain: str, network: str, address: str, reference: str) -> bool: ...


class MemoryInvoiceStore:
    """Keeps invoices in this process only. Use coinclub.aws.DynamoInvoiceStore in production."""

    def __init__(self) -> None:
        self._invoices: dict[str, Invoice] = {}

    def save(self, invoice: Invoice) -> None:
        self._invoices[invoice.id] = invoice

    def get(self, invoice_id: str) -> Invoice | None:
        return self._invoices.get(invoice_id)

    def reference_in_use(self, chain: str, network: str, address: str, reference: str) -> bool:
        return any(
            (i.chain, i.network, i.address, i.reference) == (chain, network, address, reference)
            for i in self._invoices.values()
        )


class PaymentGateway:
    def __init__(
        self,
        chain: Chain,
        address: str,
        store: InvoiceStore | None = None,
        *,
        clock: Callable[[], float] = time.time,
        scan_limit: int = SCAN_LIMIT,
    ):
        chain._require_address(address)
        self.chain = chain
        self.address = address
        self.store = store if store is not None else MemoryInvoiceStore()
        self.clock = clock
        self.scan_limit = scan_limit

    def create_invoice(
        self,
        amount: Decimal | str | int,
        *,
        asset: Asset | None = None,
        ttl_seconds: int = 3600,
    ) -> Invoice:
        now = self.clock()
        invoice = Invoice(
            id=str(uuid.uuid4()),
            chain=self.chain.name,
            network=self.chain.network,
            address=self.address,
            asset=asset or self.chain.native,
            amount=to_positive(amount),
            reference=self._new_reference(),
            created_at=now,
            expires_at=now + ttl_seconds,
        )
        self.store.save(invoice)
        return invoice

    def _new_reference(self) -> str:
        while True:
            reference = str(secrets.randbelow(MAX_REFERENCE))
            if not self.store.reference_in_use(
                self.chain.name, self.chain.network, self.address, reference
            ):
                return reference

    def check(self, invoice_id: str) -> Invoice:
        """Update an invoice from the chain and return it. Paid invoices stay paid."""
        invoice = self.store.get(invoice_id)
        if invoice is None:
            raise NotFoundError(f"no invoice {invoice_id}")
        if invoice.status != OPEN:
            return invoice
        for payment in self.chain.incoming_payments(self.address, limit=self.scan_limit):
            if self._settles(invoice, payment):
                updated = replace(
                    invoice, status=PAID, tx_id=payment.tx_id, paid_amount=payment.amount
                )
                self.store.save(updated)
                return updated
        if self.clock() > invoice.expires_at:
            updated = replace(invoice, status=EXPIRED)
            self.store.save(updated)
            return updated
        return invoice

    @staticmethod
    def _settles(invoice: Invoice, payment: Payment) -> bool:
        if payment.reference != invoice.reference or payment.destination != invoice.address:
            return False
        if payment.asset != invoice.asset or payment.amount < invoice.amount:
            return False
        if payment.timestamp is None:
            return False
        return invoice.created_at - 60 <= payment.timestamp <= invoice.expires_at
