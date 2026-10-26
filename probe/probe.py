import re, requests
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36","Accept-Language":"el-GR,el;q=0.9"}
def get(u):
    try: r=requests.get(u,headers=H,timeout=25); return r.status_code, r.text
    except Exception as e: return 0, str(e)
def txt(t): 
    t=re.sub(r"<script.*?</script>|<style.*?</style>","",t,flags=re.S); return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",t))
c,t=get("https://www.capital.gr/finance/quote/%CE%9F%CE%A0%CE%91%CE%A0/")
print("QUOTE",c,len(t))
hs=sorted(set(re.findall(r'href="([^"]+)"',t)))
print("LINKS:"); [print("  ",h) for h in hs if re.search(r"quote|merism|dividend|news|/epixeiriseis|/agores|/api",h,re.I)][:80]
print("APIS:", sorted(set(re.findall(r'["\'](/api/[^"\']+)',t)))[:40])
T=txt(t)
for k in ["P/E","Μέρισμα","Απόδοση","Κεφαλαιοποίηση","Αριθμός μετοχών","EPS","Beta","52","Ελεύθερη","Free"]:
    for m in list(re.finditer(re.escape(k),T))[:2]: print("..",k,"::",T[max(0,m.start()-120):m.end()+200])
for u in ["https://www.capital.gr/finance/dividends","https://www.capital.gr/finance/merismata","https://www.capital.gr/finance/quote/%CE%9F%CE%A0%CE%91%CE%A0/news","https://www.capital.gr/finance/quotenews/%CE%9F%CE%A0%CE%91%CE%A0","https://www.euro2day.gr/AseDividends.aspx","https://www.euro2day.gr/AseSearchQuotes.aspx","https://www.naftemporiki.gr/finance/markets/merismata/","https://www.naftemporiki.gr/symbols/OPAP.ATH","https://www.naftemporiki.gr/symbols/OPAP.ATH/news/2131515"]:
    c,t=get(u); print("\n###",u,c,len(t)); 
    if c==200:
        T=txt(t); i=max(T.find("Μέρισμα"),0); print(T[i:i+800])
        print([h for h in sorted(set(re.findall(r'href="([^"]+)"',t))) if re.search(r"symbols|merism|dividend|quote",h,re.I)][:30])
