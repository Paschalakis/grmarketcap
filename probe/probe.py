import re, requests
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36","Accept-Language":"el-GR,el;q=0.9"}
def get(u):
    try: r=requests.get(u,headers=H,timeout=25); return r.status_code, r.text
    except Exception as e: return 0, str(e)
def txt(t):
    t=re.sub(r"<script.*?</script>|<style.*?</style>","",t,flags=re.S); return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",t))
def scan(u, keys, linkpat, n=200):
    c,t=get(u); print("\n#####",u,c,len(t))
    if c!=200: return t
    hs=sorted(set(re.findall(r'href="([^"]+)"',t))); print("LINKS:",[h for h in hs if re.search(linkpat,h,re.I)][:40])
    print("APIS:", sorted(set(re.findall(r'["\']((?:https?://[^"\']*)?/api/[^"\']+)',t)))[:30])
    T=txt(t)
    for k in keys:
        for m in list(re.finditer(re.escape(k),T))[:2]: print("..",k,"::",T[max(0,m.start()-100):m.end()+n])
    return t
K=["P/E","Μέρισμα","Απόδοση","Κεφαλαιοποίηση","Αριθμός μετοχών","Μετοχές","EPS","Κέρδη ανά","52","Ελεύθερη","Free","Αποκοπή","Ειδήσεις"]
scan("https://www.capital.gr/finance/quote/%ce%9f%ce%a0%ce%91%ce%a0/",K,r"quote/|merism|dividend|news|/api")
t=scan("https://www.euro2day.gr/AseSearchQuotesAllCodes.aspx",[],r"\.aspx\?|Ase.*s=|quote|stock")
m=re.findall(r'href="([^"]*(?:OPAP|%CE%9F%CE%A0%CE%91%CE%A0|ΟΠΑΠ)[^"]*)"',t,re.I); print("OPAP links",m[:10])
c,t=get("https://www.naftemporiki.gr/symbols/ALPHA.ATH/news/2131515")
print("NAFT symbol links", sorted(set(re.findall(r'href="(/symbols/[^"]+|/finance/[^"]*symbol[^"]*|/[a-z/]*ALPHA[^"]*)"',t)))[:30])
for u in ["https://www.naftemporiki.gr/symbols/ALPHA.ATH/","https://www.naftemporiki.gr/symbols/ALPHA.ATH/news","https://www.naftemporiki.gr/finance/symbols/ALPHA.ATH/","https://www.naftemporiki.gr/finance/stock/ALPHA.ATH"]:
    c,t=get(u); print(u,c,len(t))
