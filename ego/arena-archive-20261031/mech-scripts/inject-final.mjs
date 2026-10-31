import { readFileSync } from 'fs';
const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const text = readFileSync("/tmp/inject-t3r3-p4.txt", "utf8");
const task = await taskSpace("inject-final-" + sid.slice(0,8));
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
// 找 tiptap 编辑器（ProseMirror contenteditable）
const box = await page.evaluate(() => {
  const ed = document.querySelector('.tiptap.ProseMirror');
  if (!ed) return null;
  const r = ed.getBoundingClientRect();
  return { x: r.x + r.width/2, y: r.y + r.height/2 };
});
console.log('editor box:', JSON.stringify(box));
if (!box) { await task.finish({ keep: [] }); process.exit(1); }
// 真实点击聚焦 → CDP 键盘输入
await page.mouse.click(box.x, box.y, { label: 'focus tiptap editor' });
await new Promise(p => setTimeout(p, 800));
await page.keyboard.type(text, { delay: 3 });
await new Promise(p => setTimeout(p, 1500));
const len = await page.evaluate(() => document.querySelector('.tiptap.ProseMirror').textContent.length);
console.log('typed len:', len);
if (len < 100) { console.log('TYPE FAILED'); await task.finish({ keep: [] }); process.exit(1); }
// Enter 发送
await page.keyboard.press('Enter');
await new Promise(p => setTimeout(p, 15000));
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  const ed = document.querySelector('.tiptap.ProseMirror');
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  return { edLen: ed ? ed.textContent.length : null, generating: hasStop, inBody: body.includes('Lead 续推指令'), tail: body.slice(-200) };
});
console.log('after:', JSON.stringify(st));
await task.finish({ keep: [] });
