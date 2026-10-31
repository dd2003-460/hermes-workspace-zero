import { readFileSync } from 'fs';
// 用法: node arena-inject-20261031.mjs <session-id> <text-file>
const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const text = readFileSync("/tmp/inject-t3r3-p4.txt", 'utf8');
const task = await taskSpace("inject-" + sid.slice(0,8));
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
// 找输入框：textarea 或 contenteditable
const info = await page.evaluate((msg) => {
  let ta = document.querySelector('textarea');
  let editable = !ta ? document.querySelector('[contenteditable="true"]') : null;
  const target = ta || editable;
  if (!target) return { ok: false, reason: 'no input found', bodyHead: document.body.innerText.slice(0, 300) };
  // 填内容
  if (ta) {
    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    setter.call(ta, msg);
    ta.dispatchEvent(new Event('input', { bubbles: true }));
  } else {
    target.textContent = msg;
    target.dispatchEvent(new InputEvent('input', { bubbles: true }));
  }
  return { ok: true, tag: ta ? 'textarea' : 'contenteditable', len: msg.length };
}, text);
console.log('fill:', JSON.stringify(info));
if (!info.ok) { await task.finish({ keep: [] }); process.exit(1); }
await new Promise(r => setTimeout(r, 1500));
// 点发送按钮
const sent = await page.evaluate(() => {
  const btns = [...document.querySelectorAll('button')];
  for (const b of btns) {
    const l = ((b.getAttribute('aria-label') || '') + ' ' + (b.innerText || '')).trim();
    if (/send/i.test(l) && !b.disabled) { b.click(); return l; }
  }
  // fallback: Enter key on textarea
  const ta = document.querySelector('textarea');
  if (ta) {
    ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));
    return 'enter-key';
  }
  return null;
});
console.log('send clicked:', sent);
await new Promise(r => setTimeout(r, 8000));
const after = await page.evaluate(() => {
  const body = document.body.innerText;
  const generating = !!document.querySelector('button[aria-label*="Stop" i]') || /generating/i.test(body);
  return { generating, tail: body.slice(-400) };
});
console.log('after:', JSON.stringify(after));
await task.finish({ keep: [] });
