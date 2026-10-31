import { readFileSync } from 'fs';
const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const text = readFileSync("/tmp/inject-t3r3-p4.txt", "utf8");
const task = await taskSpace("inject8-" + sid.slice(0,8));
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
// 完整合成键盘事件序列（keydown→keypress→keyup，带 keyCode/which，React onKeyDown 依赖这些）
const res = await page.evaluate((msg) => {
  const ta = document.querySelector('textarea');
  if (!ta) return { ok: false };
  const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
  setter.call(ta, msg);
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  ta.focus();
  const opts = { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true };
  ta.dispatchEvent(new KeyboardEvent('keydown', opts));
  ta.dispatchEvent(new KeyboardEvent('keypress', opts));
  ta.dispatchEvent(new KeyboardEvent('keyup', opts));
  // 同时找 form 提交
  const form = ta.closest('form');
  let submitted = false;
  if (form) { form.requestSubmit ? form.requestSubmit() : form.submit(); submitted = true; }
  return { ok: true, hasForm: !!form, submitted, len: ta.value.length };
}, text);
console.log('res:', JSON.stringify(res));
await new Promise(r => setTimeout(r, 15000));
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  const ta = document.querySelector('textarea');
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  return { taLen: ta ? ta.value.length : null, generating: hasStop, inBody: body.includes('Lead 续推指令'), tail: body.slice(-200) };
});
console.log('after:', JSON.stringify(st));
await task.finish({ keep: [] });
