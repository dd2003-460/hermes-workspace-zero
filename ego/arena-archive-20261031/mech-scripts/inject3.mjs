import { readFileSync } from 'fs';
const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const text = readFileSync("/tmp/inject-t3r3-p4.txt", "utf8");
const task = await taskSpace("inject3-" + sid.slice(0,8));
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
// 探查输入区 DOM：textarea 附近有什么按钮
const probe = await page.evaluate(() => {
  const ta = document.querySelector('textarea');
  if (!ta) return { err: 'no textarea' };
  // 向上找容器，收集容器内所有 button/svg
  let container = ta;
  for (let i = 0; i < 5 && container.parentElement; i++) container = container.parentElement;
  const btns = [...container.querySelectorAll('button')].map(b => ({
    aria: b.getAttribute('aria-label'), cls: (b.className||'').slice(0,60), txt: (b.innerText||'').slice(0,30), disabled: b.disabled
  }));
  const svgs = container.querySelectorAll('svg').length;
  return { btns, svgs, containerTag: container.tagName, containerCls: (container.className||'').slice(0,80) };
});
console.log(JSON.stringify(probe, null, 2));
await task.finish({ keep: [] });
