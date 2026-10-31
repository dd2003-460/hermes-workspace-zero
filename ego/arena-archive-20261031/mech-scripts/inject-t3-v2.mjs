import { readFileSync } from 'fs';
const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const text = readFileSync("/tmp/inject-t3r3-p4.txt", "utf8");
const task = await taskSpace("inject-t3v2-" + sid.slice(0,8));
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
const box = await page.evaluate(() => {
  const ed = document.querySelector('.tiptap.ProseMirror');
  if (!ed) return null;
  const r = ed.getBoundingClientRect();
  return { x: r.x + r.width/2, y: r.y + r.height/2 };
});
if (!box) { console.log('NO EDITOR'); await task.finish({ keep: [] }); process.exit(1); }
await page.mouse.click(box.x, box.y, { label: 'focus editor' });
await new Promise(p => setTimeout(p, 800));
await page.keyboard.type(text, { delay: 3 });
await new Promise(p => setTimeout(p, 1500));
const len = await page.evaluate(() => document.querySelector('.tiptap.ProseMirror').textContent.length);
console.log('typed:', len);
if (len < 100) { console.log('FAILED'); await task.finish({ keep: [] }); process.exit(1); }
await page.keyboard.press('Enter');
// 等 25s 看是否开始生成
await new Promise(p => setTimeout(p, 25000));
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  const nLead = body.split('Lead 续推指令').length - 1;
  return { generating: hasStop, leadCount: nLead, tail: body.slice(-300) };
});
console.log('after:', JSON.stringify(st));
await task.finish({ keep: [] });
