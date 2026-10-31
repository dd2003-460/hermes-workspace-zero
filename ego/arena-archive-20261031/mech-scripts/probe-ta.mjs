const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("probe-ta");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
const info = await page.evaluate(() => {
  const tas = [...document.querySelectorAll('textarea')].map(ta => {
    const r = ta.getBoundingClientRect();
    return { id: ta.id, name: ta.name, ph: ta.placeholder, cls: (ta.className||'').slice(0,80), rect: [r.x|0, r.y|0, r.width|0, r.height|0], visible: r.width > 0 };
  });
  const editables = [...document.querySelectorAll('[contenteditable="true"]')].map(el => {
    const r = el.getBoundingClientRect();
    return { tag: el.tagName, cls: (el.className||'').slice(0,80), rect: [r.x|0, r.y|0, r.width|0, r.height|0] };
  });
  return { nTextareas: tas.length, tas, editables };
});
console.log(JSON.stringify(info, null, 2));
await task.finish({ keep: [] });
