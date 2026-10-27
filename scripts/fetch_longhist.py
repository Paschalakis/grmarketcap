"""Πλήρες ιστορικό ημερήσιων τιμών κλεισίματος ανά μετοχή (Yahoo Finance).

Γράφει hist/<ΚΩΔΙΚΟΣ>.json με μορφή {"s": "ΣΥΜΒΟΛΟ", "d0": "YYYY-MM-DD",
"dd": [διαφορές ημερών], "c": [τιμές]}. Τρέχει μία φορά τον μήνα· τις
ενδιάμεσες μέρες τις καλύπτει το history.json.
"""
import json, os, re, time
from datetime import datetime, timezone, date
import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

def load(p, d):
    try:
        with open(p, encoding="utf-8") as f: return json.load(f)
    except Exception: return d

stocks = load("data.json", {}).get("stocks", [])
sym_en = load("scripts/symbols_en.json", {})
os.makedirs("hist", exist_ok=True)
s = requests.Session(); s.headers.update({"User-Agent": UA})

def code(sym):
    if sym in sym_en: return sym_en[sym]
    if re.fullmatch(r"[A-Z0-9]+", sym): return sym
    return None

def sig(v):
    if v >= 100: return round(v, 2)
    if v >= 1: return round(v, 4)
    return round(v, 5)

index, ok = {}, 0
for st in stocks:
    c = code(st["sym"])
    if not c: continue
    try:
        r = s.get("https://query1.finance.yahoo.com/v8/finance/chart/" + c + ".AT",
                  params={"period1": 0, "period2": int(time.time()) + 86400, "interval": "1d", "events": "split"}, timeout=30)
        res = (r.json().get("chart", {}).get("result") or [None])[0]
        if not res or not res.get("timestamp"): continue
        ts = res["timestamp"]; cl = res["indicators"]["quote"][0].get("close") or []
        days, vals, last = [], [], None
        for t, v in zip(ts, cl):
            if v is None or v <= 0: continue
            d = datetime.fromtimestamp(t + 3 * 3600, timezone.utc).date()
            if d == last: vals[-1] = sig(v); continue
            days.append(d); vals.append(sig(v)); last = d
        if len(days) < 20: continue
        dd = [(days[i] - days[i - 1]).days for i in range(1, len(days))]
        with open("hist/" + c + ".json", "w", encoding="utf-8") as f:
            json.dump({"s": st["sym"], "d0": days[0].isoformat(), "dd": dd, "c": vals}, f, separators=(",", ":"))
        index[st["sym"]] = [c, days[0].isoformat(), days[-1].isoformat(), len(days)]
        ok += 1
    except Exception as ex:
        print("σφάλμα", st["sym"], c, ex)
    time.sleep(0.3)
with open("hist/index.json", "w", encoding="utf-8") as f:
    json.dump({"updated": date.today().isoformat(), "stocks": index}, f, ensure_ascii=False, separators=(",", ":"))
print("μετοχές με ιστορικό:", ok)
first = sorted(index.items(), key=lambda kv: kv[1][1])[:5]
print("παλαιότερα:", first)
