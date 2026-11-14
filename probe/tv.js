const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1366, height: 950 } });
  const logs = [];
  p.on('pageerror', e => logs.push('pageerror: ' + e.message));
  p.on('response', r => { if (/api\.coingecko/.test(r.url())) logs.push('cg ' + r.status() + ' ' + r.url().slice(30, 110)); });
  await p.goto('https://paschalakis.github.io/grmarketcap/?v=' + Date.now(), { waitUntil: 'load' });
  await p.waitForTimeout(3000);
  await p.click('#mktsw [data-mkt="c"]'); await p.waitForTimeout(5000);
  await p.click('#xrows tr:first-child .who'); await p.waitForTimeout(5000);
  console.log('C drawer', await p.textContent('#dname'), '| paths', await p.locator('#xchart path').count(), '| ro', (await p.textContent('#xro').catch(() => '')).trim(), '| msg', await p.locator('#xchart .msg').innerText().catch(() => ''));
  await p.screenshot({ path: 'probe/x_c.png' });
  await p.click('#dclose');
  await p.click('#mktsw [data-mkt="us"]'); await p.waitForTimeout(1500);
  await p.click('#xrows tr:first-child .who'); await p.waitForTimeout(9000);
  const frames = p.frames().filter(f => /tradingview/.test(f.url()));
  console.log('US drawer', await p.textContent('#dname'), '| frames', frames.length, '| box', JSON.stringify(await p.locator('#xtv').boundingBox()));
  for (const f of frames) { try { console.log('frame text:', (await f.locator('body').innerText({ timeout: 5000 })).replace(/\s+/g, ' ').slice(0, 200)); } catch (e) {} }
  await p.screenshot({ path: 'probe/x_us.png' });
  console.log(logs.join('\n'));
  await b.close();
})();
