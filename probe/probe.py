import urllib.request, json, time
time.sleep(240)
K="AIzaSyDd3-HyjHU6Cji1DwPtZ6epuJxFUT6luws"
req=urllib.request.Request("https://identitytoolkit.googleapis.com/v1/accounts:createAuthUri?key="+K,
  data=json.dumps({"providerId":"google.com","continueUri":"https://axiogram.eu/__/auth/handler","authFlowType":"CODE_FLOW"}).encode(),
  headers={"Content-Type":"application/json","Referer":"https://axiogram.eu/"})
try:
  j=json.load(urllib.request.urlopen(req,timeout=30)); u=j.get("authUri",""); print("authUri ok", "axiogram.eu" in u)
  r=urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0) Chrome/120"})
  try:
    resp=urllib.request.urlopen(r,timeout=30); d=resp.read().decode("utf8","ignore")
    print("google", resp.status, resp.geturl()[:80]); print("MISMATCH" if "redirect_uri_mismatch" in d else "no mismatch text")
  except urllib.error.HTTPError as e:
    d=e.read().decode("utf8","ignore"); print("google HTTP", e.code, "MISMATCH" if "redirect_uri_mismatch" in d else "other")
except Exception as e: print("ERR", e)
for u in ["http://axiogram.eu/"]:
  print(u, "->", urllib.request.urlopen(u,timeout=30).geturl())
