"""Συμπληρωματικά στοιχεία μετοχών, μία-δύο φορές την ημέρα.

- Yahoo Finance: P/E, μέρισμα (απόδοση, ημερομηνία αποκοπής, ιστορικό),
  υψηλό/χαμηλό 52 εβδομάδων, ελεύθερη διασπορά, ημερομηνία αποτελεσμάτων.
- capital.gr: τελευταίες ειδήσεις ανά μετοχή.

Γράφει το extras.json. Αν κάτι αποτύχει κρατάει τα προηγούμενα στοιχεία.
"""
import json, re, sys, time, html
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
OUT = "extras.json"
ATH = timezone(timedelta(hours=2))

def load(p, d):
    try:
        with open(p, encoding="utf-8") as f: return json.load(f)
    except Exception: return d

data = load("data.json", {})
stocks = data.get("stocks", [])
sym_en = load("scripts/symbols_en.json", {})
prev = load(OUT, {}).get("stocks", {})

def ycode(sym):
    if sym in sym_en: return sym_en[sym] + ".AT"
    if re.fullmatch(r"[A-Z0-9]+", sym): return sym + ".AT"
    return None

ymap = {}
for s in stocks:
    c = ycode(s["sym"])
    if c: ymap[c] = s["sym"]

def raw(o, k):
    v = o.get(k)
    if isinstance(v, dict): v = v.get("raw")
    return v

def day(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d") if ts else None

out = {}
# ---------- Yahoo
y = requests.Session(); y.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
try:
    try: y.get("https://fc.yahoo.com", timeout=15)
    except Exception: pass
    crumb = y.get("https://query1.finance.yahoo.com/v1/test/getcrumb", timeout=15).text.strip()
    codes = list(ymap)
    for i in range(0, len(codes), 40):
        r = y.get("https://query1.finance.yahoo.com/v7/finance/quote",
                  params={"symbols": ",".join(codes[i:i + 40]), "crumb": crumb}, timeout=30)
        for q in r.json().get("quoteResponse", {}).get("result", []):
            sym = ymap.get(q.get("symbol"))
            if not sym: continue
            e = out.setdefault(sym, {})
            for k, src in [("pe", "trailingPE"), ("fpe", "forwardPE"), ("pb", "priceToBook"),
                           ("eps", "epsTrailingTwelveMonths"), ("h52", "fiftyTwoWeekHigh"),
                           ("l52", "fiftyTwoWeekLow"), ("sh", "sharesOutstanding"),
                           ("dr", "trailingAnnualDividendRate"), ("ret1y", "fiftyTwoWeekChangePercent")]:
                v = q.get(src)
                if isinstance(v, (int, float)) and v == v: e[k] = round(v, 4)
            if q.get("earningsTimestamp") and q["earningsTimestamp"] > time.time() - 86400:
                e["earn"] = day(q["earningsTimestamp"])
        time.sleep(0.5)
    print("yahoo quotes:", len(out))
    for code, sym in ymap.items():
        if sym not in out: continue
        e = out[sym]
        try:
            r = y.get("https://query2.finance.yahoo.com/v10/finance/quoteSummary/" + code,
                      params={"modules": "summaryDetail,defaultKeyStatistics,calendarEvents", "crumb": crumb}, timeout=25)
            res = (r.json().get("quoteSummary", {}).get("result") or [{}])[0]
            sd, ks, ce = res.get("summaryDetail", {}), res.get("defaultKeyStatistics", {}), res.get("calendarEvents", {})
            if raw(sd, "exDividendDate"): e["exd"] = day(raw(sd, "exDividendDate"))
            if raw(ce, "dividendDate"): e["payd"] = day(raw(ce, "dividendDate"))
            for k, o, src in [("dy", sd, "dividendYield"), ("pay", sd, "payoutRatio"), ("beta", sd, "beta"),
                              ("fl", ks, "floatShares")]:
                v = raw(o, src)
                if isinstance(v, (int, float)): e[k] = round(v, 4)
            if e.get("dr") or e.get("dy") or e.get("exd"):
                r = y.get("https://query1.finance.yahoo.com/v8/finance/chart/" + code,
                          params={"range": "5y", "interval": "1mo", "events": "div"}, timeout=25)
                dv = ((r.json().get("chart", {}).get("result") or [{}])[0].get("events") or {}).get("dividends") or {}
                e["divs"] = sorted([[day(v["date"]), round(v["amount"], 4)] for v in dv.values()], reverse=True)[:12]
        except Exception as ex:
            print("summary", code, ex)
        time.sleep(0.25)
except Exception as ex:
    print("Yahoo απέτυχε:", ex)

# ---------- capital.gr ειδήσεις
c = requests.Session(); c.headers.update({"User-Agent": UA, "Accept-Language": "el-GR,el;q=0.9"})
DT = re.compile(r"(\d{1,2}:\d{2})\s*(?:<[^>]+>\s*)*(\d{1,2}/\d{1,2}(?:/\d{2,4})?)")
def news(sym):
    u = "https://www.capital.gr/finance/news/" + quote(sym.lower()) + "/"
    r = c.get(u, timeout=25)
    if r.status_code != 200: return None
    t = r.text
    i = t.find("finance-news"); t2 = t
    items, seen = [], set()
    for m in re.finditer(r'<a[^>]+href="(/[a-z\-]+/(\d{6,})/[^"]+)"[^>]*>(.*?)</a>', t2, re.S):
        title = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(3)))).strip()
        if len(title) < 15 or m.group(2) in seen: continue
        if m.group(1).startswith(("/forex/", "/finance/")): continue
        seen.add(m.group(2))
        ctx = t2[max(0, m.start() - 600): m.start()]
        dm = list(DT.finditer(ctx))
        when = None
        if dm:
            hm, dd = dm[-1].group(1), dm[-1].group(2)
            p = dd.split("/"); yr = int(p[2]) if len(p) > 2 else datetime.now(ATH).year
            if yr < 100: yr += 2000
            try:
                dt = datetime(yr, int(p[1]), int(p[0]))
                if dt > datetime.now() + timedelta(days=2): dt = dt.replace(year=yr - 1)
                when = dt.strftime("%Y-%m-%d") + " " + hm
            except ValueError: pass
        items.append({"t": title, "u": "https://www.capital.gr" + m.group(1), "d": when})
        if len(items) >= 6: break
    return items

ranked = sorted(stocks, key=lambda s: -(s.get("mcap") or 0))
nn = 0
for s in ranked:
    if not s.get("mcap") and not s.get("vol"): continue
    try:
        n = news(s["sym"])
        if n:
            out.setdefault(s["sym"], {})["news"] = n; nn += 1
    except Exception as ex:
        print("news", s["sym"], ex)
    time.sleep(0.3)
print("news:", nn)

# κρατάμε τα παλιά όπου δεν πήραμε νέα
for sym, e in prev.items():
    n = out.setdefault(sym, {})
    for k, v in e.items():
        n.setdefault(k, v)
if len(out) < 20:
    print("Πολύ λίγα στοιχεία· δεν γράφω."); sys.exit(1)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"updated": datetime.now(ATH).strftime("%Y-%m-%dT%H:%M"), "stocks": out}, f, ensure_ascii=False, separators=(",", ":"))
print("γράφτηκε", OUT, len(out))
