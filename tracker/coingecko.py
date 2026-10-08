"""
tracker/coingecko.py
Minimal CoinGecko API client with built-in in-memory caching.

Why caching?
    CoinGecko's free tier rate-limits aggressively. The dashboard
    auto-refreshes every 30s in the frontend, so caching responses server
    side for the same period keeps us well within the limit even if many
    tabs are open.

Public methods:
    top_market(coins) -> list[dict]
        Returns the requested coins' price, 24h change, market cap and a
        24h sparkline (list of ~288 price points sampled hourly).
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Iterable


class CoinGeckoError(Exception):
    """Raised when the upstream API fails or returns unexpected data."""


@dataclass
class _CacheEntry:
    data: list[dict]
    expires_at: float


@dataclass
class CoinGeckoClient:
    base_url: str = "https://api.coingecko.com/api/v3"
    cache_seconds: int = 30
    timeout: float = 10.0
    _cache: dict[str, _CacheEntry] = field(default_factory=dict)

    def _get_json(self, path: str, params: dict | None = None) -> dict | list:
        url = f"{self.base_url}{path}"
        if params:
            from urllib.parse import urlencode
            url += "?" + urlencode(params)
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise CoinGeckoError(f"CoinGecko HTTP {e.code}: {e.reason}") from e
        except urllib.error.URLError as e:
            raise CoinGeckoError(f"CoinGecko network error: {e.reason}") from e
        except json.JSONDecodeError as e:
            raise CoinGeckoError(f"CoinGecko returned invalid JSON") from e

    def top_market(self, coins: Iterable[tuple[str, str, str]]) -> list[dict]:
        """Fetch market data for the supplied coin tuples, cached.

        Args:
            coins: iterable of (symbol, coingecko_id, display_name).

        Returns:
            list of dicts shaped for the frontend:
                {symbol, id, name, price, change_24h, market_cap, sparkline}
        """
        coins = list(coins)
        cache_key = ",".join(cid for _, cid, _ in coins)
        now = time.time()

        cached = self._cache.get(cache_key)
        if cached and cached.expires_at > now:
            return cached.data

        ids = ",".join(cid for _, cid, _ in coins)
        params = {
            "vs_currency": "usd",
            "ids": ids,
            "order": "market_cap_desc",
            "per_page": str(len(coins)),
            "page": "1",
            "sparkline": "true",
            "price_change_percentage": "24h",
        }

        raw = self._get_json("/coins/markets", params=params)
        if not isinstance(raw, list):
            raise CoinGeckoError("Unexpected /coins/markets payload shape")

        # Build a name map from input so display names match our config.
        names = {cid: name for _, cid, name in coins}
        symbols = {cid: sym for sym, cid, _ in coins}

        result: list[dict] = []
        for entry in raw:
            cid = entry.get("id", "")
            spark = entry.get("sparkline_in_7d", {}).get("price") or []
            result.append({
                "symbol": symbols.get(cid, entry.get("symbol", "")).upper(),
                "id": cid,
                "name": names.get(cid, entry.get("name", cid.title())),
                "image": entry.get("image"),
                "price": entry.get("current_price"),
                "change_24h": entry.get("price_change_percentage_24h"),
                "market_cap": entry.get("market_cap"),
                "sparkline": spark,
            })

        self._cache[cache_key] = _CacheEntry(data=result, expires_at=now + self.cache_seconds)
        return result

    def clear_cache(self) -> None:
        self._cache.clear()