import { readFileSync } from 'fs';
const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const text = readFileSync("/tmp/inject-t3r3-p4.txt", "utf8");
const task = await taskSpace("inject4-" + sid.slice(0,8));
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
// 精确定位 textarea 的直接父级链上的按钮
const probe = await page.evaluate(() => {
  const ta = document.querySelector('textarea');
  if (!ta) return { err: 'no textarea' };
  const chain = [];
  let el = ta.parentElement;
  for (let i = 0; i < 4 && el; i++) {
    chain.push({
      tag: el.tagName, cls: (el.className||'').slice(0,100),
      nBtn: el.querySelectorAll('button').length,
      btns: [...el.querySelectorAll('button')].slice(0,6).map(b => ({ aria: b.getAttribute('aria-label'), title: b.getAttribute('title'), cls: (b.className||'').slice(0,50) }))
    });
    el = el.parentElement;
  }
  return chain;
});
console.log(JSON.stringify(probe, null, 2));
await task.finish({ keep: [] });
