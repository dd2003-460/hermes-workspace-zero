const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("probe-modal");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
const r = await page.evaluate(() => {
  const b = [...document.querySelectorAll('button')].find(x => x.innerText.trim() === '继续工作');
  if (!b) return null;
  const rect = b.getBoundingClientRect();
  return { x: rect.x + rect.width/2, y: rect.y + rect.height/2 };
});
if (r) {
  await page.mouse.click(r.x, r.y, { label: 'click 继续工作' });
  await new Promise(p => setTimeout(p, 5000));
}
// 全页扫描：任何含"输入/描述/指令/prompt"的可见元素，以及新出现的 dialog/modal
const info = await page.evaluate(() => {
  const dialogs = [...document.querySelectorAll('[role="dialog"], [role="alertdialog"], .modal, [class*="modal"], [class*="Modal"]')].map(d => {
    const rr = d.getBoundingClientRect();
    return { cls: (d.className||'').slice(0,60), visible: rr.width > 0, txt: (d.innerText||'').slice(0,150) };
  }).filter(d => d.visible);
  // 所有 placeholder 含中文的 input-like
  const phs = [...document.querySelectorAll('[placeholder]')].map(el => ({ tag: el.tagName, ph: el.placeholder.slice(0,50), id: el.id })).filter(x => !/recaptcha|goog/.test(x.id));
  return { dialogs, placeholders: phs };
});
console.log(JSON.stringify(info, null, 2));
await task.finish({ keep: [] });
