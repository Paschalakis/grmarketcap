const {chromium,devices}=require('playwright');
(async()=>{const b=await chromium.launch();
for(const [n,o] of [['d',{viewport:{width:1366,height:900},deviceScaleFactor:1}],['m',devices['iPhone 13']]]){
const c=await b.newContext(o);const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.addInitScript(()=>localStorage.setItem('agora-lang','el'));
await p.goto('https://axiogram.eu/?v='+Date.now(),{waitUntil:'domcontentloaded'});await p.waitForTimeout(5000);
await p.click('#mktsw [data-mkt="c"]');await p.waitForTimeout(6000);
console.log(n,await p.textContent('#xtitle'),'|',await p.textContent('#xnote'));
console.log(n,'rows',await p.locator('#xrows tr').count(),'logos',await p.evaluate(()=>[...document.querySelectorAll('#xrows img')].filter(i=>i.complete&&i.naturalWidth>0).length),'spark',await p.locator('#xrows svg').count());
console.log(n,'first',(await p.locator('#xrows tr').first().innerText()).replace(/\s+/g,' ').slice(0,120));
console.log(n,'cstats',(await p.textContent('#cstats')).replace(/\s+/g,' ').slice(0,160));
await p.screenshot({path:'probe/cmc_'+n+'.png'});console.log(n,'errors',errs);await c.close();}
await b.close();})();
