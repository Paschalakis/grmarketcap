const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch({args:['--disable-blink-features=AutomationControlled']});
const c=await b.newContext({userAgent:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'});
const p=await c.newPage();await p.goto('https://axiogram.eu/',{waitUntil:'domcontentloaded'});
const C='?c=1idw-IXGU7tFB4ds1WN';const d=JSON.parse(fs.readFileSync('probe/grdom.json','utf8'));
const tests=[['T','ticker/AAPL/w/64/h/64/fallback/404/icon'],['T2','ticker/AAPL/fallback/404/w/64/h/64/icon'],['Z','ticker/ZZZZQX/w/64/h/64/fallback/404/icon'],['Z2','domain/zzzqqqxx-nonexist.gr/w/64/h/64/fallback/404/icon'],['BRK-B','ticker/BRK-B/w/64/h/64/fallback/404/icon'],['BRK.B','ticker/BRK.B/w/64/h/64/fallback/404/icon'],['BTC','crypto/BTC/w/64/h/64/fallback/404/icon']].concat(Object.entries(d).map(([k,v])=>[k,'domain/'+v+'/w/64/h/64/fallback/404/icon']));
const out={};
for(const [k,u] of tests){out[k]=await p.evaluate(src=>new Promise(res=>{const i=new Image();i.onload=()=>res('ok '+i.naturalWidth+'x'+i.naturalHeight);i.onerror=()=>res('error');i.src=src;setTimeout(()=>res('timeout'),12000)}),'https://cdn.brandfetch.io/'+u+C);console.log(k,u,'=>',out[k]);}
await p.evaluate(([tests,C])=>{document.open();document.write('<body style="background:#fff;display:flex;flex-wrap:wrap;gap:4px;margin:8px">'+tests.map(t=>'<div style="width:84px;font:10px sans-serif;text-align:center"><img style="width:48px;height:48px;object-fit:contain;background:#eee" src="https://cdn.brandfetch.io/'+t[1]+C+'"><br>'+t[0]+'</div>').join('')+'</body>');document.close();},[tests,C]);
await p.waitForTimeout(6000);await p.screenshot({path:'probe/grid.png',fullPage:true});
await b.close();})();
