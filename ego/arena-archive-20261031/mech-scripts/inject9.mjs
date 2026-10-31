import { readFileSync } from 'fs';
const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const text = readFileSync("/tmp/inject-t3r3-p4.txt", "utf8");
const task = await taskSpace("inject9-" + sid.slice(0,8));
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
// 定位 textarea 的屏幕坐标
const box = await page.evaluate(() => {
  const ta = document.querySelector('textarea');
  if (!ta) return null;
  const r = ta.getBoundingClientRect();
  return { x: r.x + r.width/2, y: r.y + r.height/2, w: r.width, h: r.height };
});
console.log('box:', JSON.stringify(box));
if (!box) { await task.finish({ keep: [] }); process.exit(1); }
// 真实鼠标点击聚焦 → CDP 真实键盘输入
await page.mouse.click(box.x, box.y, { label: 'focus chat input' });
await new Promise(r => setTimeout(r, 800));
await page.keyboard.type(text, { delay: 5 });
await new Promise(r => setTimeout(r, 1500));
const len = await page.evaluate(() => document.querySelector('textarea').value.length);
console.log('typed len:', len);
if (len < 100) { console.log('STILL FAILED'); await task.finish({ keep: [] }); process.exit(1); }
await page.keyboard.press('Enter');
await new Promise(r => setTimeout(r, 15000));
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  const ta = document.querySelector('textarea');
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  return { taLen: ta ? ta.value.length : null, generating: hasStop, inBody: body.includes('Lead 续推指令'), tail: body.slice(-200) };
});
console.log('after:', JSON.stringify(st));
await task.finish({ keep: [] });
