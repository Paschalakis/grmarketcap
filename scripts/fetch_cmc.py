"""Τα 500 μεγαλύτερα crypto από το CoinMarketCap API -> Firestore (site/crypto) και cspark.json.

Τρέχει στο GitHub Actions κάθε 15 λεπτά και μένει ανοιχτό ~14 λεπτά, ανανεώνοντας τις τιμές
όσο συχνά επιτρέπει το πρόγραμμα του κλειδιού (υπολογίζεται αυτόματα από το /v1/key/info):
  - δωρεάν Basic (15.000 μονάδες/μήνα): περίπου κάθε 10 λεπτά
  - Startup (450.000 μονάδες/μήνα): κάθε λεπτό
Το site διαβάζει το έγγραφο site/crypto του Firestore (δημόσιο για ανάγνωση).

CoinMarketCap endpoints:
  GET /v1/cryptocurrency/listings/latest?limit=500&convert=EUR   (2 μονάδες)
  GET /v1/global-metrics/quotes/latest?convert=EUR               (1 μονάδα, ανά ώρα)
  GET /v3/fear-and-greed/historical?limit=31                     (1 μονάδα, ανά ώρα)
  GET /v1/key/info                                               (χωρίς χρέωση)
Χωρίς κλειδί χρησιμοποιεί τη δοκιμαστική διαδρομή /public-api (μόνο για δοκιμές).
"""
import json, math, os, sys, time
from datetime import datetime, timezone
import requests

KEY = os.environ.get("CMC_API_KEY", "").strip()
BASE = "https://pro-api.coinmarketcap.com" + ("" if KEY else "/public-api")
H = {"Accept": "application/json", "User-Agent": "axiogram.eu"}
if KEY:
    H["X-CMC_PRO_API_KEY"] = KEY
RUN_MIN = float(os.environ.get("CMC_RUN_MIN", "13.5"))   # πόσο μένει ανοιχτό κάθε εκτέλεση
SPARK_STEP = 4 * 3600                                     # σημείο μίνι διαγράμματος ανά 4 ώρες
SPARK_N = 42                                              # 7 ημέρες
LIMIT = 500
credits_used = 0


def api(path, **params):
    global credits_used
    for attempt in range(3):
        try:
            r = requests.get(BASE + path, params=params, headers=H, timeout=30)
            j = r.json()
            st = j.get("status") or {}
            credits_used += st.get("credit_count") or 0
            if r.status_code == 200 and str(st.get("error_code") or 0) == "0":
                return j.get("data")
            print("CMC", path, r.status_code, st.get("error_code"), st.get("error_message"))
            if r.status_code in (401, 402, 403):
                return None
        except Exception as e:
            print("CMC", path, "σφάλμα", e)
        time.sleep(5 * (attempt + 1))
    return None


def sig(v, n=6):
    """Στρογγυλοποίηση σε n σημαντικά ψηφία (μικρότερο αρχείο)."""
    if v is None: return None
    try: v = float(v)
    except Exception: return None
    if v == 0 or not math.isfinite(v): return 0
    return round(v, max(0, n - 1 - int(math.floor(math.log10(abs(v))))))


def r2(v):
    return None if v is None else round(float(v), 2)


def interval_sec():
    """Συχνότητα ανανέωσης ώστε να ξοδεύεται το πολύ ~65% των μηνιαίων μονάδων του κλειδιού."""
    if not KEY:
        return 300
    info = api("/v1/key/info") or {}
    plan = info.get("plan") or {}
    monthly = plan.get("credit_limit_monthly") or 15000
    usage = (info.get("usage") or {}).get("current_month") or {}
    print("Πρόγραμμα:", monthly, "μονάδες/μήνα · χρησιμοποιήθηκαν", usage.get("credits_used"), "· απομένουν", usage.get("credits_left"))
    per_month = monthly * 0.65 - 2 * 24 * 30          # μείον τα ωριαία (παγκόσμια + fear & greed)
    cycles = max(1, per_month / 2)                      # 2 μονάδες κάθε λήψη των 500
    sec = 30 * 24 * 3600 / cycles
    left = usage.get("credits_left")
    if left is not None and left < monthly * 0.08:      # λίγες μονάδες έμειναν: πιο αραιά
        sec = max(sec, 1800)
    return int(min(max(sec, 60), 1800))


def coins():
    d = api("/v1/cryptocurrency/listings/latest", start=1, limit=LIMIT, convert="EUR", sort="market_cap")
    if not d:
        return None
    out = []
    for c in d:
        q = (c.get("quote") or {}).get("EUR") or {}
        if q.get("price") is None:
            continue
        out.append([c["id"], c.get("slug"), c.get("symbol"), c.get("name"), c.get("cmc_rank"), sig(q.get("price")),
                    r2(q.get("percent_change_1h")), r2(q.get("percent_change_24h")), r2(q.get("percent_change_7d")),
                    int(q["market_cap"]) if q.get("market_cap") else None, int(q["volume_24h"]) if q.get("volume_24h") else None,
                    int(c["circulating_supply"]) if c.get("circulating_supply") else None])
    return out


