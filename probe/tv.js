const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for(const o of [{viewport:{width:1366,height:900}},{viewport:{width:390,height:844},isMobile:true,hasTouch:true,colorScheme:'dark'}]){
const c=await b.newContext(o);const p=await c.newPage();await p.goto('https://axiogram.eu/?x='+Date.now());await p.waitForTimeout(4000);
console.log(o.viewport.width,'data-ui',await p.evaluate(()=>document.documentElement.getAttribute('data-ui')),'theme-mk in page',await p.evaluate(()=>typeof THEME!=='undefined'?THEME:'?'),'bg',await p.evaluate(()=>getComputedStyle(document.body).backgroundColor));
await c.close();}
await b.close();})();
