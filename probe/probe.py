import json, urllib.request, urllib.error
C="1idw-IXGU7tFB4ds1WN"
def st(path):
    u="https://cdn.brandfetch.io/"+path+("&" if "?" in path else "?")+"c="+C
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0","Referer":"https://axiogram.eu/"}),timeout=20)
        b=r.read(); return "%d %s %d"%(r.status, r.headers.get("content-type"), len(b))
    except urllib.error.HTTPError as e: return "%d %s"%(e.code, e.read()[:80])
    except Exception as e: return "ERR "+str(e)[:60]
for p in ["ticker/AAPL","ticker/AAPL/w/64/h/64/fallback/404/icon.png","ticker/AAPL/fallback/404/w/64/h/64/icon.png","ticker/ZZZZQX/fallback/404/icon","ticker/ZZZZQX","crypto/BTC/fallback/404/icon","domain/dei.gr/w/64/h/64/fallback/404/icon.png","ticker/BRK-B/fallback/404/icon","ticker/BRK.B/fallback/404/icon"]:
    print(p, "=>", st(p))
d=json.load(open("probe/grdom.json"))
for k,v in d.items(): print("GR",k,v,"=>",st("domain/%s/w/64/h/64/fallback/404/icon.png"%v))
