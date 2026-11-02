"""Plan and place ladders of DEX offers around a price.

The planning functions are pure and touch no network. place_ladder places a plan through any chain
with a DEX, one offer at a time, and stops at the first failure.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .chains.base import Chain
from .errors import ValidationError
from .models import Asset, Receipt, Wallet, to_decimal, to_positive

Number = Decimal | str | int


@dataclass(frozen=True)
class Rung:
    price: Decimal
    quantity: Decimal


def _check_rungs(rungs: int) -> None:
    if isinstance(rungs, bool) or not isinstance(rungs, int) or rungs < 1:
        raise ValidationError("rungs must be a positive whole number")


def _build(prices: list[Decimal], quantity: Number) -> list[Rung]:
    size = to_positive(quantity, name="quantity")
    if any(price <= 0 for price in prices):
        raise ValidationError("the ladder reaches zero or below: use a smaller step or fewer rungs")
    return [Rung(price, size) for price in prices]


def bottom(price: Number, step: Number, rungs: int, quantity: Number) -> list[Rung]:
    """Treat price as the floor and build upward: price, price + step, and so on."""
    _check_rungs(rungs)
    start, gap = to_positive(price, name="price"), to_positive(step, name="step")
    return _build([start + gap * i for i in range(rungs + 1)], quantity)


def top(price: Number, step: Number, rungs: int, quantity: Number) -> list[Rung]:
    """Treat price as the ceiling and build downward: price, price - step, and so on."""
    _check_rungs(rungs)
    start, gap = to_positive(price, name="price"), to_positive(step, name="step")
    return _build([start - gap * i for i in range(rungs + 1)], quantity)


def mean(price: Number, step: Number, rungs: int, quantity: Number) -> list[Rung]:
    """Centre on price with rungs on each side, lowest price first."""
    _check_rungs(rungs)
    start, gap = to_positive(price, name="price"), to_positive(step, name="step")
    return _build([start + gap * i for i in range(-rungs, rungs + 1)], quantity)


def stable(peg: Number, width: Number, rungs: int, quantity: Number) -> list[Rung]:
    """Centre on a stable asset's peg. width is the fraction per rung: 0.001 narrow, 0.01 wide."""
    centre = to_positive(peg, name="peg")
    return mean(centre, centre * to_positive(width, name="width"), rungs, quantity)


def from_range(low: Number, high: Number, rungs: int, quantity: Number) -> list[Rung]:
    """Space rungs evenly across a traded range, such as a ticker's day, week or month low and high.

    rungs counts the gaps, so the result has rungs + 1 prices, including low and high.
    """
    _check_rungs(rungs)
    floor, ceiling = to_positive(low, name="low"), to_positive(high, name="high")
    if ceiling <= floor:
        raise ValidationError("high must be greater than low")
    gap = (ceiling - floor) / rungs
    return _build([floor + gap * i for i in range(rungs + 1)], quantity)


def total_quantity(plan: list[Rung]) -> Decimal:
    return sum((rung.quantity for rung in plan), to_decimal(0))


def place_ladder(
    chain: Chain, wallet: Wallet, plan: list[Rung], *, selling: Asset, buying: Asset
) -> list[Receipt]:
    """Place each rung as a sell offer. Offers already placed stay open if a later one fails."""
    return [
        chain.place_offer(
            wallet, selling=selling, buying=buying, amount=rung.quantity, price=rung.price
        )
        for rung in plan
    ]
