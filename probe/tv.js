const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--disable-blink-features=AutomationControlled']});
const c=await b.newContext({userAgent:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'});
const p=await c.newPage();
p.on('response',async r=>{if(/brandfetch/.test(r.url())){const h=r.headers();console.log('RESP',r.status(),h['content-type'],h['x-bf-error']||'',r.url().replace('1idw-IXGU7tFB4ds1WN','ID'));}});
await p.goto('https://axiogram.eu/',{waitUntil:'domcontentloaded'});
const C='?c=1idw-IXGU7tFB4ds1WN';
const urls=['apple.com','apple.com/w/64/h/64','domain/apple.com','ticker/AAPL','ticker/AAPL/icon','apple.com/fallback/404/icon','dei.gr','domain/dei.gr','crypto/BTC','nbg.gr/w/64/h/64/icon.png'];
for(const u of urls){const r=await p.evaluate(src=>new Promise(res=>{const i=new Image();i.onload=()=>res('ok '+i.naturalWidth);i.onerror=()=>res('error');i.src=src;setTimeout(()=>res('timeout'),12000)}),'https://cdn.brandfetch.io/'+u+C);console.log(u,'=>',r);}
const r2=await p.request.get('https://cdn.brandfetch.io/apple.com'+C,{headers:{Referer:'https://axiogram.eu/',Accept:'image/avif,image/webp,image/*,*/*'}});console.log('direct',r2.status(),r2.headers()['content-type'],(await r2.text()).slice(0,300).replace(/\s+/g,' '));
await b.close();})();
