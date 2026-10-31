const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("probe-chat3");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
// 找所有可见的、y 坐标最大的容器（输入区一般在最底部）
const info = await page.evaluate(() => {
  const vh = window.innerHeight;
  const els = [...document.querySelectorAll('div')].filter(el => {
    const r = el.getBoundingClientRect();
    return r.y >= vh - 250 && r.width > 400 && r.height > 30 && r.height < 200;
  }).map(el => ({ cls: (el.className||'').toString().slice(0,70), h: el.getBoundingClientRect().height|0, y: el.getBoundingClientRect().y|0, txt: (el.innerText||'').replace(/\n/g,'|').slice(0,80) }));
  return els.slice(0, 15);
});
console.log(JSON.stringify(info, null, 1));
await task.finish({ keep: [] });
