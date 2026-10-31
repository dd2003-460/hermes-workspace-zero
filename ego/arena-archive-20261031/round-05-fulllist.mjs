import { writeFileSync } from 'fs';
const task = await taskSpace("arena-full-list2");
const page = task.page("p1");
await page.goto("https://arena.ai/agent", { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
// 侧边栏：找所有按钮，点含 sidebar 的
const clicked = await page.evaluate(() => {
  const out = [];
  for (const b of document.querySelectorAll('button')) {
    const l = ((b.getAttribute('aria-label') || '') + ' ' + (b.innerText || '')).trim();
    if (/sidebar/i.test(l)) { b.click(); out.push(l); }
  }
  return out;
});
console.log('clicked:', JSON.stringify(clicked));
await new Promise(r => setTimeout(r, 8000));
let all = await page.evaluate(() => {
  const seen = new Set(); const out = [];
  for (const a of document.querySelectorAll('a[href*="/agent/"]')) {
    const h = a.href.split('?')[0];
    if (!seen.has(h)) { seen.add(h); out.push({ t: a.innerText.slice(0,100).replace(/\n/g,' '), h }); }
  }
  return out;
});
console.log('first pass:', all.length);
for (let i = 0; i < 8; i++) {
  const grew = await page.evaluate(() => {
    let n = 0;
    for (const c of document.querySelectorAll('div,nav,aside,ul')) {
      if (c.scrollHeight > c.clientHeight + 50) { c.scrollTop = c.scrollHeight; n++; }
    }
    return n;
  });
  await new Promise(r => setTimeout(r, 3000));
  const now = await page.evaluate(() => {
    const seen = new Set();
    for (const a of document.querySelectorAll('a[href*="/agent/"]')) seen.add(a.href.split('?')[0]);
    return seen.size;
  });
  console.log(`scroll ${i}: scrollables=${grew} total=${now}`);
  if (now === all.length && i > 1) break;
  all = await page.evaluate(() => {
    const seen = new Set(); const out = [];
    for (const a of document.querySelectorAll('a[href*="/agent/"]')) {
      const h = a.href.split('?')[0];
      if (!seen.has(h)) { seen.add(h); out.push({ t: a.innerText.slice(0,100).replace(/\n/g,' '), h }); }
    }
    return out;
  });
}
writeFileSync('/Users/a1-6/Desktop/workspace/ego/arena-archive-20261031/session-links.json', JSON.stringify(all, null, 2));
console.log('TOTAL:', all.length);
await task.finish({ keep: [] });
