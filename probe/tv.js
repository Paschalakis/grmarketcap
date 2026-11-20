const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('https://axiogram.eu/',{waitUntil:'domcontentloaded'});
const d=JSON.parse(fs.readFileSync('probe/grdom.json','utf8'));
const paths=["ticker/AAPL/w/64/h/64/fallback/404/icon.png","ticker/AAPL/fallback/404/icon","ticker/ZZZZQX/fallback/404/icon","ticker/NVDA/fallback/404/icon","ticker/BRK-B/fallback/404/icon","ticker/BRK.B/fallback/404/icon","crypto/BTC/fallback/404/icon"].concat(Object.entries(d).map(([k,v])=>"domain/"+v+"/w/64/h/64/fallback/404/icon.png#"+k));
const res=await p.evaluate(async(paths)=>{const out=[];await Promise.all(paths.map(pth=>new Promise(r=>{const i=new Image();const t=setTimeout(()=>{out.push([pth,'timeout']);r()},15000);i.onload=()=>{clearTimeout(t);out.push([pth,'ok '+i.naturalWidth+'x'+i.naturalHeight]);r()};i.onerror=()=>{clearTimeout(t);out.push([pth,'error']);r()};i.src="https://cdn.brandfetch.io/"+pth.split('#')[0]+"?c=1idw-IXGU7tFB4ds1WN";})));return out;},paths);
res.sort().forEach(r=>console.log(r[0],'=>',r[1]));
// screenshot grid
await p.setContent('<body style="background:#fff;display:flex;flex-wrap:wrap;gap:6px">'+paths.map(x=>'<div style="width:90px;font:10px sans-serif;text-align:center"><img style="width:48px;height:48px;object-fit:contain" src="https://cdn.brandfetch.io/'+x.split('#')[0]+'?c=1idw-IXGU7tFB4ds1WN"><br>'+(x.split('#')[1]||x.slice(0,14))+'</div>').join('')+'</body>');
await p.waitForTimeout(8000);await p.screenshot({path:'probe/grid.png',fullPage:true});
await b.close();})();
