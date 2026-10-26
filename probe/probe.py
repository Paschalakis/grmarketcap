import re, requests, json
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36","Accept-Language":"el-GR,el;q=0.9"}
def get(u, j=False):
    h=dict(H)
    if j: h.update({"Accept":"application/json","X-Requested-With":"XMLHttpRequest","Referer":"https://www.capital.gr/"})
    try: r=requests.get(u,headers=h,timeout=25); return r.status_code, r.text
    except Exception as e: return 0, str(e)
def txt(t):
    t=re.sub(r"<script.*?</script>|<style.*?</style>","",t,flags=re.S); return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",t))
c,t=get("https://www.capital.gr/Api/Quotes/news/%CE%91%CE%9B%CE%A6%CE%91",True); print("NEWSAPI",c,len(t)); print(t[:1500])
c,t=get("https://www.euro2day.gr/QuotesDetail.aspx?q=30"); T=txt(t); i=T.find("ΑΛΦΑ"); print("\nE2D TEXT:", T[i:i+3500])
for u in ["https://www.capital.gr/finance/dividends/","https://www.capital.gr/finance/stockdividends/","https://www.capital.gr/finance/calendar/","https://www.euro2day.gr/AseCorporateActions.aspx","https://www.euro2day.gr/AseDividend.aspx","https://www.euro2day.gr/investments/ase/merismata/list.html","https://www.naftemporiki.gr/finance/merismata/","https://athens.euronext.com/el/markets/corporate-actions","https://www.athexgroup.gr/el/market-corporate-actions","https://www.mononews.gr/merismata"]:
    c,t=get(u); print("\n##",u,c,len(t))
c,t=get("https://www.euro2day.gr/")
print([h for h in sorted(set(re.findall(r'href="([^"]+)"',t))) if re.search(r"meris|divid|calend|hmerolog|etairik",h,re.I)])
