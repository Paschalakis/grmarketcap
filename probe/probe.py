import urllib.request, urllib.error
K="AIzaSyDd3-HyjHU6Cji1DwPtZ6epuJxFUT6luws"
for d in ["config","stats","cmd"]:
    u="https://firestore.googleapis.com/v1/projects/agora-athinon/databases/(default)/documents/site/%s?key=%s"%(d,K)
    try: r=urllib.request.urlopen(u,timeout=20); print(d,r.status)
    except urllib.error.HTTPError as e: print(d,e.code)
for u in ["https://axiogram.eu/admin/","https://axiogram.eu/"]:
    try:
        t=urllib.request.urlopen(u,timeout=20).read().decode()
        print(u,"Διαχείριση" in t, "siteBn" in t)
    except Exception as e: print(u,e)
