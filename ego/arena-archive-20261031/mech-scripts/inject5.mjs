import { readFileSync } from 'fs';
const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const text = readFileSync("/tmp/inject-t3r3-p4.txt", "utf8");
const task = await taskSpace("inject5-" + sid.slice(0,8));
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
// 用 CDP 级真实输入：先聚焦，再逐字符走 keyboard（ego-browser 的 page 底层是 playwright-like）
const filled = await page.evaluate((msg) => {
  const ta = document.querySelector('textarea');
  if (!ta) return { ok: false };
  ta.focus();
  const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
  setter.call(ta, msg);
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  return { ok: true, len: ta.value.length };
}, text);
console.log('fill:', JSON.stringify(filled));
await new Promise(r => setTimeout(r, 1000));
// 检查 textarea 同级/父级的 svg 按钮（发送键通常是纸飞机 svg）
const clicked = await page.evaluate(() => {
  const ta = document.querySelector('textarea');
  let el = ta.parentElement;
  for (let i = 0; i < 3 && el; i++) {
    const btns = [...el.querySelectorAll('button')];
    // 取最靠右的、非 disabled 的 button（发送键一般在输入框右侧）
    const rects = btns.map(b => ({ b, r: b.getBoundingClientRect() })).filter(x => x.r.width > 0 && !x.b.disabled);
    if (rects.length) {
      rects.sort((a, c) => c.r.x - a.r.x);
      const target = rects[0];
      console.log && 0;
      target.b.click();
      return { x: target.r.x, aria: target.b.getAttribute('aria-label'), cls: (target.b.className||'').slice(0,40) };
    }
    el = el.parentElement;
  }
  return null;
});
console.log('clicked rightmost btn:', JSON.stringify(clicked));
await new Promise(r => setTimeout(r, 12000));
const after = page.evaluate ? null : null;
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  const ta = document.querySelector('textarea');
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  return { taCleared: ta ? ta.value === '' : null, generating: hasStop, tail: body.slice(-250) };
});
console.log('after:', JSON.stringify(st));
await task.finish({ keep: [] });
