"""Ξένες μετοχές για το χαρτοφυλάκιο (Yahoo Finance).

- universe.json: λίστα συμβόλων ΗΠΑ (NYSE, Nasdaq κ.λπ.) για την αναζήτηση
  στη φόρμα. Ανανεώνεται μία φορά την εβδομάδα.
- foreign.json: τρέχουσες τιμές (και σε €) μόνο για τα σύμβολα που έχει
  προσθέσει κάποιος σε χαρτοφυλάκιο (Firestore "tracked") και όσα υπάρχουν
  στο scripts/foreign_tracked.json.
- hist/F_<ΣΥΜΒΟΛΟ>.json: ημερήσιο ιστορικό σε €, ανανεώνεται κάθε εβδομάδα.
"""
import json, os, re, time
from datetime import datetime, timezone, date, timedelta
import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
API_KEY = "AIzaSyDd3-HyjHU6Cji1DwPtZ6epuJxFUT6luws"
PROJECT = "agora-athinon"
OK = re.compile(r"^[A-Z0-9][A-Z0-9.\-^=]{0,19}$")

def load(p, d):
    try:
        with open(p, encoding="utf-8") as f: return json.load(f)
    except Exception: return d

def save(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))

s = requests.Session(); s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})

# ---------- 1. λίστα συμβόλων (εβδομαδιαία)
uni = load("universe.json", {})
if not uni.get("s") or uni.get("updated", "") < (date.today() - timedelta(days=7)).isoformat():
    rows = {}
    def clean(n):
        n = re.sub(r"\s*-\s*(Common Stock|Ordinary Shares|Class [A-Z] (Common Stock|Ordinary Shares)|American Depositary Shares.*|Common Shares.*)$", "", n, flags=re.I)
        n = re.sub(r"\s+(Common Stock|Ordinary Shares)$", "", n, flags=re.I)
        return n.strip()[:60]
    try:
        t = s.get("https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt", timeout=40).text
        for line in t.splitlines()[1:]:
            p = line.split("|")
            if len(p) < 8 or p[3] != "N" or not p[0]: continue
            rows[p[0].replace(".", "-")] = [p[0].replace(".", "-"), clean(p[1]), "Nasdaq" + (" · ETF" if p[6] == "Y" else ""), "USD"]
        t = s.get("https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt", timeout=40).text
        EX = {"A": "NYSE American", "N": "NYSE", "P": "NYSE Arca", "Z": "Cboe", "V": "IEX"}
        for line in t.splitlines()[1:]:
            p = line.split("|")
            if len(p) < 8 or p[6] != "N" or not p[0]: continue
            sym = p[0].replace(".", "-").replace("$", "-P")
            rows[sym] = [sym, clean(p[1]), EX.get(p[2], p[2]) + (" · ETF" if p[4] == "Y" else ""), "USD"]
    except Exception as ex:
        print("λίστα συμβόλων:", ex)
    if len(rows) > 3000:
        save("universe.json", {"updated": date.today().isoformat(), "s": sorted(rows.values())})
        print("universe:", len(rows))

# ---------- 2. ποια σύμβολα παρακολουθούμε
tracked = set(t for t in load("scripts/foreign_tracked.json", []) if OK.match(t))
try:
    url = "https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents/tracked" % PROJECT
    tok = None
    for _ in range(10):
        r = s.get(url, params={"pageSize": 300, "key": API_KEY, **({"pageToken": tok} if tok else {})}, timeout=20)
        if r.status_code != 200: print("Firestore:", r.status_code, r.text[:200]); break
        j = r.json()
        for d in j.get("documents", []):
            t = d.get("fields", {}).get("t", {}).get("stringValue", "")
            if OK.match(t): tracked.add(t)
        tok = j.get("nextPageToken")
        if not tok: break
except Exception as ex:
    print("Firestore:", ex)
tracked = sorted(tracked)[:400]
print("παρακολουθούνται:", tracked)

# ---------- 3. τιμές και ισοτιμίες
try: s.get("https://fc.yahoo.com", timeout=15)
except Exception: pass
crumb = s.get("https://query1.finance.yahoo.com/v1/test/getcrumb", timeout=15).text.strip()
def quotes(syms):
    out = {}
    for i in range(0, len(syms), 40):
        r = s.get("https://query1.finance.yahoo.com/v7/finance/quote", params={"symbols": ",".join(syms[i:i + 40]), "crumb": crumb}, timeout=30)
        for q in r.json().get("quoteResponse", {}).get("result", []):
            out[q["symbol"]] = q
        time.sleep(0.4)
    return out

