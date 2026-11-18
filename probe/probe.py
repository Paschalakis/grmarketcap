import urllib.request, json, os, time, io, zipfile
tok=os.environ.get("GH_TOKEN","")
H={"Authorization":"Bearer "+tok,"Accept":"application/vnd.github+json"}
B="https://api.github.com/repos/Paschalakis/grmarketcap/"
def api(u, data=None, method=None):
    r=urllib.request.Request(B+u, data=data, method=method, headers=H)
    return urllib.request.urlopen(r,timeout=60)
t0=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
api("actions/workflows/notify.yml/dispatches", json.dumps({"ref":"main","inputs":{"mode":"alerts"}}).encode(), "POST")
rid=None
for i in range(40):
    time.sleep(10)
    runs=json.load(api("actions/workflows/notify.yml/runs?per_page=5"))["workflow_runs"]
    mine=[r for r in runs if r["created_at"]>=t0]
    if mine and mine[0]["status"]=="completed": rid=mine[0]["id"]; break
print("run", rid, [ (r["event"],r["status"],r["created_at"]) for r in runs[:4]])
if rid:
    z=zipfile.ZipFile(io.BytesIO(api("actions/runs/%d/logs"%rid).read()))
    for n in z.namelist():
        if "Ειδοποι" in n or "notify" in n.lower():
            txt=z.read(n).decode("utf8","ignore")
            lines=[l for l in txt.splitlines() if "##[" not in l and "pip" not in l.lower()]
            print("==",n); print("\n".join(lines[-40:]))
