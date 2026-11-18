import urllib.request, time
time.sleep(90)
for p in ["__/auth/handler?apiKey=x","__/auth/handler.js","__/auth/iframe","__/auth/experiments.js","sw.js"]:
    try:
        r=urllib.request.urlopen("https://axiogram.eu/"+p, timeout=30); d=r.read()
        print(p, r.status, len(d), r.headers.get("content-type"), r.geturl(), d[:60] if p=="sw.js" else "")
    except Exception as e: print(p, "ERR", e)
