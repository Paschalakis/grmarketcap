import requests, json
H = {"User-Agent": "Mozilla/5.0 Chrome/124", "Origin": "https://www.tradingview.com", "Referer": "https://www.tradingview.com/", "Content-Type": "application/json"}
cands=["earnings_release_next_date","earnings_release_date","earnings_release_next_trading_date_fq","ex_dividend_date_upcoming","dividend_ex_date_upcoming","dividend_payment_date_upcoming","dividends_yield_current","dividends_yield","dividend_yield_recent","price_earnings_ttm","price_book_fq","price_book_ratio","return_on_equity","Perf.Y","Perf.YTD","beta_1_year","dividend_payout_ratio_ttm","earnings_per_share_diluted_ttm","RSI","Recommend.All","net_margin","total_revenue_yoy_growth_ttm","debt_to_equity","price_sales_ratio","High.All","price_52_week_high","price_52_week_low","dps_common_stock_prim_issue_fy","dividends_per_share_fq","earnings_per_share_forecast_next_fq","industry","sector"]
for m in ["greece","america"]:
  ok=[]
  for c in cands:
    b={"columns":["name",c],"range":[0,3],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"},"filter":[]}
    r=requests.post("https://scanner.tradingview.com/%s/scan"%m,headers=H,data=json.dumps(b),timeout=30)
    if r.status_code==200: ok.append((c,[d["d"][1] for d in r.json().get("data",[])]))
    else: print(m,c,"BAD",r.status_code)
  for c,v in ok: print(m,c,v)
