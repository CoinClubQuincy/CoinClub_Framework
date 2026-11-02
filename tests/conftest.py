"""Shared test helpers."""

from __future__ import annotations

from decimal import Decimal
from typing import ClassVar

from coinclub.chains.base import Chain, NetworkConfig
from coinclub.models import CONFIRMED, Asset, Balance, Payment, Receipt, Wallet


class FakeChain(Chain):
    """An in-memory chain, for testing code that sits above the chain adapters."""

    name = "fake"
    native = Asset("FAKE")
    default_network = "testnet"
    networks: ClassVar = {
        "testnet": NetworkConfig("https://fake.invalid"),
        "mainnet": NetworkConfig("https://fake.invalid", mainnet=True),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payments: list[Payment] = []
        self.offers: list[dict] = []
        self.fail_after: int | None = None

    def create_wallet(self):
        return Wallet(self.name, "addr", "secret")

    def wallet_from_secret(self, secret):
        return Wallet(self.name, "addr", secret)

    def is_valid_address(self, address):
        return address.startswith("addr")

    def balances(self, address):
        return [Balance(self.native, Decimal("5"))]

    def transfer(self, wallet, to, amount, *, asset=None, reference=None, wait=True):
        self._require_write()
        return Receipt(self.name, self.network, "tx", CONFIRMED)

    def transaction(self, tx_id):
        return Receipt(self.name, self.network, tx_id, CONFIRMED)

    def incoming_payments(self, address, *, limit=100):
        return list(self.payments)[:limit]

    def place_offer(self, wallet, *, selling, buying, amount, price):
        self._require_write()
        if self.fail_after is not None and len(self.offers) >= self.fail_after:
            raise RuntimeError("offer rejected")
        self.offers.append({"amount": amount, "price": price})
        return Receipt(self.name, self.network, f"offer{len(self.offers)}", CONFIRMED)
