from decimal import Decimal

import pytest
from conftest import FakeChain

from coinclub import Asset, MainnetNotAllowedError, ValidationError
from coinclub.liquidity import bottom, from_range, mean, place_ladder, stable, top, total_quantity


def prices(plan):
    return [rung.price for rung in plan]


def test_bottom_matches_the_original_algorithm():
    assert prices(bottom("1", "0.25", 2, "5")) == [Decimal("1"), Decimal("1.25"), Decimal("1.50")]


def test_top_builds_downward():
    assert prices(top("1", "0.25", 2, "5")) == [Decimal("1"), Decimal("0.75"), Decimal("0.50")]


def test_mean_is_symmetric_with_one_centre_rung():
    assert prices(mean("1", "0.015", 1, "5")) == [Decimal("0.985"), Decimal("1"), Decimal("1.015")]


def test_stable_width_is_a_fraction_of_the_peg():
    assert prices(stable("2", "0.01", 1, "5")) == [Decimal("1.98"), Decimal("2"), Decimal("2.02")]


def test_range_includes_both_ends():
    assert prices(from_range("1", "2", 2, "5")) == [Decimal("1"), Decimal("1.5"), Decimal("2")]


def test_ladder_reaching_zero_is_rejected():
    with pytest.raises(ValidationError, match="zero"):
        top("1", "0.5", 2, "5")
    with pytest.raises(ValidationError, match="zero"):
        mean("1", "1", 1, "5")


@pytest.mark.parametrize("rungs", [0, -1, 1.5, True])
def test_bad_rung_counts_are_rejected(rungs):
    with pytest.raises(ValidationError):
        bottom("1", "1", rungs, "5")


@pytest.mark.parametrize("bad", [0.5, "0", "-1"])
def test_bad_prices_and_quantities_are_rejected(bad):
    with pytest.raises(ValidationError):
        bottom(bad, "1", 1, "5")
    with pytest.raises(ValidationError):
        bottom("1", "1", 1, bad)


def test_inverted_range_is_rejected():
    with pytest.raises(ValidationError):
        from_range("2", "1", 2, "5")


def test_total_quantity():
    assert total_quantity(bottom("1", "1", 2, "5")) == 15


def test_place_ladder_places_every_rung():
    chain = FakeChain()
    plan = bottom("1", "1", 1, "5")
    wallet = chain.create_wallet()
    receipts = place_ladder(chain, wallet, plan, selling=Asset("A"), buying=Asset("B"))
    assert len(receipts) == 2
    assert [offer["price"] for offer in chain.offers] == prices(plan)


def test_place_ladder_stops_at_the_first_failure():
    chain = FakeChain()
    chain.fail_after = 1
    with pytest.raises(RuntimeError):
        place_ladder(chain, chain.create_wallet(), bottom("1", "1", 3, "5"),
                     selling=Asset("A"), buying=Asset("B"))
    assert len(chain.offers) == 1


def test_place_ladder_respects_the_mainnet_guard():
    chain = FakeChain("mainnet")
    with pytest.raises(MainnetNotAllowedError):
        place_ladder(chain, chain.create_wallet(), bottom("1", "1", 1, "5"),
                     selling=Asset("A"), buying=Asset("B"))
