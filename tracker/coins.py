"""
tracker/coins.py
Top coins tracked by the dashboard. CoinGecko IDs are used (not symbols)
because IDs are unambiguous, e.g. 'bitcoin', 'ethereum'.

Order = display order in the UI. Change freely; the API call derives IDs.
"""

from __future__ import annotations

# (symbol, coingecko_id, display_name)  -- keep symbols lowercase
TOP_COINS: list[tuple[str, str, str]] = [
    ("btc",  "bitcoin",        "Bitcoin"),
    ("eth",  "ethereum",       "Ethereum"),
    ("sol",  "solana",         "Solana"),
    ("bnb",  "binancecoin",    "BNB"),
    ("xrp",  "ripple",         "XRP"),
    ("ada",  "cardano",        "Cardano"),
    ("doge", "dogecoin",       "Dogecoin"),
    ("trx",  "tron",           "TRON"),
    ("avax", "avalanche-2",    "Avalanche"),
    ("link", "chainlink",      "Chainlink"),
]


def coin_ids() -> list[str]:
    return [cid for _, cid, _ in TOP_COINS]