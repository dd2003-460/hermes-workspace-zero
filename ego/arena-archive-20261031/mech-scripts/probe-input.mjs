const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("probe-input");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 15000));
const info = await page.evaluate(() => {
  const out = [];
  for (const el of document.querySelectorAll('textarea, input[type="text"], [contenteditable]')) {
    if (el.id === 'g-recaptcha-response-100000') continue;
    const r = el.getBoundingClientRect();
    out.push({ tag: el.tagName, id: el.id, ph: el.placeholder || el.getAttribute('data-placeholder') || '', rect: [r.x|0, r.y|0, r.width|0, r.height|0] });
  }
  // 底部区域的所有可交互元素
  const bottom = [...document.querySelectorAll('button, [role="textbox"], div[tabindex]')].filter(el => {
    const r = el.getBoundingClientRect();
    return r.y > 600 && r.width > 0;
  }).map(el => ({ tag: el.tagName, role: el.getAttribute('role'), aria: el.getAttribute('aria-label'), txt: (el.innerText||'').slice(0,30), y: el.getBoundingClientRect().y|0 }));
  return { inputs: out, bottomEls: bottom.slice(0, 20) };
});
console.log(JSON.stringify(info, null, 2));
await task.finish({ keep: [] });
