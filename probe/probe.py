import urllib.request, time, json, os
time.sleep(60)
def g(u):
    r=urllib.request.urlopen(u,timeout=30); return r.read().decode("utf8","ignore")
h=g("https://axiogram.eu/?x=%d"%time.time())
print("tools view", "view-tools" in h, "tl-scr" in h, "pf-share" in h, len(h))
print("sw push", "notificationclick" in g("https://axiogram.eu/sw.js?x=1"))
j=json.loads(g("https://axiogram.eu/screener.json"));print("screener", j["updated"], len(j["gr"]), len(j["us"]), j["cols"][-1])
print("http->https", urllib.request.urlopen("http://axiogram.eu/",timeout=30).geturl())
tok=os.environ.get("GH_TOKEN","")
def api(u):
    r=urllib.request.Request("https://api.github.com/repos/Paschalakis/grmarketcap/"+u, headers={"Authorization":"Bearer "+tok,"Accept":"application/vnd.github+json"})
    return json.load(urllib.request.urlopen(r,timeout=30))
for wf in ["notify.yml","update-prices.yml"]:
    for r in api("actions/workflows/%s/runs?per_page=3"%wf).get("workflow_runs",[]): print(wf, r["event"], r["status"], r["conclusion"], r["created_at"])
