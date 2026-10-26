import re, requests, json
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36","Accept-Language":"el-GR,el;q=0.9"}
def get(u, j=False):
    h=dict(H); 
    if j: h.update({"Accept":"application/json","X-Requested-With":"XMLHttpRequest","Referer":"https://www.capital.gr/finance/quote/%ce%91%ce%9b%ce%a6%ce%91/"})
    try: r=requests.get(u,headers=h,timeout=25); return r.status_code, r.text
    except Exception as e: return 0, str(e)
def txt(t):
    t=re.sub(r"<script.*?</script>|<style.*?</style>","",t,flags=re.S); return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",t))
c,t=get("https://www.capital.gr/api/quotes/%CE%91%CE%9B%CE%A6%CE%91/full/?langCd=el",True); print("FULL",c,len(t)); print(t[:3000])
c,t=get("https://www.capital.gr/finance/news/%ce%91%ce%9b%ce%a6%ce%91/"); print("\nNEWS",c,len(t))
i=t.find("Alpha Bank"); 
arts=re.findall(r'<a[^>]+href="(/[^"]*/\d{6,}/[^"]*)"[^>]*>(.*?)</a>',t,re.S); print(len(arts)); [print("  ",a[0],"|",re.sub(r"\s+"," ",re.sub(r"<[^>]+>","",a[1]))[:120]) for a in arts[:25]]
m=re.search(r'href="(/[^"]*/\d{6,}/[^"]*)"',t); 
if m: j=t.find(m.group(0)); print("CTX:",t[max(0,j-800):j+900])
c,t=get("https://www.capital.gr/finance/profile/%ce%91%ce%9b%ce%a6%ce%91/"); print("\nPROFILE",c,len(t)); T=txt(t)
for k in ["P/E","Μέρισμα","Απόδοση","Κέρδη ανά","EPS","Ελεύθερη","Free float","Μερισματική","Αποκοπή"]:
    for m in list(re.finditer(re.escape(k),T))[:2]: print("..",k,"::",T[max(0,m.start()-100):m.end()+250])
c,t=get("https://www.euro2day.gr/QuotesDetail.aspx?q=30"); print("\nE2D",c,len(t)); T=txt(t)
for k in ["P/E","Μέρισμα","Απόδοση","Κέρδη ανά","EPS","Ελεύθερη","Free float","Αποκοπή","Μερισματική","Ρ/Ε"]:
    for m in list(re.finditer(re.escape(k),T))[:2]: print("..",k,"::",T[max(0,m.start()-100):m.end()+250])
