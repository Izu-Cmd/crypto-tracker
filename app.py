"""
crypto-tracker / app.py
Flask entry point. Exposes:
    GET /             -> dashboard (templates/index.html)
    GET /api/prices   -> JSON for the top N coins from CoinGecko
    GET /api/health   -> simple liveness probe

Run with:
    python app.py
Then open http://localhost:5000
"""

from __future__ import annotations

import os
import time

from flask import Flask, jsonify, render_template

from tracker.coingecko import CoinGeckoClient, CoinGeckoError
from tracker.coins import TOP_COINS


def create_app() -> Flask:
    app = Flask(__name__)
    client = CoinGeckoClient(
        base_url=os.environ.get("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3"),
        cache_seconds=int(os.environ.get("CACHE_SECONDS", "30")),
        timeout=float(os.environ.get("HTTP_TIMEOUT", "10")),
    )

    @app.route("/")
    def index():
        return render_template("index.html", coins=TOP_COINS)

    @app.route("/api/prices")
    def prices():
        try:
            data = client.top_market(TOP_COINS)
            return jsonify({
                "ok": True,
                "fetched_at": int(time.time()),
                "coins": data,
            })
        except CoinGeckoError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 502
        except Exception as exc:  # pragma: no cover -- last-resort safety net
            return jsonify({"ok": False, "error": f"unexpected: {exc}"}), 500

    @app.route("/api/health")
    def health():
        return jsonify({"ok": True, "service": "crypto-tracker", "version": "0.1.0"})

    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    create_app().run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")