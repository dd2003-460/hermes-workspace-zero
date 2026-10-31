import { readFileSync } from 'fs';
const sid = "01a1840f-b471-7f18-b90d-cb5fe174c209";
const text = readFileSync("/tmp/inject-t4r1-s03.txt", "utf8");
const task = await taskSpace("inject-t4-" + sid.slice(0,8));
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
// 点"继续工作"唤出编辑器（若存在）
const cr = await page.evaluate(() => {
  const b = [...document.querySelectorAll('button')].find(x => x.innerText.trim() === '继续工作');
  if (!b) return null;
  const r = b.getBoundingClientRect();
  return { x: r.x + r.width/2, y: r.y + r.height/2 };
});
if (cr) {
  await page.mouse.click(cr.x, cr.y, { label: 'click 继续工作 to open editor' });
  await new Promise(p => setTimeout(p, 6000));
}
const box = await page.evaluate(() => {
  const ed = [...document.querySelectorAll('.tiptap, .ProseMirror, [contenteditable="true"]')].find(el => el.getBoundingClientRect().width > 0);
  if (!ed) return null;
  const r = ed.getBoundingClientRect();
  return { x: r.x + r.width/2, y: r.y + r.height/2 };
});
console.log('editor:', JSON.stringify(box));
if (!box) { console.log('NO EDITOR'); await task.finish({ keep: [] }); process.exit(1); }
await page.mouse.click(box.x, box.y, { label: 'focus editor' });
await new Promise(p => setTimeout(p, 800));
await page.keyboard.type(text, { delay: 3 });
await new Promise(p => setTimeout(p, 1500));
const len = await page.evaluate(() => {
  const ed = [...document.querySelectorAll('.tiptap, .ProseMirror, [contenteditable="true"]')].find(el => el.getBoundingClientRect().width > 0);
  return ed ? ed.textContent.length : -1;
});
console.log('typed:', len);
if (len < 100) { console.log('FAILED'); await task.finish({ keep: [] }); process.exit(1); }
await page.keyboard.press('Enter');
await new Promise(p => setTimeout(p, 30000));
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  const nLead = body.split('Lead 续推指令').length - 1;
  return { generating: hasStop, leadCount: nLead, tail: body.slice(-300) };
});
console.log('after:', JSON.stringify(st));
await task.finish({ keep: [] });
