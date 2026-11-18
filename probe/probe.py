import urllib.request, os
os.makedirs("probe/auth", exist_ok=True)
B="https://agora-athinon.firebaseapp.com"
for p in ["__/auth/handler","__/auth/handler.js","__/auth/experiments.js","__/auth/iframe","__/auth/iframe.js","__/firebase/init.json","__/firebase/init.js"]:
    try:
        r=urllib.request.urlopen(B+"/"+p, timeout=30); d=r.read()
        open("probe/auth/"+p.replace("/","_"),"wb").write(d)
        print(p, r.status, len(d), r.headers.get("content-type"))
    except Exception as e: print(p, "ERR", e)
