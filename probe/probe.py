import subprocess, json, re, requests
subprocess.run(["python","scripts/fetch_extras.py"])
d=json.load(open("extras.json"))
print("size", len(json.dumps(d,ensure_ascii=False)))
for k in ["ΑΛΦΑ","ΔΕΗ","ALWN","ΟΤΕ","ΜΟΗ","ΕΤΕ"]: print(k, json.dumps(d["stocks"].get(k),ensure_ascii=False)[:900])
print("with pe", sum(1 for v in d["stocks"].values() if "pe" in v), "exd", sum(1 for v in d["stocks"].values() if "exd" in v), "news", sum(1 for v in d["stocks"].values() if "news" in v), "nodate", sum(1 for v in d["stocks"].values() for n in v.get("news",[]) if not n["d"]))
t=requests.get("https://www.capital.gr/finance/news/%ce%b1%ce%bb%cf%86%ce%b1/",headers={"User-Agent":"Mozilla/5.0 Chrome/124"}).text
i=t.find("/4023811/"); print("CTX", t[max(0,i-1500):i+300])
