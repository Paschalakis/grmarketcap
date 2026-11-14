const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1366, height: 950 } });
  const logs = [];
  p.on('pageerror', e => logs.push('pageerror: ' + e.message));
  p.on('response', r => { if (/coingecko/.test(r.url())) logs.push('cg ' + r.status() + ' ' + r.url().slice(0, 90)); });
  await p.goto('https://paschalakis.github.io/grmarketcap/?v=' + Date.now(), { waitUntil: 'load' });
  await p.waitForTimeout(3000);
  await p.click('#mktsw [data-mkt="us"]'); await p.waitForTimeout(2500);
  console.log('US rows', await p.locator('#xrows tr').count(), (await p.locator('#xrows tr').first().innerText()).replace(/\s+/g, ' '));
  await p.screenshot({ path: 'probe/x_us.png' });
  await p.click('#mktsw [data-mkt="c"]'); await p.waitForTimeout(6000);
  console.log('C rows', await p.locator('#xrows tr').count(), (await p.locator('#xrows tr').first().innerText().catch(() => '-')).replace(/\s+/g, ' '), '|', await p.locator('#xempty').innerText().catch(() => ''));
  await p.screenshot({ path: 'probe/x_c.png' });
  console.log(logs.join('\n'));
  await b.close();
})();
