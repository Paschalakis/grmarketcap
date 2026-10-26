import re, requests, sys
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36","Accept-Language":"el-GR,el;q=0.9"}
def get(u):
    try:
        r=requests.get(u,headers=H,timeout=25); return r.status_code, r.text
    except Exception as e: return 0, str(e)
def links(u, pat):
    c,t=get(u); hs=sorted(set(re.findall(r'href="([^"]+)"',t)))
    m=[h for h in hs if re.search(pat,h,re.I)]
    print(f"\n### {u} -> {c} len={len(t)} links={len(hs)}"); [print("  ",h) for h in m[:60]]
    return t
def show(u, n=1500, find=None):
    c,t=get(u); print(f"\n### {u} -> {c} len={len(t)}")
    if find:
        for f in find:
            for m in list(re.finditer(f,t,re.I))[:3]: print("  ..",re.sub(r"\s+"," ",t[max(0,m.start()-300):m.end()+500]))
    else: print(t[:n])
links("https://www.capital.gr/finance/allstocks", r"quote|stock|μερισ|dividend|merism")
t=links("https://www.capital.gr/", r"merism|dividend|finance/")
links("https://www.euro2day.gr/", r"Ase|merism|dividend|stock|quote")
links("https://www.naftemporiki.gr/finance/", r"symbol|merism|dividend")
show("https://www.naftemporiki.gr/symbols/OPAP.ATH/", find=[r"P/E", r"Μέρισμα", r"Απόδοση"])
show("https://www.naftemporiki.gr/symbols/OPAP.ATH/news/", find=[r"<article", r"href=\"/[a-z]+/\d+"])
# r2
