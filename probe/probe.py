import re, requests, json
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36","Accept-Language":"en-US,en;q=0.9"}
s=requests.Session(); s.headers.update(H)
r=s.get("https://query1.finance.yahoo.com/v8/finance/chart/ALPHA.AT?range=2y&interval=1mo&events=div",timeout=25); print("CHART",r.status_code); 
try: j=r.json(); print(json.dumps(j["chart"]["result"][0].get("events"),ensure_ascii=False)[:800]); print(json.dumps(j["chart"]["result"][0]["meta"])[:600])
except Exception as e: print(e, r.text[:300])
try:
    s.get("https://fc.yahoo.com",timeout=15)
except Exception as e: print("fc",e)
cr=s.get("https://query1.finance.yahoo.com/v1/test/getcrumb",timeout=15); print("CRUMB",cr.status_code,cr.text[:40])
r=s.get("https://query2.finance.yahoo.com/v10/finance/quoteSummary/ALPHA.AT",params={"modules":"summaryDetail,defaultKeyStatistics,calendarEvents,financialData","crumb":cr.text},timeout=25)
print("QS",r.status_code); print(r.text[:4000])
r=s.get("https://query1.finance.yahoo.com/v7/finance/quote",params={"symbols":"ALPHA.AT,PPC.AT,ALWN.AT","crumb":cr.text},timeout=25); print("Q7",r.status_code,r.text[:2500])
