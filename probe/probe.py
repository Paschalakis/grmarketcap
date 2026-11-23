import subprocess, os
subprocess.run(["pip","install","-q","firebase-admin","requests"],capture_output=True)
env=dict(os.environ, CMC_RUN_MIN="0.2")
r=subprocess.run(["python3","scripts/fetch_cmc.py"],cwd="probe",env=env,capture_output=True,text=True,timeout=300)
print(r.stdout[-3000:]); print(r.stderr[-3000:])
import json
try:
  d=json.load(open("probe/crypto.json")); print("coins",len(d["c"]),"g",d["g"],"fng",(d["fng"] or [])[:2], "slugs", [c[1] for c in d["c"][:40]])
  s=json.load(open("probe/cspark.json")); print("spark n",len(s["d"]),"len btc",len(s["d"]["bitcoin"]), "size", len(json.dumps(s,separators=(',',':')))//1024,"KB")
except Exception as e: print("ERR",e)
