const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const MOB = process.env.MOB === '1';
  const p = await b.newPage({ viewport: MOB ? { width: 390, height: 844 } : { width: 1366, height: 950 } });
  const logs = [];
  p.on('console', m => { if (m.type() === 'error') logs.push('console: ' + m.text().slice(0, 300)); });
  p.on('pageerror', e => logs.push('pageerror: ' + e.message));
  p.on('requestfailed', r => { if (/tradingview/.test(r.url())) logs.push('failed: ' + r.url().slice(0, 200) + ' ' + (r.failure() || {}).errorText); });
  p.on('response', r => { if (/tradingview/.test(r.url()) && r.status() >= 400) logs.push('http ' + r.status() + ' ' + r.url().slice(0, 200)); });
  await p.goto('https://paschalakis.github.io/grmarketcap/?v=' + Date.now(), { waitUntil: 'load' });
  await p.waitForTimeout(4000);
  for (const sym of ['ΕΤΕ']) {
    await p.evaluate(s => { const tr = document.querySelector('#rows tr[data-s="' + s + '"]') || document.querySelector('#rows tr'); tr.click(); }, sym);
    await p.waitForTimeout(800);
    const has = await p.locator('[data-ckind="tv"]').count();
    console.log(sym, 'tv button count', has);
    if (!has) { console.log(await p.locator('.ctool').innerHTML().catch(() => 'no ctool')); continue; }
    await p.click('[data-ckind="tv"]');
    await p.waitForTimeout(9000);
    console.log(sym, 'tvbox html', (await p.locator('#tvbox').innerHTML().catch(() => 'none')).slice(0, 600));
    const frames = p.frames().filter(f => /tradingview/.test(f.url()));
    console.log(sym, 'frames', frames.map(f => f.url().slice(0, 160)));
    for (const f of frames) { try { console.log(sym, 'frame text:', (await f.locator('body').innerText({ timeout: 5000 })).replace(/\s+/g, ' ').slice(0, 400)); } catch (e) { console.log('frame err', e.message.slice(0, 100)); } }
    console.log(sym, 'tvbox size', JSON.stringify(await p.locator('#tvbox').boundingBox()));
    await p.screenshot({ path: 'probe/tv_' + (sym === 'ΕΤΕ' ? 'ete' : 'dei') + (MOB ? '_m' : '') + '.png' });
    await p.evaluate(() => { const c = document.getElementById('dclose'); if (c) c.click(); });
    await p.waitForTimeout(500);
  }
  console.log(logs.slice(0, 30).join('\n'));
  await b.close();
})();
