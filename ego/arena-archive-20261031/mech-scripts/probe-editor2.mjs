const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("probe-editor2");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
// 滚动到底部，等输入区渲染
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await new Promise(p => setTimeout(p, 3000));
const info = await page.evaluate(() => {
  const eds = [...document.querySelectorAll('.tiptap, .ProseMirror, [contenteditable="true"]')].map(el => {
    const r = el.getBoundingClientRect();
    return { cls: (el.className||'').slice(0,50), rect: [r.x|0, r.y|0, r.width|0, r.height|0], visible: r.width > 0 };
  });
  // "继续工作"按钮是否还在
  const contBtn = [...document.querySelectorAll('button')].find(b => b.innerText.trim() === '继续工作');
  let cr = null;
  if (contBtn) { const r = contBtn.getBoundingClientRect(); cr = [r.x|0, r.y|0]; }
  return { editors: eds, contBtn: cr };
});
console.log(JSON.stringify(info, null, 1));
if (info.contBtn) {
  // 点它，看编辑器是否出现
  await page.mouse.click(info.contBtn[0] + 363, info.contBtn[1] + 22, { label: 'click 继续工作' });
  await new Promise(p => setTimeout(p, 8000));
  const after = await page.evaluate(() => {
    const eds = [...document.querySelectorAll('.tiptap, .ProseMirror, [contenteditable="true"]')].filter(el => {
      const r = el.getBoundingClientRect(); return r.width > 0;
    }).map(el => { const r = el.getBoundingClientRect(); return [r.x|0, r.y|0, r.width|0, r.height|0]; });
    return { visibleEditors: eds };
  });
  console.log('after click:', JSON.stringify(after));
}
await task.finish({ keep: [] });
