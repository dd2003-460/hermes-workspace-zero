import { readFileSync } from 'fs';
const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const text = readFileSync("/tmp/inject-t3r3-p4.txt", "utf8");
const task = await taskSpace("inject6-" + sid.slice(0,8));
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
// 真实键盘输入：focus textarea → keyboard.type（走 CDP，React 受控组件可识别）
await page.evaluate(() => document.querySelector('textarea').focus());
await page.keyboard.type(text);
await new Promise(r => setTimeout(r, 1500));
const len = await page.evaluate(() => document.querySelector('textarea').value.length);
console.log('typed, ta len:', len);
if (len < 100) { console.log('TYPE FAILED'); await task.finish({ keep: [] }); process.exit(1); }
// 按 Enter 发送
await page.keyboard.press('Enter');
await new Promise(r => setTimeout(r, 15000));
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  const ta = document.querySelector('textarea');
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  return { taCleared: ta ? ta.value === '' : null, generating: hasStop, tail: body.slice(-250) };
});
console.log('after:', JSON.stringify(st));
await task.finish({ keep: [] });
