import re, requests
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36","Accept-Language":"el-GR,el;q=0.9"}
def get(u):
    try: r=requests.get(u,headers=H,timeout=25); return r.status_code, r.text
    except Exception as e: return 0, str(e)
def txt(t):
    t=re.sub(r"<script.*?</script>|<style.*?</style>","",t,flags=re.S); return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",t))
u="https://www.capital.gr/finance/quote/%ce%91%ce%9b%ce%a6%ce%91/"
c,t=get(u); print("#####",u,c,len(t))
hs=sorted(set(re.findall(r'href="([^"]+)"',t))); print("LINKS:",[h for h in hs if re.search(r"quote|merism|dividend|news|finance",h,re.I)][:60])
print("APIS:", sorted(set(re.findall(r'["\']((?:https?:)?[^"\']*/api/[^"\']+)',t)))[:30])
T=txt(t); print("TEXT:", T[:200])
for k in ["P/E","Μέρισμα","Απόδοση","Κεφαλαιοποίηση","μετοχών","EPS","Κέρδη","52","Ελεύθερη","Αποκοπή","Beta","Υψηλό","Χαμηλό"]:
    for m in list(re.finditer(re.escape(k),T))[:2]: print("..",k,"::",T[max(0,m.start()-100):m.end()+200])
c,t=get("https://www.euro2day.gr/AseSearchQuotesAllCodes.aspx")
i=t.find("ΑΛΦΑ"); print("\nE2D around ΑΛΦΑ:", t[max(0,i-1500):i+600])
