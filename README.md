# crypto-tracker

> Live crypto dashboard tracking the top 10 coins by market cap. Flask backend, vanilla JS frontend, CoinGecko data, zero build step.

![status](https://img.shields.io/badge/status-live-16c784)
![python](https://img.shields.io/badge/python-3.9%2B-3776ab)
![license](https://img.shields.io/badge/license-MIT-f0b90b)

A full-stack side project that fetches live prices, 24h change, market cap, and a 7-day sparkline for each of the top 10 coins, then renders them in a clean dark dashboard that auto-refreshes every 30 seconds.

## ✨ What it does

- 📊 Live prices for **BTC, ETH, SOL, BNB, XRP, ADA, DOGE, TRX, AVAX, LINK**
- 📈 Inline SVG sparklines — no chart library, no npm, no build step
- 🔄 Auto-refresh every 30s with a visible "updated" timestamp
- 💾 Server-side caching respects CoinGecko rate limits
- 🧪 Pytest suite covers the API client and Flask routes (no network in tests)

## 🚀 Run it locally

Requires Python 3.9+.

```bash
git clone https://github.com/Izu-Cmd/crypto-tracker.git
cd crypto-tracker
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000**.

## 🧪 Run the tests

```bash
pytest tests/ -v
```

Tests mock the network — no real CoinGecko calls.

## 🌐 Deploy for free

The app is a plain Flask server. One-click options:

### Render

1. Push this repo to GitHub (already done ✅)
2. Go to [render.com](https://render.com) → **New Web Service**
4. Connect this repo
5. Settings:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `python app.py`
6. Hit deploy. Done. Free tier is fine for a portfolio demo.

### Railway

Even faster:

1. Go to [railway.app](https://railway.app)
2. **New Project → Deploy from GitHub**
4. Select this repo
5. Railway auto-detects Python and runs `python app.py`

### Fly.io

If you want edge deployment:

```bash
# install flyctl, then:
fly launch
fly deploy
```

## 🗂 Project layout

```
crypto-tracker/
├── app.py                      # Flask entry, routes, error handling
├── tracker/
│   ├── __init__.py
│   ├── coingecko.py            # API client with in-memory caching
│   └── coins.py                # Top-10 coin config
├── templates/
│   └── index.html              # Dashboard template
├── static/
│   ├── style.css               # Dark, minimal styling
│   └── app.js                  # Fetch loop + sparklines (vanilla JS)
├── tests/
│   ├── test_coingecko.py
│   └── test_app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE                     # MIT
└── README.md
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and edit:

| Variable             | Default                              | Purpose                          |
|----------------------|--------------------------------------|----------------------------------|
| `PORT`               | `5000`                               | HTTP port                        |
| `CACHE_SECONDS`      | `30`                                 | How long to cache CoinGecko data |
| `HTTP_TIMEOUT`       | `10`                                 | CoinGecko request timeout        |
| `COINGECKO_BASE_URL` | `https://api.coingecko.com/api/v3`   | Override for Pro tier proxies     |
| `FLASK_DEBUG`        | unset                                | Set to `1` for hot reload        |

## 🧱 Architecture notes

- **Why Flask?** Zero ceremony. One file, one process, one command to run.
- **Why stdlib `urllib` in the backend?** No third-party packages for HTTP — keeps the dependency tree tiny.
- **Why no chart library?** 50 lines of inline SVG drawing = sharper result, zero `node_modules`.
- **Why cache server-side?** CoinGecko free tier has tight rate limits. Server cache means N tabs = 1 API call per 30s.

## 📸 What it looks like

Once you run it, you'll see a dark dashboard with:

- A table of coins ranked by market cap
- Price column (auto-formatted for sub-$1 coins)
- 24h change column (green if up, red if down)
- Market cap column (formatted as $X.XXB / $X.XXT)
- Sparkline column showing 7-day price action

## 📄 License

MIT — see [LICENSE](./LICENSE).

## 👤 Author

Built by [Izu](https://github.com/Izu-Cmd) as part of a portfolio sprint.