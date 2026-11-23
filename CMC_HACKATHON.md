# Axiogram × CoinMarketCap API

**CMC API Hackathon, Round 2 · Track: Markets and Trading Tools**

Live: **https://axiogram.eu** · Code: this repository · Language of the app: Greek (with an English toggle)

## What Axiogram is

Axiogram is a free web app (installable as a PWA) for retail investors in Greece. It puts the Athens Stock Exchange,
the 500 largest US stocks, crypto and Hyperliquid perpetuals in one place, with a portfolio tracker, price alerts
(push + email), a stock screener, a dividend calendar and a weekly email summary.

Most Greek investors hold a mix of Athens stocks, US stocks and some crypto. Until now Axiogram's crypto side was
limited to the top 100 coins, fetched live from each visitor's browser, which often hit rate limits.

## What the CoinMarketCap API made possible (new for this hackathon)

| Feature | Before | With the CMC API |
|---|---|---|
| Crypto market list | Top 100 | **Top 500**, ranked, with 1h / 24h / 7d change, market cap, volume |
| Loading | Each visitor called a free API from the browser (rate limited) | One server job calls CMC; every visitor reads one cached document, so the list opens instantly |
| Portfolio | Prices for held coins fetched per visitor | Every coin in the top 500 is priced from the CMC snapshot, no extra calls |
| Global stats | Separate sources | Total market cap, 24h volume, BTC / ETH dominance from **CMC global metrics** |
| Fear & Greed | Third-party index | **CMC Fear & Greed** with today / yesterday / 1 week / 1 month |
| 7-day sparklines | — | Built from our own CMC snapshots (one point every 4 h, kept for 7 days) |
| Price alerts | Crypto prices from another source | The alert job reads the CMC snapshot first |
| Search | Remote search | Instant local search over the 500 coins (symbol or name) |

If the CMC data is missing or older than 3 hours, the site falls back automatically to the previous source,
so users never see an empty page.

## How it works

```
GitHub Actions (every 15 min, each run stays ~14 min)
  └─ scripts/fetch_cmc.py
       ├─ GET /v1/key/info                          → plan limits, picks a safe refresh interval
       ├─ GET /v1/cryptocurrency/listings/latest    → top 500 in EUR (every 1–10 min)
       ├─ GET /v1/global-metrics/quotes/latest      → market cap, volume, dominance (hourly)
       └─ GET /v3/fear-and-greed/historical         → last 31 days (hourly)
            │
            ├─ Firestore  site/crypto   (one public, read-only document, ~50 KB)
            └─ repo       cspark.json   (7-day sparklines, every 4 h)

Browser (axiogram.eu)
  └─ reads site/crypto once a minute while the crypto view is open
```

The API key lives only in a GitHub Actions secret (`CMC_API_KEY`). It never reaches the browser or the repository.

### Credit budget

`/v1/cryptocurrency/listings/latest` with `limit=500` costs 2 credits. `fetch_cmc.py` reads the monthly limit from
`/v1/key/info` and refreshes as often as ~65% of it allows:

| Plan | Credits / month | Refresh | Used / month |
|---|---|---|---|
| Basic (free) | 15,000 | every ~10 min | ~10,000 |
| Startup (hackathon) | 450,000 | every 1 min | ~90,000 |

When fewer than 8% of the month's credits are left, it slows down to every 30 minutes.

## CMC API endpoints used

- `GET /v1/cryptocurrency/listings/latest?start=1&limit=500&convert=EUR&sort=market_cap`
- `GET /v1/global-metrics/quotes/latest?convert=EUR`
- `GET /v3/fear-and-greed/historical?limit=31` (fallback: `/v3/fear-and-greed/latest`)
- `GET /v1/key/info`
- Coin logos: `https://s2.coinmarketcap.com/static/img/coins/64x64/{id}.png`

## Evidence of a real API call

Code: [`scripts/fetch_cmc.py`](scripts/fetch_cmc.py) · Workflow: [`.github/workflows/update-crypto.yml`](.github/workflows/update-crypto.yml)
· Sample responses: [`docs/cmc-sample.md`](docs/cmc-sample.md)

## Where the API fell short

- No sparkline / short price history in the listings response, so we keep our own 7-day history from snapshots.
- A browser-only static site cannot hold a secret key; we needed a small server job (GitHub Actions) and a cache
  (Firestore) in between.
- Logos are available as image URLs by coin id, but the id → logo mapping is not part of the listings response.
- `error_code` is a number in v1 responses and a string in v3 responses.

## Files

| File | Role |
|---|---|
| `scripts/fetch_cmc.py` | Calls the CMC API, writes the Firestore document and `cspark.json` |
| `.github/workflows/update-crypto.yml` | Runs it every 15 minutes |
| `src/body.html` (search `CoinMarketCap API`) | Site: loading, the 500-coin list, global stats, Fear & Greed, fallback |
| `scripts/notify.py` | Price alerts: crypto prices from the CMC snapshot |
