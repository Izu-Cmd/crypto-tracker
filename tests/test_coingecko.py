"""
tests/test_coingecko.py
Unit tests for the CoinGeckoClient. The network is mocked so tests run
deterministically and don't depend on rate-limited upstream calls.
"""

import json
from unittest.mock import patch

import pytest

from tracker.coingecko import CoinGeckoClient, CoinGeckoError
from tracker.coins import TOP_COINS


SAMPLE_MARKETS = [
    {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "image": "https://example.com/btc.png",
        "current_price": 67000.42,
        "price_change_percentage_24h": 1.23,
        "market_cap": 1_300_000_000_000,
        "sparkline_in_7d": {"price": [66000, 66500, 67000, 67000.42]},
    },
    {
        "id": "ethereum",
        "symbol": "eth",
        "name": "Ethereum",
        "image": "https://example.com/eth.png",
        "current_price": 3500.10,
        "price_change_percentage_24h": -0.55,
        "market_cap": 420_000_000_000,
        "sparkline_in_7d": {"price": [3520, 3510, 3505, 3500.10]},
    },
]


def _fake_urlopen(payload):
    """Return a context manager whose .read() yields JSON bytes."""
    from contextlib import contextmanager
    body = json.dumps(payload).encode("utf-8")

    @contextmanager
    def _ctx(*args, **kwargs):
        class _Resp:
            def read(self_inner):
                return body
        yield _Resp()

    return _ctx


def test_top_market_returns_cached_payload():
    client = CoinGeckoClient(cache_seconds=60)
    with patch("urllib.request.urlopen", _fake_urlopen(SAMPLE_MARKETS)):
        result = client.top_market(TOP_COINS)

    assert isinstance(result, list)
    assert len(result) == 2
    btc = result[0]
    assert btc["symbol"] == "BTC"
    assert btc["id"] == "bitcoin"
    assert btc["name"] == "Bitcoin"
    assert btc["price"] == 67000.42
    assert btc["change_24h"] == 1.23
    assert isinstance(btc["sparkline"], list)
    assert btc["sparkline"][-1] == 67000.42


def test_cache_is_used_on_second_call():
    client = CoinGeckoClient(cache_seconds=60)

    with patch("urllib.request.urlopen", _fake_urlopen(SAMPLE_MARKETS)) as m:
        client.top_market(TOP_COINS)
        client.top_market(TOP_COINS)  # should hit cache, no second call
        assert m.call_count == 1


def test_http_error_raises_coin_gecko_error():
    client = CoinGeckoClient(cache_seconds=0)
    from urllib.error import HTTPError

    def _raise(*args, **kwargs):
        raise HTTPError(url="x", msg="rate limited", hdrs={}, fp=None, code=429)

    with patch("urllib.request.urlopen", side_effect=_raise):
        with pytest.raises(CoinGeckoError):
            client.top_market(TOP_COINS)


def test_invalid_json_raises_coin_gecko_error():
    client = CoinGeckoClient(cache_seconds=0)

    from contextlib import contextmanager

    @contextmanager
    def _ctx(*args, **kwargs):
        class _Resp:
            def read(self_inner):
                return b"not json{"
        yield _Resp()

    with patch("urllib.request.urlopen", _ctx):
        with pytest.raises(CoinGeckoError):
            client.top_market(TOP_COINS)


def test_clear_cache_forces_refetch():
    client = CoinGeckoClient(cache_seconds=60)

    with patch("urllib.request.urlopen", _fake_urlopen(SAMPLE_MARKETS)) as m:
        client.top_market(TOP_COINS)
        client.clear_cache()
        client.top_market(TOP_COINS)
        assert m.call_count == 2


def test_unknown_coin_id_falls_back_to_titlecase():
    """If we pass coins not in TOP_COINS, name should still come back."""
    client = CoinGeckoClient(cache_seconds=60)
    with patch("urllib.request.urlopen", _fake_urlopen(SAMPLE_MARKETS)):
        result = client.top_market([("foo", "bitcoin", "Foo")])
    # name argument overrides upstream name because of our map.
    assert result[0]["name"] == "Foo"