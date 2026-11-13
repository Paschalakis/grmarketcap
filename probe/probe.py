import requests, json
U="https://api.hyperliquid.xyz/info"
r=requests.options(U,headers={"Origin":"https://paschalakis.github.io","Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"content-type"},timeout=20)
print("OPTIONS",r.status_code,{k:v for k,v in r.headers.items() if k.lower().startswith("access-control")})
r=requests.post(U,json={"type":"allMids"},headers={"Origin":"https://paschalakis.github.io"},timeout=20)
print("POST",r.status_code,{k:v for k,v in r.headers.items() if k.lower().startswith("access-control")}, len(r.text))
m=r.json(); print({k:m[k] for k in list(m)[:5]}, "HYPE" in m)
# a known public vault address to see structure
r=requests.post(U,json={"type":"clearinghouseState","user":"0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"},timeout=20)
print("STATE",r.status_code,json.dumps(r.json())[:1500])
r=requests.post(U,json={"type":"meta"},timeout=20); print("META",json.dumps(r.json())[:300])
