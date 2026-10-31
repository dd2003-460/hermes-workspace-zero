const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("probe-input2");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 15000));
const info = await page.evaluate(() => {
  const out = [];
  for (const el of document.querySelectorAll('textarea, input[type="text"], [contenteditable]')) {
    if (el.id === 'g-recaptcha-response-100000') continue;
    const r = el.getBoundingClientRect();
    out.push({ tag: el.tagName, id: el.id, ph: el.placeholder || '', rect: [r.x|0, r.y|0, r.width|0, r.height|0] });
  }
  return { n: out.length, inputs: out };
});
console.log(JSON.stringify(info, null, 2));
await task.finish({ keep: [] });
