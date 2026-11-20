import subprocess
print(subprocess.run(["node","probe/tv.js"],capture_output=True,text=True,timeout=120).stdout)
