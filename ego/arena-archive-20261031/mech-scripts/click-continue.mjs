const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("click-continue");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 15000));
// 点"继续工作"按钮（真实鼠标点击）
const r = await page.evaluate(() => {
  const b = [...document.querySelectorAll('button')].find(x => x.innerText.trim() === '继续工作');
  if (!b) return null;
  const rect = b.getBoundingClientRect();
  return { x: rect.x + rect.width/2, y: rect.y + rect.height/2 };
});
console.log('btn:', JSON.stringify(r));
if (r) {
  await page.mouse.click(r.x, r.y, { label: 'click 继续工作 button' });
  await new Promise(p => setTimeout(p, 10000));
  // 看是否出现输入框或开始生成
  const st = await page.evaluate(() => {
    const tas = [...document.querySelectorAll('textarea')].filter(t => !/recaptcha/.test(t.id)).map(t => {
      const rr = t.getBoundingClientRect(); return [rr.x|0, rr.y|0, rr.width|0, rr.height|0];
    });
    const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
    return { textareas: tas, generating: hasStop, tail: document.body.innerText.slice(-200) };
  });
  console.log('after:', JSON.stringify(st));
}
await task.finish({ keep: [] });
