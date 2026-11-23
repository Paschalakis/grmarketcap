import json, os, urllib.request
K=os.environ["CMC_API_KEY"]
j=json.load(urllib.request.urlopen(urllib.request.Request("https://pro-api.coinmarketcap.com/v1/key/info",headers={"X-CMC_PRO_API_KEY":K}),timeout=30))
d=j["data"]; print("plan",json.dumps(d.get("plan")), "usage", json.dumps((d.get("usage") or {}).get("current_month")))