Q = quotes(tracked)
q_out, curs = {}, set()
for t in tracked:
    q = Q.get(t)
    if not q or q.get("regularMarketPrice") is None: continue
    p, cur = float(q["regularMarketPrice"]), q.get("currency") or "USD"
    if cur in ("GBp", "GBX"): p, cur = p / 100, "GBP"
    if cur == "ILA": p, cur = p / 100, "ILS"
    if cur == "ZAc": p, cur = p / 100, "ZAR"
    curs.add(cur)
    q_out[t] = {"p": round(p, 4), "cur": cur, "c": round(q.get("regularMarketChangePercent") or 0, 3),
                "n": q.get("longName") or q.get("shortName") or t, "ex": q.get("fullExchangeName") or q.get("exchange") or ""}
fx = {}
need = sorted(c for c in curs | {"USD", "GBP", "CHF"} if c != "EUR")
FXQ = quotes(["EUR%s=X" % c for c in need])
for c in need:
    v = (FXQ.get("EUR%s=X" % c) or {}).get("regularMarketPrice")
    if v: fx[c] = round(float(v), 6)
for t, q in q_out.items():
    r = 1 if q["cur"] == "EUR" else fx.get(q["cur"])
    q["pe"] = round(q["p"] / r, 4) if r else None
q_out = {t: q for t, q in q_out.items() if q["pe"]}

old = load("foreign.json", {})
if q_out and (old.get("q") != q_out or old.get("fx") != fx):
    save("foreign.json", {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "fx": fx, "q": q_out})
    print("foreign.json:", len(q_out))
else:
    print("καμία αλλαγή στις τιμές")

# ---------- 4. ιστορικό σε € (εβδομαδιαία ανά σύμβολο)
os.makedirs("hist", exist_ok=True)
def daily(sym, start=0):
    r = s.get("https://query1.finance.yahoo.com/v8/finance/chart/" + sym, params={"period1": start, "period2": int(time.time()) + 86400, "interval": "1d"}, timeout=30)
    res = (r.json().get("chart", {}).get("result") or [None])[0]
    if not res or not res.get("timestamp"): return {}
    off = (res.get("meta") or {}).get("gmtoffset") or 0
    out = {}
    for t, v in zip(res["timestamp"], res["indicators"]["quote"][0].get("close") or []):
        if v: out[datetime.fromtimestamp(t + off, timezone.utc).date()] = float(v)
    return out
fxh = {}
for t, q in q_out.items():
    fn = "hist/F_" + re.sub(r"[^A-Z0-9.\-]", "_", t) + ".json"
    prev = load(fn, None)
    if prev and prev.get("u", "") >= (date.today() - timedelta(days=7)).isoformat(): continue
    try:
        px = daily(t)
        if len(px) < 5: continue
        cur, div = q["cur"], 1
        if (Q.get(t) or {}).get("currency") in ("GBp", "GBX", "ILA", "ZAc"): div = 100
        rates = {}
        if cur != "EUR":
            if cur not in fxh: fxh[cur] = daily("EUR%s=X" % cur, int(datetime.combine(min(px), datetime.min.time()).timestamp()))
            rates = fxh[cur]
        days = sorted(px); vals, last = [], fx.get(cur)
        rk = sorted(rates); ri = 0; cur_rate = rates[rk[0]] if rk else last
        for d in days:
            while ri < len(rk) and rk[ri] <= d: cur_rate = rates[rk[ri]]; ri += 1
            r = 1 if cur == "EUR" else (cur_rate or last)
            if not r: break
            v = px[d] / div / r
            vals.append(round(v, 4) if v >= 1 else round(v, 6))
        if len(vals) != len(days): continue
        dd = [(days[i] - days[i - 1]).days for i in range(1, len(days))]
        save(fn, {"s": t, "u": date.today().isoformat(), "d0": days[0].isoformat(), "dd": dd, "c": vals})
        print("ιστορικό", t, len(days))
    except Exception as ex:
        print("ιστορικό", t, ex)
    time.sleep(0.4)
