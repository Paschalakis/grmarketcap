"""Στοιχεία για το φίλτρο μετοχών και το ημερολόγιο (TradingView scanner) -> screener.json.

Ελλάδα: όλες οι μετοχές του data.json που βρίσκονται στο TradingView.
ΗΠΑ: οι 500 μεγαλύτερες μετοχές NASDAQ/NYSE και όσες ξένες παρακολουθούμε.

Κάθε γραμμή είναι πίνακας με τη σειρά του COLS_OUT, ώστε το αρχείο να μένει μικρό.
"""
import json, re
from datetime import datetime, timezone
import requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36",
     "Origin": "https://www.tradingview.com", "Referer": "https://www.tradingview.com/", "Content-Type": "application/json"}
TV = ["name", "description", "close", "change", "market_cap_basic", "sector", "industry", "price_earnings_ttm", "price_book_fq",
      "dividends_yield_current", "return_on_equity", "Perf.W", "Perf.Y", "Perf.YTD", "beta_1_year", "RSI", "Recommend.All",
      "net_margin", "total_revenue_yoy_growth_ttm", "debt_to_equity", "earnings_release_next_date", "ex_dividend_date_upcoming",
      "dividend_payment_date_upcoming", "dps_common_stock_prim_issue_fy", "dividends_per_share_fq", "logoid", "currency", "type", "is_primary"]
COLS_OUT = ["k", "n", "p", "c", "m", "sec", "ind", "pe", "pb", "dy", "roe", "w", "y", "ytd", "beta", "rsi", "rec",
            "nm", "rg", "de", "earn", "exd", "pay", "dps", "logo"]


def load(p, d):
    try:
        with open(p, encoding="utf-8") as f: return json.load(f)
    except Exception: return d


def scan(market, body):
    r = requests.post("https://scanner.tradingview.com/%s/scan" % market, headers=H, data=json.dumps(body), timeout=60)
    print(market, r.status_code, len(r.text))
    r.raise_for_status()
    return [dict(zip(TV, d.get("d") or [])) for d in r.json().get("data", [])]


def rnd(v, n=3):
    if v is None: return None
    try:
        v = float(v)
    except Exception: return None
    if v != v: return None
    return round(v, n)


def day(ts):
    if not ts: return None
    try: return datetime.fromtimestamp(int(ts), timezone.utc).strftime("%Y-%m-%d")
    except Exception: return None


def row(key, v):
    dps = v.get("dividends_per_share_fq") or v.get("dps_common_stock_prim_issue_fy")
    return [key, v.get("description") or v.get("name"), rnd(v.get("close"), 4), rnd(v.get("change"), 2),
            int(v["market_cap_basic"]) if v.get("market_cap_basic") else None, v.get("sector") or "", v.get("industry") or "",
            rnd(v.get("price_earnings_ttm"), 2), rnd(v.get("price_book_fq"), 2), rnd(v.get("dividends_yield_current"), 2),
            rnd(v.get("return_on_equity"), 1), rnd(v.get("Perf.W"), 2), rnd(v.get("Perf.Y"), 1), rnd(v.get("Perf.YTD"), 1),
            rnd(v.get("beta_1_year"), 2), rnd(v.get("RSI"), 1), rnd(v.get("Recommend.All"), 2), rnd(v.get("net_margin"), 1),
            rnd(v.get("total_revenue_yoy_growth_ttm"), 1), rnd(v.get("debt_to_equity"), 2), day(v.get("earnings_release_next_date")),
            day(v.get("ex_dividend_date_upcoming")), day(v.get("dividend_payment_date_upcoming")), rnd(dps, 4), v.get("logoid") or None]


# Ελλάδα
sym_en = load("scripts/symbols_en.json", {})
stocks = load("data.json", {}).get("stocks", [])
code2sym = {}
for s in stocks:
    sym = s["sym"]
    code = sym_en.get(sym) or (sym if re.fullmatch(r"[A-Z0-9]+", sym) else None)
    if code: code2sym[code.upper()] = sym
gr = []
for v in scan("greece", {"columns": TV, "range": [0, 2000], "filter": [], "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"}}):
    sym = code2sym.get((v.get("name") or "").upper())
    if sym and v.get("close") is not None: gr.append(row(sym, v))
print("Ελλάδα:", len(gr))

# ΗΠΑ
us, seen = [], set()
flt = [{"left": "type", "operation": "equal", "right": "stock"}, {"left": "is_primary", "operation": "equal", "right": True},
       {"left": "exchange", "operation": "in_range", "right": ["NASDAQ", "NYSE"]}]
for v in scan("america", {"columns": TV, "range": [0, 560], "filter": flt, "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"}}):
    if not v.get("name") or v.get("close") is None or v.get("currency") not in (None, "USD"): continue
    key = (v.get("description") or "").split(" Class ")[0]
    if key in seen: continue
    seen.add(key)
    us.append(row(v["name"].replace(".", "-"), v))
    if len(us) >= 500: break
have = {r[0] for r in us}
extra = [t for t in list((load("foreign.json", {}).get("q") or {}).keys()) + load("scripts/foreign_tracked.json", [])
         if re.fullmatch(r"[A-Z0-9\-]+", t) and t not in have]
if extra:
    for v in scan("america", {"columns": TV, "range": [0, 200], "filter": [{"left": "name", "operation": "in_range", "right": sorted({t.replace("-", ".") for t in extra})}],
                              "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"}}):
        k = (v.get("name") or "").replace(".", "-")
        if k in have or v.get("close") is None: continue
        have.add(k); us.append(row(k, v))
print("ΗΠΑ:", len(us))

if len(gr) >= 50 and len(us) >= 300:
    out = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "cols": COLS_OUT, "gr": gr, "us": us}
    with open("screener.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print("γράφτηκε screener.json")
else:
    raise SystemExit("λίγες γραμμές, δεν γράφτηκε")
