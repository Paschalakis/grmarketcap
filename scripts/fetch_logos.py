"""Λογότυπα μετοχών από το TradingView (μία φορά την εβδομάδα).

Γράφει το logos.json: {σύμβολο: logoid}. Η σελίδα φορτώνει την εικόνα από
https://s3-symbol-logo.tradingview.com/<logoid>.svg και, αν δεν υπάρχει,
δείχνει τα αρχικά της μετοχής.
"""
import json, re
import requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36",
     "Origin": "https://www.tradingview.com", "Referer": "https://www.tradingview.com/", "Content-Type": "application/json"}

def load(p, d):
    try:
        with open(p, encoding="utf-8") as f: return json.load(f)
    except Exception: return d

sym_en = load("scripts/symbols_en.json", {})
stocks = load("data.json", {}).get("stocks", [])
out = {}

def scan(market, body):
    r = requests.post("https://scanner.tradingview.com/%s/scan" % market, headers=H, data=json.dumps(body), timeout=40)
    print(market, r.status_code, len(r.text))
    return r.json().get("data", []) if r.ok else []

# Ελλάδα
rows = scan("greece", {"columns": ["name", "logoid"], "range": [0, 2000], "filter": [], "sort": {"sortBy": "name", "sortOrder": "asc"}})
tv = {}
for d in rows:
    name, logo = (d.get("d") or [None, None])[:2]
    if name and logo: tv[name.upper()] = logo
print("TradingView Ελλάδα με λογότυπο:", len(tv))
for s in stocks:
    sym = s["sym"]
    code = sym_en.get(sym) or (sym if re.fullmatch(r"[A-Z0-9]+", sym) else None)
    if code and code.upper() in tv: out[sym] = tv[code.upper()]

# Ξένες μετοχές που παρακολουθούμε
foreign = list((load("foreign.json", {}).get("q") or {}).keys())
us = [t for t in foreign if re.fullmatch(r"[A-Z0-9\-]+", t)]
if us:
    rows = scan("america", {"columns": ["name", "logoid"], "range": [0, 500],
                            "filter": [{"left": "name", "operation": "in_range", "right": [t.replace("-", ".") for t in us]}]})
    for d in rows:
        name, logo = (d.get("d") or [None, None])[:2]
        if name and logo: out["f:" + name.replace(".", "-").upper()] = logo
old = load("logos.json", {})
if len(out) >= 20 and out != old:
    with open("logos.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print("λογότυπα:", len(out), "π.χ.", {k: out[k] for k in list(out)[:5]}, "RDW:", out.get("f:RDW"), "ΠΕΙΡ:", out.get("ΠΕΙΡ"))
