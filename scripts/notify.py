"""Ειδοποιήσεις τιμών και εβδομαδιαία σύνοψη χαρτοφυλακίου (τρέχει στο GitHub Actions).

    python scripts/notify.py alerts   # κάθε ~10 λεπτά: ειδοποιήσεις, δοκιμαστικά, σύνοψη κατ' απαίτηση
    python scripts/notify.py weekly   # Παρασκευή απόγευμα: σύνοψη σε όσους την έχουν ενεργοποιήσει

Μυστικά του αποθετηρίου (Settings → Secrets and variables → Actions):
    FIREBASE_SA   το JSON του λογαριασμού υπηρεσίας του Firebase (για ανάγνωση χρηστών και αποστολή push)
    GMAIL_USER    η διεύθυνση Gmail από την οποία στέλνεται η σύνοψη
    GMAIL_APP_PW  κωδικός εφαρμογής (App password) αυτού του λογαριασμού

Το σενάριο δεν αποτυγχάνει ποτέ (exit 0), ώστε να μη στέλνει το GitHub email αποτυχίας κάθε 10 λεπτά.
"""
import html, json, os, smtplib, sys, time, traceback
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import requests

SITE = "https://axiogram.eu/"
ATH = timezone(timedelta(hours=2))  # αρκεί για ημερομηνίες· η θερινή ώρα δεν επηρεάζει τους ελέγχους
TVH = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36",
       "Origin": "https://www.tradingview.com", "Referer": "https://www.tradingview.com/", "Content-Type": "application/json"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36"}


def load(p, d):
    try:
        with open(p, encoding="utf-8") as f: return json.load(f)
    except Exception: return d


def now_ath(): return datetime.now(timezone.utc).astimezone(ATH)


def fmt_num(v, d=2):
    s = ("{:,.%df}" % d).format(v)
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(v, d=2):
    if v is None: return "—"
    return ("+" if v > 0.004 else "−" if v < -0.004 else "") + fmt_num(abs(v), d) + "%"


def fmt_px(v, cur):
    a = abs(v)
    d = 2 if a >= 100 else 3 if a >= 1 else 6
    s = fmt_num(v, d)
    if "," in s: s = s.rstrip("0").rstrip(",") if d > 2 else s
    return s + " " + {"EUR": "€", "USD": "$"}.get(cur, cur)


