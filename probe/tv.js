const {chromium,devices}=require('playwright');
const PF=[{id:'a',side:'buy',sym:'ΔΕΗ',qty:150,price:11.2,date:'2025-02-12',ts:1},{id:'b',side:'buy',sym:'ΕΤΕ',qty:300,price:7.85,date:'2025-05-07',ts:2},{id:'c',side:'buy',sym:'ΜΠΕΛΑ',qty:60,price:26,date:'2025-06-01',ts:3},{id:'d',side:'buy',sym:'f:NVDA',qty:8,price:110,date:'2025-03-05',ts:4,m:{s:'NVDA',n:'NVIDIA',cur:'USD'}},{id:'e',side:'buy',sym:'f:AAPL',qty:5,price:190,date:'2025-01-03',ts:5,m:{s:'AAPL',n:'Apple',cur:'USD'}},{id:'f',side:'buy',sym:'c:bitcoin',qty:0.02,price:62000,date:'2025-03-03',ts:6,m:{s:'BTC',n:'Bitcoin'}},{id:'g',side:'buy',sym:'c:ethereum',qty:0.5,price:2400,date:'2025-04-12',ts:7,m:{s:'ETH',n:'Ethereum'}}];
(async()=>{const b=await chromium.launch({args:['--disable-blink-features=AutomationControlled']});
for(const [n,dev] of [['phone',devices['iPhone 15 Pro']],['tablet',devices['iPad Pro 11']]]){
 const c=await b.newContext({...dev});
 const p=await c.newPage();
 await p.addInitScript(pf=>{if(!sessionStorage.getItem('i')){sessionStorage.setItem('i',1);localStorage.setItem('agora-lang','el');localStorage.setItem('agora-portfolio',JSON.stringify(pf));localStorage.setItem('agora-favs',JSON.stringify(['ΔΕΗ','ΟΤΕ','f:NVDA','c:bitcoin']));}},PF);
 await p.goto('https://axiogram.eu/?shot='+Date.now(),{waitUntil:'domcontentloaded'});await p.waitForTimeout(9000);
 const shot=async(name)=>{await p.waitForTimeout(1800);await p.screenshot({path:'probe/sh_'+n+'_'+name+'.png'});};
 await p.evaluate(()=>window.scrollTo(0,0));await shot('1_markets');
 await p.evaluate(()=>{const e=document.getElementById('secsec');e&&e.scrollIntoView();window.scrollBy(0,-20)});await shot('2_sectors');
 await p.evaluate(()=>{const e=document.getElementById('allsec');e&&e.scrollIntoView();window.scrollBy(0,-20)});await shot('3_allstocks');
 await p.evaluate(()=>window.scrollTo(0,0));await p.click('#gsBtn');await p.waitForTimeout(600);await p.fill('#gsQ','nv');await shot('4_search');
 await p.keyboard.press('Escape');await p.waitForTimeout(400);
 await p.evaluate(()=>{const e=document.getElementById('allsec');e&&e.scrollIntoView()});await p.waitForTimeout(500);await p.click('#rows tr >> nth=0');await p.waitForTimeout(5000);await shot('5_stock');
 await p.keyboard.press('Escape');await p.evaluate(()=>{const c=document.querySelector('#drawer .close,#closeDrawer,#dclose');if(c)c.click();});await p.waitForTimeout(600);
 await p.evaluate(()=>window.scrollTo(0,0));await p.click('.cat[data-cat="pf"]');await p.waitForTimeout(3500);await p.evaluate(()=>window.scrollTo(0,0));await shot('6_portfolio');
 await p.evaluate(()=>window.scrollTo(0,700));await shot('7_portfolio2');
 await p.evaluate(()=>window.scrollTo(0,0));await p.click('.cat[data-cat="mk"]');await p.waitForTimeout(800);await p.click('#mktsw [data-mkt="c"]');await p.waitForTimeout(3000);await p.evaluate(()=>{const e=document.getElementById('allsec');e&&e.scrollIntoView();window.scrollBy(0,-120)});await shot('8_crypto');
 await p.click('#mktsw [data-mkt="gr"]').catch(()=>{});await p.evaluate(()=>window.scrollTo(0,0));await p.click('#tab-tools');await p.waitForTimeout(3000);await shot('9_tools');
 await c.close();}
await b.close();})();
