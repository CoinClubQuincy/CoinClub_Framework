"""Chain-neutral data types. Amounts are always Decimal, never float."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

from .errors import ValidationError

PENDING = "pending"
CONFIRMED = "confirmed"
FAILED = "failed"


def to_decimal(value: Decimal | str | int, *, name: str = "amount") -> Decimal:
    """Convert to Decimal, rejecting floats because they cannot represent money exactly."""
    if isinstance(value, bool) or not isinstance(value, (Decimal, str, int)):
        raise ValidationError(f"{name} must be a Decimal, str or int, not {type(value).__name__}")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValidationError(f"{name} is not a number: {value!r}") from exc
    if not result.is_finite():
        raise ValidationError(f"{name} must be finite")
    return result


def to_positive(value: Decimal | str | int, *, name: str = "amount") -> Decimal:
    result = to_decimal(value, name=name)
    if result <= 0:
        raise ValidationError(f"{name} must be greater than zero")
    return result


@dataclass(frozen=True)
class Asset:
    """A native coin (no issuer) or a token.

    issuer means: the issuing account on XRPL and Stellar, the contract address on EVM chains,
    the asset ID on Algorand and the policy ID on Cardano.
    """

    code: str
    issuer: str | None = None

    @property
    def is_native(self) -> bool:
        return self.issuer is None


@dataclass(frozen=True)
class Balance:
    asset: Asset
    amount: Decimal


@dataclass(frozen=True)
class Payment:
    """An incoming payment that has reached finality."""

    tx_id: str
    sender: str
    destination: str
    asset: Asset
    amount: Decimal
    reference: str | None = None
    timestamp: float | None = None


@dataclass(frozen=True)
class BookOffer:
    """An open offer selling `amount` of the base asset at `price` quote units per base unit."""

    price: Decimal
    amount: Decimal


@dataclass(frozen=True)
class Receipt:
    chain: str
    network: str
    tx_id: str
    status: str
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)

    @property
    def confirmed(self) -> bool:
        return self.status == CONFIRMED


@dataclass(frozen=True)
class Wallet:
    """An address and its secret. The secret never appears in repr() or str()."""

    chain: str
    address: str
    secret: str = field(repr=False)