def glob():
    g = api("/v1/global-metrics/quotes/latest", convert="EUR")
    if not g:
        return None
    q = (g.get("quote") or {}).get("EUR") or {}
    return {"mc": int(q.get("total_market_cap") or 0), "vol": int(q.get("total_volume_24h") or 0),
            "mcch": r2(q.get("total_market_cap_yesterday_percentage_change")), "btc": r2(g.get("btc_dominance")),
            "eth": r2(g.get("eth_dominance")), "n": g.get("active_cryptocurrencies")}


def fng():
    d = api("/v3/fear-and-greed/historical", limit=31)
    if not d:
        d1 = api("/v3/fear-and-greed/latest")
        d = [d1] if d1 else None
    if not d:
        return None
    return [{"v": int(x.get("value")), "c": x.get("value_classification"), "t": x.get("timestamp") or x.get("update_time")} for x in d if x.get("value") is not None]


def spark_load():
    try:
        with open("cspark.json", encoding="utf-8") as f:
            s = json.load(f)
        if s.get("step") == SPARK_STEP:
            return s
    except Exception:
        pass
    return {"step": SPARK_STEP, "t": 0, "d": {}}


def spark_update(s, cs):
    """Ένα σημείο ανά 4 ώρες για κάθε νόμισμα. Για νέο νόμισμα, αρχική εκτίμηση από τις μεταβολές 7ημ/24ω/1ω."""
    now = int(time.time()); bucket = now - now % SPARK_STEP
    if s["t"] >= bucket:
        return False
    d = s["d"]; keep = {}
    for c in cs:
        slug, p, h1, h24, d7 = c[1], c[5], c[6], c[7], c[8]
        arr = d.get(slug)
        if not arr:
            arr = []
            if d7 is not None and h24 is not None:   # πρόχειρη αρχή, μέχρι να μαζευτεί ιστορικό
                p7, p1 = p / (1 + d7 / 100), p / (1 + h24 / 100)
                for i in range(SPARK_N - 6):
                    arr.append(sig(p7 + (p1 - p7) * i / (SPARK_N - 6), 5))
                for i in range(6):
                    arr.append(sig(p1 + (p - p1) * i / 6, 5))
        arr = (arr + [sig(p, 5)])[-SPARK_N:]
        keep[slug] = arr
    s["d"] = keep; s["t"] = bucket
    return True


def firestore():
    raw = os.environ.get("FIREBASE_SA")
    if not raw:
        return None
    import firebase_admin
    from firebase_admin import credentials, firestore as fs
    firebase_admin.initialize_app(credentials.Certificate(json.loads(raw)))
    return fs.client()


def main():
    if not KEY and not os.environ.get("CMC_ALLOW_KEYLESS"):
        print("Δεν υπάρχει CMC_API_KEY: το site χρησιμοποιεί εφεδρικά το CoinGecko. Πρόσθεσε το secret για να ενεργοποιηθεί.")
        return
    db = firestore()
    every = interval_sec()
    print("Ανανέωση κάθε", every, "δευτ.", "(με κλειδί)" if KEY else "(χωρίς κλειδί: δοκιμαστικά)")
    end = time.time() + RUN_MIN * 60
    G = F = None; gAt = 0; spark = spark_load(); spark_changed = False; n = 0
    while True:
        t0 = time.time()
        cs = coins()
        if cs:
            if not G or t0 - gAt > 3600:
                G = glob() or G; F = fng() or F; gAt = t0
            doc = {"src": "CoinMarketCap", "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "every": every, "cols": ["id", "slug", "sym", "name", "rank", "p", "h1", "h24", "d7", "mc", "vol", "circ"],
                   "c": cs, "g": G, "fng": F}
            body = json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
            if db:
                db.collection("site").document("crypto").set({"c": body, "at": int(t0 * 1000)})
            with open("crypto.json", "w", encoding="utf-8") as f:
                f.write(body)
            spark_changed = spark_update(spark, cs) or spark_changed
            n += 1
            print(datetime.now(timezone.utc).strftime("%H:%M:%S"), "→", len(cs), "νομίσματα,", round(len(body) / 1024), "KB · BTC", cs[0][5], "€ · μονάδες", credits_used)
        if time.time() + every > end:
            break
        time.sleep(max(5, every - (time.time() - t0)))
    if spark_changed:
        with open("cspark.json", "w", encoding="utf-8") as f:
            json.dump(spark, f, separators=(",", ":"))
        print("cspark.json ενημερώθηκε")
    print("Λήψεις:", n, "· μονάδες:", credits_used)
    if not n:
        sys.exit(1)


if __name__ == "__main__":
    main()
