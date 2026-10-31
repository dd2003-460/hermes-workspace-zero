import { readFileSync } from 'fs';
const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const text = readFileSync("/tmp/inject-t3r3-p4.txt", "utf8");
const task = await taskSpace("inject7-" + sid.slice(0,8));
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
// 组合：先 setter+input 事件填值（让 React state 有内容），再 focus + Enter 真实按键
const filled = await page.evaluate((msg) => {
  const ta = document.querySelector('textarea');
  if (!ta) return { ok: false };
  const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
  setter.call(ta, msg);
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  ta.focus();
  return { ok: true, len: ta.value.length };
}, text);
console.log('fill:', JSON.stringify(filled));
if (!filled.ok) { await task.finish({ keep: [] }); process.exit(1); }
await new Promise(r => setTimeout(r, 1000));
// 真实 Enter（CDP keydown，React onSubmit 应捕获）
await page.keyboard.press('Enter');
await new Promise(r => setTimeout(r, 15000));
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  const ta = document.querySelector('textarea');
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  // 检查是否出现新消息（Lead 指令文本出现在正文里）
  const inBody = body.includes('Lead 续推指令 · 2026-10-31');
  return { taLen: ta ? ta.value.length : null, generating: hasStop, inBody, tail: body.slice(-200) };
});
console.log('after:', JSON.stringify(st));
await task.finish({ keep: [] });
