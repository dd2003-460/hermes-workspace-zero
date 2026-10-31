import { readFileSync, writeFileSync } from 'fs';
const task = await taskSpace("arena-scroll-more");
const page = task.page("p1");
await page.goto("https://arena.ai/agent", { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
await page.evaluate(() => {
  for (const b of document.querySelectorAll('button')) {
    const l = ((b.getAttribute('aria-label') || '') + ' ' + (b.innerText || '')).trim();
    if (/sidebar/i.test(l)) b.click();
  }
});
await new Promise(r => setTimeout(r, 8000));
let prev = 0;
for (let i = 0; i < 40; i++) {
  await page.evaluate(() => {
    for (const c of document.querySelectorAll('div,nav,aside,ul')) {
      if (c.scrollHeight > c.clientHeight + 50) c.scrollTop = c.scrollHeight;
    }
  });
  await new Promise(r => setTimeout(r, 2500));
  const now = await page.evaluate(() => {
    const seen = new Set();
    for (const a of document.querySelectorAll('a[href*="/agent/"]')) seen.add(a.href.split('?')[0]);
    return seen.size;
  });
  if (now === prev && i > 3) break;
  prev = now;
}
const all = await page.evaluate(() => {
  const seen = new Set(); const out = [];
  for (const a of document.querySelectorAll('a[href*="/agent/"]')) {
    const h = a.href.split('?')[0];
    if (!seen.has(h)) { seen.add(h); out.push({ t: a.innerText.slice(0,100).replace(/\n/g,' '), h }); }
  }
  return out;
});
writeFileSync('/Users/a1-6/Desktop/workspace/ego/arena-archive-20261031/session-links.json', JSON.stringify(all, null, 2));
console.log('TOTAL:', all.length);
await task.finish({ keep: [] });
