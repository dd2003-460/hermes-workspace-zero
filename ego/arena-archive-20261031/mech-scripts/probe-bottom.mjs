const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("probe-bottom");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
// 页面底部 300px 内所有可见元素
const info = await page.evaluate(() => {
  const vh = window.innerHeight;
  const els = [...document.querySelectorAll('*')].filter(el => {
    const r = el.getBoundingClientRect();
    return r.y + r.height >= vh - 300 && r.width > 50 && r.height > 20 && el.children.length < 8;
  }).map(el => ({ tag: el.tagName, cls: (el.className||'').toString().slice(0,60), txt: (el.innerText||'').slice(0,60) }));
  // 去重
  const seen = new Set();
  return els.filter(e => { const k = e.tag+e.cls+e.txt; if (seen.has(k)) return false; seen.add(k); return true; }).slice(0, 25);
});
console.log(JSON.stringify(info, null, 2));
await task.finish({ keep: [] });
