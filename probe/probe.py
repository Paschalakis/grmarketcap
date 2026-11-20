import subprocess
r=subprocess.run(["node","probe/tv.js"],capture_output=True,text=True,timeout=200);print(r.stdout);print(r.stderr[-1500:])
# 1795183488
