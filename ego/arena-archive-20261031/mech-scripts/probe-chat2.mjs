const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("probe-chat2");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
// 先滚动到底部（输入框可能随滚动出现）
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await new Promise(p => setTimeout(p, 3000));
const info = await page.evaluate(() => {
  const btns = [...document.querySelectorAll('button')].map(b => ({ txt: (b.innerText||'').trim().slice(0,20), aria: b.getAttribute('aria-label') })).filter(x => x.txt || x.aria);
  return { n: btns.length, btns: btns.slice(-30) };
});
console.log(JSON.stringify(info, null, 1));
await task.finish({ keep: [] });
