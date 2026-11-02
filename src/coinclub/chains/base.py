"""The interface every chain adapter implements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar

from ..errors import (
    MainnetNotAllowedError,
    UnsupportedOperationError,
    ValidationError,
)
from ..models import Asset, Balance, BookOffer, Payment, Receipt, Wallet


@dataclass(frozen=True)
class NetworkConfig:
    url: str
    mainnet: bool = False


class Chain(ABC):
    """One network of one blockchain.

    Reads work on any network. Writes on a mainnet raise MainnetNotAllowedError unless the chain
    was connected with allow_mainnet=True, so a misconfigured script cannot spend real funds.
    """

    name: ClassVar[str]
    native: ClassVar[Asset]
    networks: ClassVar[Mapping[str, NetworkConfig]]
    default_network: ClassVar[str]

    def __init__(
        self, network: str | None = None, *, url: str | None = None, allow_mainnet: bool = False
    ):
        self.network = network or self.default_network
        if self.network not in self.networks:
            choices = ", ".join(sorted(self.networks))
            raise ValidationError(f"{self.name} has no network {self.network!r}: use {choices}")
        self.config = self.networks[self.network]
        self.url = url or self.config.url
        self.allow_mainnet = allow_mainnet

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name}:{self.network}>"

    @property
    def is_mainnet(self) -> bool:
        return self.config.mainnet

    def _require_write(self) -> None:
        if self.is_mainnet and not self.allow_mainnet:
            raise MainnetNotAllowedError(
                f"{self.name}:{self.network} is a mainnet. Pass allow_mainnet=True to spend real "
                "funds."
            )

    def _require_wallet(self, wallet: Wallet) -> None:
        if wallet.chain != self.name:
            raise ValidationError(f"this wallet is for {wallet.chain}, not {self.name}")

    def _require_address(self, address: str) -> None:
        if not self.is_valid_address(address):
            raise ValidationError(f"not a valid {self.name} address: {address!r}")

    def _unsupported(self, operation: str) -> UnsupportedOperationError:
        return UnsupportedOperationError(f"{self.name} does not support {operation}")

    @abstractmethod
    def create_wallet(self) -> Wallet:
        """Generate a key locally. Nothing is sent to the network."""

    @abstractmethod
    def wallet_from_secret(self, secret: str) -> Wallet:
        """Rebuild a wallet from its secret."""

    @abstractmethod
    def is_valid_address(self, address: str) -> bool:
        """Check an address's format and checksum, without using the network."""

    @abstractmethod
    def balances(self, address: str) -> list[Balance]:
        """Return the native balance followed by any token balances."""

    def balance(self, address: str, asset: Asset | None = None) -> Decimal:
        wanted = asset or self.native
        for item in self.balances(address):
            if item.asset == wanted:
                return item.amount
        return Decimal(0)

    @abstractmethod
    def transfer(
        self,
        wallet: Wallet,
        to: str,
        amount: Decimal | str | int,
        *,
        asset: Asset | None = None,
        reference: str | None = None,
        wait: bool = True,
    ) -> Receipt:
        """Send funds. Raises TransactionFailedError if the network rejects it.

        reference is carried with the payment: a destination tag or memo on XRPL, a memo on
        Stellar, a note on Algorand, transaction data on EVM chains, CIP-20 metadata on Cardano.
        """

    @abstractmethod
    def transaction(self, tx_id: str) -> Receipt:
        """Look up a transaction. Raises NotFoundError if the network does not know it."""

    def incoming_payments(self, address: str, *, limit: int = 100) -> list[Payment]:
        """Return recent final payments received by address, newest first."""
        raise self._unsupported("listing incoming payments")

    def request_test_funds(self, wallet: Wallet) -> None:
        """Ask a test network's faucet to fund a wallet."""
        raise self._unsupported("faucet funding")

    def add_trustline(
        self, wallet: Wallet, asset: Asset, limit: Decimal | str | int | None = None
    ) -> Receipt:
        """Allow a wallet to hold an issued asset."""
        raise self._unsupported("trust lines")

    def order_book(self, base: Asset, quote: Asset, *, limit: int = 20) -> list[BookOffer]:
        """Return offers selling base for quote, best price first."""
        raise self._unsupported("order books")

    def place_offer(
        self,
        wallet: Wallet,
        *,
        selling: Asset,
        buying: Asset,
        amount: Decimal | str | int,
        price: Decimal | str | int,
    ) -> Receipt:
        """Offer to sell amount of selling at price units of buying per unit."""
        raise self._unsupported("DEX offers")

    def cancel_offer(
        self,
        wallet: Wallet,
        offer_id: int,
        *,
        selling: Asset | None = None,
        buying: Asset | None = None,
    ) -> Receipt:
        """Cancel an open offer. Stellar also needs the offer's selling and buying assets."""
        raise self._unsupported("DEX offers")
