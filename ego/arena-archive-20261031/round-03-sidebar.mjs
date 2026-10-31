const task = await taskSpace("arena-sidebar");
const page = task.page("p1");
await page.goto("https://arena.ai/agent", { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
// 点 Toggle Sidebar / Expand sidebar
const clicked = await page.evaluate(() => {
  const btns = [...document.querySelectorAll('button')];
  for (const b of btns) {
    const l = (b.getAttribute('aria-label') || '') + ' ' + (b.innerText || '');
    if (/Toggle Sidebar|Expand sidebar/i.test(l)) { b.click(); return l.trim(); }
  }
  return null;
});
console.log('clicked:', clicked);
await new Promise(r => setTimeout(r, 8000));
const info = await page.evaluate(() => {
  const body = document.body.innerText;
  const as = [...document.querySelectorAll('a')].map(a => ({ t: a.innerText.slice(0,60).replace(/\n/g,' '), h: a.href })).filter(x => x.h.includes('/agent/') || x.t);
  return { nLinks: as.length, links: as.slice(0, 60), bodyLen: body.length };
});
console.log(JSON.stringify(info, null, 2));
await task.finish({ keep: [] });
