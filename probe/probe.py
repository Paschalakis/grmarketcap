import urllib.request, json, os, io, zipfile
H={"Authorization":"Bearer "+os.environ.get("GH_TOKEN",""),"Accept":"application/vnd.github+json"}
r=urllib.request.urlopen(urllib.request.Request("https://api.github.com/repos/Paschalakis/grmarketcap/actions/runs/44277409885/logs",headers=H),timeout=60)
z=zipfile.ZipFile(io.BytesIO(r.read()))
for n in z.namelist():
    if "Ειδοποι" in n:
        t=z.read(n).decode("utf8","ignore").splitlines()
        i=[k for k,l in enumerate(t) if "χρήστες" in l][0]
        print("\n".join(l[29:] for l in t[i:]))
