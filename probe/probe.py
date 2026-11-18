import subprocess
for args in (["axiogram.eu","A"],["www.axiogram.eu","CNAME"],["www.axiogram.eu","A"],["axiogram.eu","NS"]):
    for srv in ("8.8.8.8","1.1.1.1","dns1.papaki.gr"):
        r=subprocess.run(["dig","+short","@"+srv]+args,capture_output=True,text=True,timeout=20)
        print(args, srv, "->", r.stdout.strip().replace("\n"," | ") or "(κενό)", r.stderr.strip()[:80])
