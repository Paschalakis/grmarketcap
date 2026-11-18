import os, json, urllib.request
tok=os.environ.get("GH_TOKEN","")
r=urllib.request.Request("https://api.github.com/repos/Paschalakis/grmarketcap/actions/workflows/update-prices.yml/dispatches", data=json.dumps({"ref":"main"}).encode(), method="POST", headers={"Authorization":"Bearer "+tok,"Accept":"application/vnd.github+json"})
try: print("dispatch", urllib.request.urlopen(r,timeout=30).status)
except Exception as e: print("ERR", e, getattr(e,"read",lambda:b"")())
