"""Read-only market data from centralized exchanges. This module never places orders."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import requests

from .errors import NetworkError, NotFoundError

TIMEOUT_SECONDS = 20


@dataclass(frozen=True)
class Ticker:
    symbol: str
    last: Decimal
    bid: Decimal
    ask: Decimal
    open: Decimal
    high: Decimal
    low: Decimal
    change_percent: Decimal
    volume: Decimal
    quote_volume: Decimal

    @classmethod
    def from_binance_style(cls, row: dict[str, Any]) -> Ticker:
        return cls(
            symbol=row["symbol"],
            last=Decimal(str(row["lastPrice"])),
            bid=Decimal(str(row["bidPrice"])),
            ask=Decimal(str(row["askPrice"])),
            open=Decimal(str(row["openPrice"])),
            high=Decimal(str(row["highPrice"])),
            low=Decimal(str(row["lowPrice"])),
            change_percent=Decimal(str(row["priceChangePercent"])),
            volume=Decimal(str(row["volume"])),
            quote_volume=Decimal(str(row["quoteVolume"])),
        )


class BitrueClient:
    """Bitrue's public 24-hour ticker."""

    def __init__(self, url: str = "https://www.bitrue.com"):
        self.url = url.rstrip("/")

    def tickers(self) -> list[Ticker]:
        try:
            response = requests.get(f"{self.url}/api/v1/ticker/24hr", timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
            rows = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise NetworkError(f"Bitrue ticker failed: {exc}") from exc
        return [Ticker.from_binance_style(row) for row in rows]

    def ticker(self, symbol: str) -> Ticker:
        wanted = symbol.upper()
        for item in self.tickers():
            if item.symbol.upper() == wanted:
                return item
        raise NotFoundError(f"Bitrue has no market {symbol}")
