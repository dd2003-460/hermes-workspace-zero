import { writeFileSync } from 'fs';
const task = await taskSpace("arena-scroll-deep");
const page = task.page("p1");
await page.goto("https://arena.ai/agent", { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 15000));
let opened = false;
for (let attempt = 0; attempt < 3 && !opened; attempt++) {
  await page.evaluate(() => {
    for (const b of document.querySelectorAll('button')) {
      const l = ((b.getAttribute('aria-label') || '') + ' ' + (b.innerText || '')).trim();
      if (/Toggle Sidebar/i.test(l)) b.click();
    }
  });
  await new Promise(r => setTimeout(r, 8000));
  opened = (await page.evaluate(() => document.querySelectorAll('a[href*="/agent/"]').length)) > 10;
}
if (!opened) { console.log('sidebar failed'); await task.finish({ keep: [] }); process.exit(1); }
// 深滚：每轮滚动后等待，直到连续 10 轮无增长
let prev = 0, stable = 0;
for (let i = 0; i < 80; i++) {
  await page.evaluate(() => {
    for (const c of document.querySelectorAll('div,nav,aside,ul')) {
      if (c.scrollHeight > c.clientHeight + 50) c.scrollTop = c.scrollHeight;
    }
  });
  await new Promise(r => setTimeout(r, 2000));
  const now = await page.evaluate(() => {
    const seen = new Set();
    for (const a of document.querySelectorAll('a[href*="/agent/"]')) seen.add(a.href.split('?')[0]);
    return seen.size;
  });
  if (now === prev) stable++; else stable = 0;
  if (stable >= 10) break;
  prev = now;
  if (i % 10 === 0) console.log(`scroll ${i}: total=${now}`);
}
const all = await page.evaluate(() => {
  const seen = new Set(); const out = [];
  for (const a of document.querySelectorAll('a[href*="/agent/"]')) {
    const h = a.href.split('?')[0];
    if (!seen.has(h)) { seen.add(h); out.push({ t: a.innerText.slice(0,120).replace(/\n/g,' '), h }); }
  }
  return out;
});
writeFileSync('/Users/a1-6/Desktop/workspace/ego/arena-archive-20261031/session-links.json', JSON.stringify(all, null, 2));
console.log('TOTAL:', all.length);
await task.finish({ keep: [] });
