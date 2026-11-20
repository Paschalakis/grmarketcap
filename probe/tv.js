const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--disable-blink-features=AutomationControlled']});
for(const [n,vp] of [['d',{width:1366,height:900}],['m',{width:390,height:844}]]){
const c=await b.newContext({viewport:vp,deviceScaleFactor:2,userAgent:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'});
const p=await c.newPage();await p.goto('https://axiogram.eu/?v='+Date.now(),{waitUntil:'domcontentloaded'});await p.waitForTimeout(6000);
await p.locator('#allsec').scrollIntoViewIfNeeded();await p.waitForTimeout(3000);
console.log(n,'logos loaded',await p.evaluate(()=>[...document.querySelectorAll('.mono.haslogo img')].filter(i=>i.complete&&i.naturalWidth>0).length),'mono total',await p.locator('#rows .mono').count());
await p.screenshot({path:'probe/live_'+n+'.png'});
await p.click('#mktsw [data-mkt="us"]');await p.waitForTimeout(4000);await p.locator('#allsec').scrollIntoViewIfNeeded();await p.waitForTimeout(2500);
console.log(n,'us logos',await p.evaluate(()=>[...document.querySelectorAll('#rows .haslogo img')].filter(i=>i.complete&&i.naturalWidth>0).length));
await p.screenshot({path:'probe/live_us_'+n+'.png'});await c.close();}
await b.close();})();
