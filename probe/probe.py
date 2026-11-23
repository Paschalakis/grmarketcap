import json, urllib.request, subprocess, time
time.sleep(60)
u="https://firestore.googleapis.com/v1/projects/agora-athinon/databases/(default)/documents/site/crypto?key=AIzaSyDd3-HyjHU6Cji1DwPtZ6epuJxFUT6luws"
try:
    j=json.load(urllib.request.urlopen(u,timeout=30)); d=json.loads(j["fields"]["c"]["stringValue"])
    print("firestore: updated",d["updated"],"cur",d.get("cur"),"every",d.get("every"),"coins",len(d["c"]),"BTC",d["c"][0][5],"g",d.get("g"),"fng",(d.get("fng") or [])[:2])
except Exception as e: print("firestore ERR",e)
r=subprocess.run(["node","probe/tv.js"],capture_output=True,text=True,timeout=200);print(r.stdout[-2500:]);print(r.stderr[-800:])
