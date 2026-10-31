const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("check-" + sid.slice(0,8));
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
const info = await page.evaluate(() => {
  const body = document.body.innerText;
  // 找输入框当前内容
  const ta = document.querySelector('textarea');
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  // 最后几条消息的时间戳
  const stamps = [...body.matchAll(/(\d+m \d+s|\d+h \d+m) \| (\d+ days?|yesterday|today) ago/g)].map(m => m[0]).slice(-5);
  return { taValue: ta ? ta.value.slice(0,200) : null, hasStop, stamps, len: body.length };
});
console.log(JSON.stringify(info, null, 2));
await task.finish({ keep: [] });
