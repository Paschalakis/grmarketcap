"""Οι 100 μεγαλύτερες μετοχές ΗΠΑ (TradingView scanner) -> us.json. Κάθε ώρα."""
import json
from datetime import datetime, timezone
import requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36",
     "Origin": "https://www.tradingview.com", "Referer": "https://www.tradingview.com/", "Content-Type": "application/json"}
COLS = ["name", "description", "close", "change", "Perf.W", "market_cap_basic", "volume", "logoid", "sector", "exchange", "currency"]
body = {"columns": COLS, "range": [0, 130], "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
        "filter": [{"left": "type", "operation": "equal", "right": "stock"},
                   {"left": "is_primary", "operation": "equal", "right": True},
                   {"left": "exchange", "operation": "in_range", "right": ["NASDAQ", "NYSE"]}]}
r = requests.post("https://scanner.tradingview.com/america/scan", headers=H, data=json.dumps(body), timeout=40)
print("status", r.status_code, len(r.text))
rows, seen = [], set()
for d in r.json().get("data", []):
    v = dict(zip(COLS, d.get("d") or []))
    if not v.get("name") or v.get("close") is None or not v.get("market_cap_basic"): continue
    if v.get("currency") not in (None, "USD"): continue
    key = (v.get("description") or "").split(" Class ")[0]
    if key in seen: continue          # π.χ. GOOGL / GOOG
    seen.add(key)
    rows.append({"s": v["name"].replace(".", "-"), "n": v.get("description") or v["name"], "p": round(float(v["close"]), 4),
                 "c": round(float(v.get("change") or 0), 3), "w": None if v.get("Perf.W") is None else round(float(v["Perf.W"]), 3),
                 "m": int(v["market_cap_basic"]), "v": int(v.get("volume") or 0), "l": v.get("logoid") or None,
                 "x": v.get("exchange") or "", "sec": v.get("sector") or ""})
    if len(rows) >= 100: break
print("rows", len(rows), [x["s"] for x in rows[:12]])
if len(rows) >= 80:
    try: old = json.load(open("us.json", encoding="utf-8")).get("s")
    except Exception: old = None
    if old != rows:
        with open("us.json", "w", encoding="utf-8") as f:
            json.dump({"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "s": rows}, f, ensure_ascii=False, separators=(",", ":"))
        print("γράφτηκε us.json")