# ---------------------------------------------------------------- τιμές
class Prices:
    def __init__(self):
        self.data = load("data.json", {})
        fx = (self.data.get("fx") or {}).get("USD") or (load("foreign.json", {}).get("fx") or {}).get("USD") or 1.1
        self.usd = float(fx)  # 1 € = usd $
        self.gr = {s["sym"]: s for s in self.data.get("stocks", [])}
        self.foreign = load("foreign.json", {}).get("q") or {}
        scr = load("screener.json", {})
        cols = scr.get("cols") or []
        self.scr = {}
        for mk in ("gr", "us"):
            for row in scr.get(mk) or []:
                o = dict(zip(cols, row))
                self.scr[o["k"] if mk == "gr" else "f:" + o["k"]] = o
        self.us, self.cg = {}, {}
        upd = self.data.get("updated") or ""
        self.gr_today = upd[:10] == datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def need(self, keys):
        f = sorted({k[2:] for k in keys if k.startswith("f:")} - set(self.us))
        c = sorted({k[2:] for k in keys if k.startswith("c:")} - set(self.cg))
        if f:
            try:
                cols = ["name", "close", "change", "Perf.W", "currency", "description"]
                body = {"columns": cols, "range": [0, 500], "filter": [{"left": "name", "operation": "in_range", "right": [t.replace("-", ".") for t in f]}],
                        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"}}
                r = requests.post("https://scanner.tradingview.com/america/scan", headers=TVH, data=json.dumps(body), timeout=40)
                for d in r.json().get("data", []):
                    v = dict(zip(cols, d.get("d") or []))
                    k = (v.get("name") or "").replace(".", "-")
                    if k in f and v.get("close") is not None and k not in self.us:
                        self.us[k] = {"p": float(v["close"]), "c": v.get("change"), "w": v.get("Perf.W"), "cur": v.get("currency") or "USD", "n": v.get("description")}
            except Exception as e: print("TradingView:", e)
        if c and getattr(self, "db", None):
            # πρώτα από το CoinMarketCap (site/crypto, γράφεται από το update-crypto.yml)
            try:
                snap = self.db.collection("site").document("crypto").get()
                doc = json.loads((snap.to_dict() or {}).get("c") or "{}") if snap.exists else {}
                upd = doc.get("updated")
                fresh = upd and (datetime.now(timezone.utc) - datetime.fromisoformat(upd.replace("Z", "+00:00"))).total_seconds() < 3 * 3600
                if fresh:
                    want = set(c)
                    for row in doc.get("c") or []:
                        slug = row[1]
                        if slug in want and row[5] is not None:
                            isusd = doc.get("cur") == "USD"; px = float(row[5])
                            self.cg[slug] = {"eur": px / self.usd if isusd else px, "c": row[7], "w": row[8], "s": row[2], "n": row[3], "usd": px if isusd else px * self.usd}
                    c = [x for x in c if x not in self.cg]
                    print("CoinMarketCap:", len(self.cg), "νομίσματα · από CoinGecko:", len(c))
            except Exception as e: print("CoinMarketCap:", e)
        if c:
            try:
                for i in range(0, len(c), 200):
                    part = c[i:i + 200]
                    r = requests.get("https://api.coingecko.com/api/v3/coins/markets", params={"vs_currency": "eur", "ids": ",".join(part), "price_change_percentage": "24h,7d", "per_page": 250}, headers=UA, timeout=40)
                    for x in r.json() if r.ok else []:
                        if x.get("current_price") is None: continue
                        self.cg[x["id"]] = {"eur": float(x["current_price"]), "c": x.get("price_change_percentage_24h_in_currency", x.get("price_change_percentage_24h")),
                                            "w": x.get("price_change_percentage_7d_in_currency"), "s": (x.get("symbol") or "").upper(), "n": x.get("name")}
                    r = requests.get("https://api.coingecko.com/api/v3/simple/price", params={"ids": ",".join(part), "vs_currencies": "usd"}, headers=UA, timeout=30)
                    for k, v in (r.json() if r.ok else {}).items():
                        if k in self.cg and v.get("usd") is not None: self.cg[k]["usd"] = float(v["usd"])
            except Exception as e: print("CoinGecko:", e)

    def get(self, k):
        """{eur, usd, nat, cur, c (ημέρα %), w (εβδομάδα %), live}"""
        if k.startswith("c:"):
            q = self.cg.get(k[2:])
            if not q: return None
            return {"eur": q["eur"], "usd": q.get("usd") or q["eur"] * self.usd, "nat": q.get("usd") or q["eur"] * self.usd, "cur": "USD", "c": q.get("c"), "w": q.get("w"), "live": True}
        if k.startswith("f:"):
            t = k[2:]
            q = self.us.get(t)
            if q and q["cur"] == "USD":
                return {"eur": q["p"] / self.usd, "usd": q["p"], "nat": q["p"], "cur": "USD", "c": q.get("c"), "w": q.get("w"), "live": True}
            f = self.foreign.get(t)
            if f and f.get("pe") is not None:
                return {"eur": f["pe"], "usd": f["pe"] * self.usd, "nat": f.get("p"), "cur": f.get("cur") or "USD", "c": f.get("c"), "w": (self.scr.get(k) or {}).get("w"), "live": True}
            return None
        s = self.gr.get(k)
        if not s or s.get("price") is None: return None
        return {"eur": float(s["price"]), "usd": float(s["price"]) * self.usd, "nat": float(s["price"]), "cur": "EUR", "c": s.get("chg"), "w": (self.scr.get(k) or {}).get("w"), "live": self.gr_today}


# ---------------------------------------------------------------- Firebase
def init_fb():
    raw = (os.environ.get("FIREBASE_SA") or "").strip()
    if not raw:
        print("Δεν έχει οριστεί το μυστικό FIREBASE_SA· οι ειδοποιήσεις δεν είναι ενεργές.")
        return None
    import firebase_admin
    from firebase_admin import credentials, firestore
    firebase_admin.initialize_app(credentials.Certificate(json.loads(raw)))
    return firestore.client()


def send_push(tokens, title, body, tag, url=SITE + "#tools"):
    """Στέλνει σε όλες τις συσκευές. Επιστρέφει τα tokens που δεν ισχύουν πια."""
    from firebase_admin import messaging, exceptions
    bad = []
    for t in tokens:
        try:
            messaging.send(messaging.Message(token=t["t"], data={"title": title, "body": body, "tag": tag, "url": url},
                                             webpush=messaging.WebpushConfig(headers={"Urgency": "high", "TTL": "86400"})))
            print("  push ok", t.get("d"))
        except (messaging.UnregisteredError, messaging.SenderIdMismatchError) as e:
            print("  push: άκυρο token", t.get("d"), type(e).__name__); bad.append(t["t"])
        except exceptions.InvalidArgumentError as e:
            print("  push: άκυρο token", t.get("d"), e); bad.append(t["t"])
        except Exception as e:
            print("  push σφάλμα", t.get("d"), type(e).__name__, e)
    return bad


def us_open(n):
    u = n.astimezone(timezone.utc)
    m = u.hour * 60 + u.minute
    return u.weekday() < 5 and 13 * 60 + 30 <= m <= 21 * 60 + 5


def run_alerts(db):
    P = Prices(); P.db = db
    users = [(d.id, d.to_dict() or {}) for d in db.collection("users").stream()]
    print("χρήστες:", len(users))
    keys = set()
    for _, d in users:
        for a in d.get("alerts") or []:
            if a.get("on"): keys.add(a.get("k") or "")
    P.need(keys)
    n = datetime.now(timezone.utc)
    today = now_ath().strftime("%Y-%m-%d")
    for uid, d in users:
        try:
            upd, tokens = {}, [t for t in (d.get("push") or []) if t.get("t")]
            alerts = d.get("alerts") or []
            # δοκιμαστικές ειδοποιήσεις
            tested = False
            for t in tokens:
                if t.get("test") and t.get("test") != t.get("tested"):
                    print(uid[:6], "δοκιμαστική ειδοποίηση")
                    bad = send_push([t], "Axiogram", "Οι ειδοποιήσεις λειτουργούν σε αυτή τη συσκευή ✓", "test")
                    if bad: t["dead"] = True
                    t["tested"] = t["test"]; tested = True
            if tested:
                upd["push"] = [t for t in tokens if not t.get("dead")]
                tokens = upd["push"]
            # ειδοποιήσεις τιμών
            changed, bad_all = False, set()
            for a in alerts:
                if not a.get("on"): continue
                q = P.get(a.get("k") or "")
                if not q: continue
                hit, body = False, ""
                if a.get("op") == "mv":
                    stock = not str(a.get("k")).startswith("c:")
                    ok_time = (not stock) or (str(a.get("k")).startswith("f:") and us_open(n)) or (not str(a.get("k")).startswith("f:") and q["live"] and now_ath().weekday() < 5)
                    if ok_time and q.get("c") is not None and abs(float(q["c"])) >= float(a.get("v") or 0) and a.get("last") != today:
                        hit = True; a["last"] = today
                        body = "Μεταβολή σήμερα " + fmt_pct(float(q["c"])) + " · τιμή " + fmt_px(q["nat"] if q["cur"] != "EUR" else q["eur"], q["cur"])
                else:
                    cur = a.get("cur") or "EUR"
                    px = q["eur"] if cur == "EUR" else q["usd"] if cur == "USD" else (q["nat"] if q["cur"] == cur else None)
                    if px is None or (not q["live"] and not str(a.get("k")).startswith("c:")): continue
                    v = float(a.get("v") or 0)
                    if (a.get("op") == "gt" and px >= v) or (a.get("op") == "lt" and px <= v):
                        hit = True; a["on"] = False; a["fired"] = int(time.time() * 1000)
                        body = ("Ανέβηκε πάνω από " if a.get("op") == "gt" else "Έπεσε κάτω από ") + fmt_px(v, cur) + " · τώρα " + fmt_px(px, cur)
                if hit:
                    changed = True
                    print(uid[:6], "ειδοποίηση", a.get("lab"), body)
                    if tokens: bad_all.update(send_push(tokens, "🔔 " + str(a.get("lab") or ""), body, "al-" + str(a.get("id")), SITE + "#tools"))
            if changed: upd["alerts"] = alerts
            if bad_all:
                upd["push"] = [t for t in tokens if t["t"] not in bad_all]
            # σύνοψη κατ' απαίτηση («Στείλε μου μία τώρα»)
            if d.get("wtest") and d.get("wtest") != d.get("wsent"):
                try:
                    weekly_for(uid, d, P)
                except Exception: traceback.print_exc()
                upd["wsent"] = d.get("wtest")
            if upd:
                db.collection("users").document(uid).update(upd)
        except Exception:
            traceback.print_exc()


# ---------------------------------------------------------------- εβδομαδιαία σύνοψη
def positions(d, since):
    pos = {}
    for t in sorted(d.get("txns") or [], key=lambda t: (t.get("date") or "", t.get("ts") or 0)):
        k = t.get("sym")
        if not k or k.startswith("p:"): continue
        p = pos.setdefault(k, {"qty": 0.0, "qty0": 0.0, "cost": 0.0, "flow": 0.0, "last": 0.0, "mp": None, "mpTs": 0, "m": t.get("m") or {}})
        q, px = float(t.get("qty") or 0), float(t.get("price") or 0)
        sell = t.get("side") == "sell"
        if sell:
            avg = p["cost"] / p["qty"] if p["qty"] else 0
            q = min(q, p["qty"]); p["cost"] -= q * avg; p["qty"] -= q
        else:
            p["qty"] += q; p["cost"] += q * px
        if (t.get("date") or "") <= since: p["qty0"] = p["qty"]
        else: p["flow"] += -q * px if sell else q * px
        p["last"] = px or p["last"]
        if t.get("m"): p["m"] = t["m"]
        if t.get("mp") is not None and (t.get("mpTs") or 0) >= p["mpTs"]: p["mp"], p["mpTs"] = float(t["mp"]), t.get("mpTs") or 0
    return {k: v for k, v in pos.items() if v["qty"] > 1e-9 or v["qty0"] > 1e-9}


def label(k, p, P):
    m = p.get("m") or {}
    if k.startswith("c:"):
        q = P.cg.get(k[2:]) or {}
        return q.get("s") or m.get("s") or k[2:].upper(), q.get("n") or m.get("n") or ""
    if k.startswith("f:"): return k[2:], (P.us.get(k[2:]) or {}).get("n") or m.get("n") or ""
    if k.startswith("m:"): return m.get("n") or m.get("s") or "Άλλο", ""
    s = P.gr.get(k) or {}
    return k, (s.get("name") or "").title()


def yahoo_week(sym):
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/" + sym, params={"range": "1mo", "interval": "1d"}, headers=UA, timeout=20)
        res = r.json()["chart"]["result"][0]
        ts, cl = res["timestamp"], res["indicators"]["quote"][0]["close"]
        pts = [(t, c) for t, c in zip(ts, cl) if c is not None]
        last_t, last = pts[-1]
        base = [c for t, c in pts if t <= last_t - 6.5 * 86400]
        return (last / base[-1] - 1) * 100 if base else None
    except Exception as e:
        print("Yahoo", sym, e); return None


BENCH = None


def weekly_for(uid, d, P):
    global BENCH
    user = os.environ.get("GMAIL_USER", "").strip()
    pw = os.environ.get("GMAIL_APP_PW", "").strip().replace(" ", "")
    if not user or not pw:
        print("Δεν έχουν οριστεί GMAIL_USER / GMAIL_APP_PW· η σύνοψη δεν στέλνεται."); return
    from firebase_admin import auth
    try: to = auth.get_user(uid).email
    except Exception as e: print("χωρίς email", uid[:6], e); return
    if not to: return
    since = (now_ath() - timedelta(days=7)).strftime("%Y-%m-%d")
    pos = positions(d, since)
    P.need(set(pos))
    rows, v_now, v_0, flows = [], 0.0, 0.0, 0.0
    for k, p in pos.items():
        q = P.get(k)
        if k.startswith("m:"): px, w = (p["mp"] if p["mp"] is not None else p["last"]), 0.0
        elif q: px, w = q["eur"], q.get("w")
        else: px, w = p["last"], None
        val = p["qty"] * px
        p0 = px / (1 + w / 100) if w is not None and w > -99 else px
        v_now += val; v_0 += p["qty0"] * p0; flows += p["flow"]
        lab, name = label(k, p, P)
        if p["qty"] > 1e-9: rows.append({"k": k, "lab": lab, "n": name, "v": val, "w": w, "pl": (val / p["cost"] - 1) * 100 if p["cost"] else None})
    # Perpetuals (Hyperliquid)
    for wl in d.get("wallets") or []:
        try:
            r = requests.post("https://api.hyperliquid.xyz/info", json={"type": "clearinghouseState", "user": wl["a"]}, timeout=20).json()
            av = float((r.get("marginSummary") or {}).get("accountValue") or 0) / P.usd
            hist = requests.post("https://api.hyperliquid.xyz/info", json={"type": "portfolio", "user": wl["a"]}, timeout=20).json()
            wk = [x for x in hist if x[0] == "week"]
            av0 = float(wk[0][1]["accountValueHistory"][0][1]) / P.usd if wk and wk[0][1].get("accountValueHistory") else av
            if av > 0:
                v_now += av; v_0 += av0
                rows.append({"k": "p:", "lab": "HL", "n": wl.get("n") or "Hyperliquid", "v": av, "w": (av / av0 - 1) * 100 if av0 else None, "pl": None})
        except Exception as e: print("Hyperliquid", e)
    change = v_now - v_0 - flows
    base = v_0 + max(flows, 0)
    pct = change / base * 100 if base else None
    rows.sort(key=lambda r: -r["v"])
    movers = sorted([r for r in rows if r["w"] is not None], key=lambda r: -r["w"])
    # επόμενα γεγονότα
    t1 = (now_ath() + timedelta(days=1)).strftime("%Y-%m-%d"); t2 = (now_ath() + timedelta(days=8)).strftime("%Y-%m-%d")
    ev = []
    for r in rows:
        o = P.scr.get(r["k"]) or {}
        for key, txt in (("earn", "Αποτελέσματα"), ("exd", "Αποκοπή μερίσματος"), ("pay", "Πληρωμή μερίσματος")):
            dt = o.get(key)
            if dt and t1 <= dt <= t2: ev.append((dt, r["lab"], txt + (" " + fmt_num(o["dps"], 3) + (" €" if not r["k"].startswith("f:") else " $") if key != "earn" and o.get("dps") else "")))
    ex = (load("extras.json", {}).get("stocks") or {})
    for r in rows:
        e = ex.get(r["k"]) or {}
        if e.get("exd") and t1 <= e["exd"] <= t2 and not any(x[1] == r["lab"] and x[0] == e["exd"] for x in ev): ev.append((e["exd"], r["lab"], "Αποκοπή μερίσματος"))
    ev.sort()
    if BENCH is None:
        BENCH = [("Γενικός Δείκτης", yahoo_week("GD.AT")), ("S&P 500", yahoo_week("%5EGSPC")), ("Bitcoin", yahoo_week("BTC-EUR"))]
    alerts = d.get("alerts") or []
    fired = [a for a in alerts if a.get("fired") and a["fired"] >= (time.time() - 7 * 86400) * 1000]
    active = sum(1 for a in alerts if a.get("on"))
    send_email(user, pw, to, v_now, change, pct, rows, movers, ev, BENCH, fired, active, since)


def pill(v):
    col = "#21a36a" if (v or 0) > 0.004 else "#d6474f" if (v or 0) < -0.004 else "#8a93a6"
    return '<span style="color:%s;font-weight:700">%s</span>' % (col, fmt_pct(v))


def send_email(user, pw, to, v_now, change, pct, rows, movers, ev, bench, fired, active, since):
    e = html.escape
    d0 = datetime.strptime(since, "%Y-%m-%d") + timedelta(days=1)
    rng = d0.strftime("%d/%m") + "–" + now_ath().strftime("%d/%m")
    td = 'style="padding:8px 0;border-bottom:1px solid #2a3142;color:#e8ecf4"'
    best = [m for m in movers if m["w"] > 0.004][:3]; worst = [m for m in movers[::-1] if m["w"] < -0.004][:3]
    def mv_rows(lst): return "".join('<tr><td %s><b>%s</b> <span style="color:#8a93a6">%s</span></td><td %s align="right">%s</td></tr>' % (td, e(r["lab"]), e((r["n"] or "")[:34]), td, pill(r["w"])) for r in lst)
    hold = "".join('<tr><td %s><b>%s</b> <span style="color:#8a93a6">%s</span></td><td %s align="right">%s €</td><td %s align="right">%s</td></tr>' % (td, e(r["lab"]), e((r["n"] or "")[:28]), td, fmt_num(r["v"]), td, pill(r["w"])) for r in rows[:12])
    evs = "".join('<tr><td %s style="color:#8a93a6;padding:6px 14px 6px 0">%s</td><td %s><b>%s</b> · %s</td></tr>' % ("", datetime.strptime(x[0], "%Y-%m-%d").strftime("%d/%m"), 'style="color:#e8ecf4;padding:6px 0"', e(x[1]), e(x[2])) for x in ev[:12])
    bh = " &nbsp;·&nbsp; ".join("%s %s" % (e(n), pill(v)) for n, v in bench if v is not None)
    sec = lambda t: '<h3 style="margin:26px 0 8px;font-size:15px;color:#c9d1e0">%s</h3>' % t
    body = ('<div style="background:#151a24;padding:24px 12px;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#e8ecf4">'
            '<div style="max-width:560px;margin:0 auto;background:#1e2430;border-radius:16px;padding:24px 22px">'
            '<div style="font-size:13px;color:#8a93a6">Axiogram · εβδομάδα %s</div>' % rng +
            '<div style="font-size:30px;font-weight:800;margin:10px 0 2px">%s €</div>' % fmt_num(v_now) +
            '<div style="font-size:16px">%s%s € (%s) αυτή την εβδομάδα</div>' % ("+" if change >= 0 else "−", fmt_num(abs(change)), fmt_pct(pct)) +
            ('<div style="font-size:13px;color:#8a93a6;margin-top:10px">Αγορές: %s</div>' % bh if bh else "") +
            (sec("Κέρδισαν περισσότερο") + '<table width="100%" cellspacing="0">' + mv_rows(best) + "</table>" if best else "") +
            (sec("Έχασαν περισσότερο") + '<table width="100%" cellspacing="0">' + mv_rows(worst) + "</table>" if worst else "") +
            (sec("Τι έρχεται την επόμενη εβδομάδα") + '<table cellspacing="0">' + evs + "</table>" if evs else "") +
            (sec("Ειδοποιήσεις") + '<div style="font-size:14px;color:#e8ecf4">%s%s</div>' % ("Ενεργές: %d. " % active, ("Αυτή την εβδομάδα ειδοποιήθηκες για: " + ", ".join(e(str(a.get("lab"))) for a in fired) + ".") if fired else "") if active or fired else "") +
            sec("Οι θέσεις σου") + '<table width="100%" cellspacing="0">' + hold + "</table>" +
            '<div style="text-align:center;margin:26px 0 6px"><a href="%s" style="background:#4062f0;color:#fff;text-decoration:none;padding:11px 22px;border-radius:999px;font-weight:700;display:inline-block">Άνοιξε το Axiogram</a></div>' % SITE +
            '<p style="font-size:12px;color:#8a93a6;line-height:1.5;margin:18px 0 0">Η μεταβολή της εβδομάδας είναι κατά προσέγγιση και δεν περιλαμβάνει τις αγορές και πωλήσεις που έκανες μέσα στην εβδομάδα. '
            'Τιμές από capital.gr, TradingView, CoinGecko και Hyperliquid. Δεν αποτελεί επενδυτική συμβουλή. '
            'Για να σταματήσεις τη σύνοψη: Axiogram → Εργαλεία → Ειδοποιήσεις.</p></div></div>')
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Axiogram · Η εβδομάδα σου: %s" % fmt_pct(pct)
    msg["From"] = formataddr(("Axiogram", user))
    msg["To"] = to
    text = "Axiogram · εβδομάδα %s\nΑξία: %s €\nΜεταβολή: %s (%s)\n\n%s" % (rng, fmt_num(v_now), fmt_num(change), fmt_pct(pct), SITE)
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(body, "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as s:
        s.login(user, pw)
        s.sendmail(user, [to], msg.as_string())
    print("  email στάλθηκε")


def run_weekly(db):
    P = Prices(); P.db = db
    for doc in db.collection("users").stream():
        d = doc.to_dict() or {}
        if not d.get("weekly"): continue
        print("σύνοψη για", doc.id[:6])
        try: weekly_for(doc.id, d, P)
        except Exception: traceback.print_exc()


# ---------------------------------------------------------------- σελίδα διαχείρισης (axiogram.eu/admin)
CMD_WF = {"prices": "update-prices.yml", "foreign": "update-foreign.yml", "extras": "update-extras.yml",
          "logos": "update-logos.yml", "longhist": "update-longhist.yml"}


def to_ms(v):
    """Το πεδίο updated μπορεί να είναι αριθμός (ms), κείμενο ISO ή Timestamp του Firestore."""
    if v is None: return 0
    if isinstance(v, (int, float)): return int(v if v > 1e11 else v * 1000)
    if hasattr(v, "timestamp"): return int(v.timestamp() * 1000)
    try: return int(datetime.fromisoformat(str(v).replace("Z", "+00:00")).timestamp() * 1000)
    except Exception: return 0


def write_stats(db):
    """Μόνο αριθμοί (κανένα email ή στοιχείο χρήστη) στο site/stats, για την επισκόπηση."""
    now = time.time() * 1000
    st = {"users": 0, "act7": 0, "act30": 0, "withPf": 0, "txns": 0, "alertsOn": 0, "push": 0, "weekly": 0, "wallets": 0, "fired24": 0}
    for doc in db.collection("users").stream():
        d = doc.to_dict() or {}
        st["users"] += 1
        u = to_ms(d.get("updated"))
        if u and now - u < 7 * 864e5: st["act7"] += 1
        if u and now - u < 30 * 864e5: st["act30"] += 1
        tx = d.get("txns") or []
        if tx: st["withPf"] += 1
        st["txns"] += len(tx)
        al = d.get("alerts") or []
        st["alertsOn"] += sum(1 for a in al if a.get("on"))
        st["fired24"] += sum(1 for a in al if a.get("fired") and now - float(a["fired"]) < 864e5)
        st["push"] += sum(1 for t in (d.get("push") or []) if t.get("t"))
        if d.get("weekly"): st["weekly"] += 1
        st["wallets"] += len(d.get("wallets") or [])
    st["at"] = int(now)
    db.collection("site").document("stats").set(st)
    print("στατιστικά:", {k: v for k, v in st.items() if k != "at"})


def run_cmds(db):
    """Εκτελεί τα «Τρέξε τώρα» που ζήτησε ο ιδιοκτήτης από τη σελίδα διαχείρισης."""
    ref = db.collection("site").document("cmd")
    snap = ref.get()
    runs = (snap.to_dict() or {}).get("runs") or {} if snap.exists else {}
    tok = os.environ.get("GH_TOKEN"); repo = os.environ.get("GITHUB_REPOSITORY", "Paschalakis/grmarketcap")
    for k, v in runs.items():
        at, done = (v or {}).get("at") or 0, (v or {}).get("done") or 0
        if not at or done >= at or k not in CMD_WF: continue
        ok = False
        if tok:
            r = requests.post("https://api.github.com/repos/%s/actions/workflows/%s/dispatches" % (repo, CMD_WF[k]),
                              headers={"Authorization": "Bearer " + tok, "Accept": "application/vnd.github+json"}, json={"ref": "main"}, timeout=20)
            ok = r.status_code == 204
            print("εκτέλεση", k, r.status_code, "" if ok else r.text[:200])
        ref.set({"runs": {k: {"at": at, "done": int(time.time() * 1000), "ok": ok}}}, merge=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "alerts"
    try:
        db = init_fb()
        if db is not None:
            run_weekly(db) if mode == "weekly" else run_alerts(db)
            for f in (run_cmds, write_stats):
                try: f(db)
                except Exception: traceback.print_exc()
    except Exception:
        traceback.print_exc()
    sys.exit(0)
