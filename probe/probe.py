import subprocess, json
subprocess.run(["python","scripts/fetch_extras.py"])
d=json.load(open("extras.json"))
for k in ["ΑΛΦΑ","ΔΕΗ","ALWN"]: print(k, json.dumps(d["stocks"].get(k,{}).get("news"),ensure_ascii=False)[:1200])
print("with pe", sum(1 for v in d["stocks"].values() if "pe" in v), "exd", sum(1 for v in d["stocks"].values() if "exd" in v), "news", sum(1 for v in d["stocks"].values() if "news" in v), "nodate", sum(1 for v in d["stocks"].values() for n in v.get("news",[]) if not n["d"]))
