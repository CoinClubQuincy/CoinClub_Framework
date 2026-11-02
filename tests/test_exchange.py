from decimal import Decimal

import pytest
import responses

from coinclub import NetworkError, NotFoundError
from coinclub.exchange import BitrueClient

URL = "https://www.bitrue.com/api/v1/ticker/24hr"
ROW = {
    "symbol": "XRPUSDT", "lastPrice": "0.5", "bidPrice": "0.49", "askPrice": "0.51",
    "openPrice": "0.45", "highPrice": "0.6", "lowPrice": "0.4", "priceChangePercent": "11.1",
    "volume": "100", "quoteVolume": "50",
}


@responses.activate
def test_ticker_parses_exact_decimals():
    responses.get(URL, json=[ROW])
    ticker = BitrueClient().ticker("xrpusdt")
    assert ticker.last == Decimal("0.5")
    assert ticker.high == Decimal("0.6")


@responses.activate
def test_unknown_market_raises():
    responses.get(URL, json=[ROW])
    with pytest.raises(NotFoundError):
        BitrueClient().ticker("NOPE")


@responses.activate
def test_server_error_raises():
    responses.get(URL, status=500)
    with pytest.raises(NetworkError):
        BitrueClient().tickers()
