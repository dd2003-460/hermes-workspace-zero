import { writeFileSync } from 'fs';
const task = await taskSpace("arena-retry-list");
const page = task.page("p1");
await page.goto("https://arena.ai/agent", { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 15000));
// 只点一次 Toggle Sidebar（奇数次点击=展开）
let state = null;
for (let attempt = 0; attempt < 3; attempt++) {
  const n = await page.evaluate(() => {
    let c = 0;
    for (const b of document.querySelectorAll('button')) {
      const l = ((b.getAttribute('aria-label') || '') + ' ' + (b.innerText || '')).trim();
      if (/Toggle Sidebar/i.test(l)) { b.click(); c++; }
    }
    return c;
  });
  console.log(`attempt ${attempt}: toggled ${n}`);
  await new Promise(r => setTimeout(r, 8000));
  const cnt = await page.evaluate(() => document.querySelectorAll('a[href*="/agent/"]').length);
  console.log(`  links now: ${cnt}`);
  if (cnt > 10) { state = 'open'; break; }
}
if (!state) { console.log('FAILED to open sidebar'); await task.finish({ keep: [] }); process.exit(1); }
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
  if (i % 5 === 0) console.log(`scroll ${i}: total=${now}`);
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
