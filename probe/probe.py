import subprocess, time
time.sleep(60)
for u in ["http://axiogram.eu/","https://axiogram.eu/","http://www.axiogram.eu/","https://paschalakis.github.io/grmarketcap/","https://axiogram.eu/data.json"]:
    r=subprocess.run(["curl","-sS","-o","/dev/null","-L","--max-time","30","-w","%{http_code} final=%{url_effective} ssl=%{ssl_verify_result}",u],capture_output=True,text=True)
    print(u,"->",r.stdout,r.stderr.strip()[:160])
r=subprocess.run(["curl","-sS","--max-time","30","-L","http://axiogram.eu/"],capture_output=True,text=True)
import re; print("title:",re.findall(r"<title>(.*?)</title>",r.stdout)[:1])
r=subprocess.run(["bash","-c","echo | openssl s_client -connect axiogram.eu:443 -servername axiogram.eu 2>/dev/null | openssl x509 -noout -subject -issuer -dates"],capture_output=True,text=True)
print("cert:",r.stdout.strip().replace("\n"," | ") or r.stderr.strip()[:200])
