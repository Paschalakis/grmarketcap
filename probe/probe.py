import os, json, urllib.request
tok=os.environ.get("GH_TOKEN","")
def get(u):
    r=urllib.request.Request("https://api.github.com/repos/Paschalakis/grmarketcap/"+u, headers={"Authorization":"Bearer "+tok,"Accept":"application/vnd.github+json"})
    return json.load(urllib.request.urlopen(r,timeout=30))
runs=get("actions/workflows/update-prices.yml/runs?per_page=8")
for r in runs.get("workflow_runs",[]):
    print(r["id"], r["event"], r["status"], r["conclusion"], r["created_at"], r["updated_at"])
    if r["status"]!="completed" or r["created_at"]>"2026-11-18":
        jobs=get("actions/runs/%d/jobs"%r["id"])
        for j in jobs.get("jobs",[]):
            print("  job", j["status"], j["conclusion"], j["started_at"], [ (s["name"],s["status"],s["conclusion"]) for s in j.get("steps",[])])
