const task = await taskSpace("arena-full-list");
const page = task.page("p1");
await page.goto("https://arena.ai/agent", { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 10000));
// 确保侧边栏展开
await page.evaluate(() => {
  const btns = [...document.querySelectorAll('button')];
  for (const b of btns) {
    const l = (b.getAttribute('aria-label') || '') + ' ' + (b.innerText || '');
    if (/Toggle Sidebar|Expand sidebar/i.test(l)) { b.click(); return; }
  }
});
await new Promise(r => setTimeout(r, 8000));
// 收集全部会话链接（去重）
let all = await page.evaluate(() => {
  const seen = new Set();
  const out = [];
  for (const a of document.querySelectorAll('a[href*="/agent/"]')) {
    const h = a.href.split('?')[0];
    if (!seen.has(h)) { seen.add(h); out.push({ t: a.innerText.slice(0,100).replace(/\n/g,' '), h }); }
  }
  return out;
});
console.log('first pass:', all.length);
// 尝试滚动侧边栏加载更多历史
for (let i = 0; i < 6; i++) {
  const grew = await page.evaluate(() => {
    // 找可滚动的侧边栏容器
    const cands = [...document.querySelectorAll('div,nav,aside')].filter(el => el.scrollHeight > el.clientHeight + 50 && el.clientWidth < 500);
    let n = 0;
    for (const c of cands) { c.scrollTop = c.scrollHeight; n++; }
    return n;
  });
  await new Promise(r => setTimeout(r, 3500));
  const now = await page.evaluate(() => {
    const seen = new Set();
    for (const a of document.querySelectorAll('a[href*="/agent/"]')) { seen.add(a.href.split('?')[0]); }
    return seen.size;
  });
  console.log(`scroll ${i}: containers=${grew} total=${now}`);
  if (now === all.length) break;
  all = await page.evaluate(() => {
    const seen = new Set();
    const out = [];
    for (const a of document.querySelectorAll('a[href*="/agent/"]')) {
      const h = a.href.split('?')[0];
      if (!seen.has(h)) { seen.add(h); out.push({ t: a.innerText.slice(0,100).replace(/\n/g,' '), h }); }
    }
    return out;
  });
}
require('fs').writeFileSync('/Users/a1-6/Desktop/workspace/ego/arena-archive-20261031/session-links.json', JSON.stringify(all, null, 2));
console.log('TOTAL:', all.length);
await task.finish({ keep: [] });
