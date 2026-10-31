const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("probe-input3");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 15000));
// 滚动到底部，看输入框是否懒加载
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await new Promise(r => setTimeout(r, 3000));
const info = await page.evaluate(() => {
  const out = [];
  for (const el of document.querySelectorAll('textarea, input[type="text"], [contenteditable]')) {
    if (/recaptcha|goog-gt/.test(el.id)) continue;
    const r = el.getBoundingClientRect();
    out.push({ tag: el.tagName, id: el.id, ph: el.placeholder || '', rect: [r.x|0, r.y|0, r.width|0, r.height|0] });
  }
  // 找 "继续工作" 按钮位置
  const contBtn = [...document.querySelectorAll('button')].find(b => b.innerText.trim() === '继续工作');
  const cr = contBtn ? contBtn.getBoundingClientRect() : null;
  return { n: out.length, inputs: out, contBtn: cr ? [cr.x|0, cr.y|0, cr.width|0, cr.height|0] : null };
});
console.log(JSON.stringify(info, null, 2));
await task.finish({ keep: [] });
