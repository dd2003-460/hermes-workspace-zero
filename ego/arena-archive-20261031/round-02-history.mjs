const task = await taskSpace("arena-session-history");
const page = task.page("p1");
await page.goto("https://arena.ai/agent", { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
// 找所有可能的入口：历史按钮、侧边栏、菜单
const info = await page.evaluate(() => {
  const btns = [...document.querySelectorAll('button')].map(b => (b.innerText || b.getAttribute('aria-label') || '').slice(0,40)).filter(Boolean);
  const as = [...document.querySelectorAll('a')].map(a => ({ t: a.innerText.slice(0,40).replace(/\n/g,' '), h: a.href })).filter(x => x.t || x.h.includes('agent'));
  return { btns: btns.slice(0,40), links: as.slice(0,40) };
});
console.log(JSON.stringify(info, null, 2));
await task.finish({ keep: [] });
