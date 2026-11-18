import urllib.request, json, os
tok=os.environ.get("GH_TOKEN","")
def api(u):
    r=urllib.request.Request("https://api.github.com/repos/Paschalakis/grmarketcap/"+u, headers={"Authorization":"Bearer "+tok,"Accept":"application/vnd.github+json"})
    return json.load(urllib.request.urlopen(r,timeout=30))
for r in api("actions/workflows/notify.yml/runs?per_page=5").get("workflow_runs",[]): print("notify", r["id"], r["event"], r["status"], r["conclusion"], r["created_at"])
r=urllib.request.Request("https://api.github.com/repos/Paschalakis/grmarketcap/actions/workflows/notify.yml/dispatches", data=json.dumps({"ref":"main","inputs":{"mode":"alerts"}}).encode(), method="POST", headers={"Authorization":"Bearer "+tok,"Accept":"application/vnd.github+json"})
print("dispatch", urllib.request.urlopen(r,timeout=30).status)
