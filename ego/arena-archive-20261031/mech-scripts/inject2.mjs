import { readFileSync } from 'fs';
const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const text = readFileSync("/tmp/inject-t3r3-p4.txt", "utf8");
const task = await taskSpace("inject2-" + sid.slice(0,8));
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
// 用真实键盘事件填 textarea（React 受控组件需要 beforeinput/input 全链路）
const filled = await page.evaluate((msg) => {
  const ta = document.querySelector('textarea');
  if (!ta) return { ok: false, reason: 'no textarea' };
  ta.focus();
  const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
  setter.call(ta, msg);
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  return { ok: true, len: ta.value.length };
}, text);
console.log('fill:', JSON.stringify(filled));
if (!filled.ok) { await task.finish({ keep: [] }); process.exit(1); }
await new Promise(r => setTimeout(r, 1000));
// 找发送按钮：aria-label 含 Send，或 class 含 send；逐个试
const btnInfo = await page.evaluate(() => {
  const out = [];
  for (const b of document.querySelectorAll('button')) {
    const l = ((b.getAttribute('aria-label') || '') + '|' + (b.className || '')).slice(0, 80);
    if (/send/i.test(l)) out.push({ l, disabled: b.disabled });
  }
  return out;
});
console.log('send buttons:', JSON.stringify(btnInfo));
let sent = null;
for (const b of btnInfo) {
  if (!b.disabled) {
    sent = await page.evaluate((label) => {
      for (const x of document.querySelectorAll('button')) {
        const l = ((x.getAttribute('aria-label') || '') + '|' + (x.className || '')).slice(0, 80);
        if (l === label && !x.disabled) { x.click(); return true; }
      }
      return false;
    }, b.l);
    if (sent) { console.log('clicked:', b.l); break; }
  }
}
if (!sent) {
  // fallback Enter
  sent = await page.evaluate(() => {
    const ta = document.querySelector('textarea');
    if (!ta) return false;
    ta.focus();
    ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
    ta.dispatchEvent(new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
    ta.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
    return true;
  });
  console.log('fallback enter used');
}
await new Promise(r => setTimeout(r, 10000));
const after = await page.evaluate(() => {
  const body = document.body.innerText;
  const ta = document.querySelector('textarea');
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  return { taCleared: ta ? ta.value === '' : null, generating: hasStop, tail: body.slice(-300) };
});
console.log('after:', JSON.stringify(after));
await task.finish({ keep: [] });
