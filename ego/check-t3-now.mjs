const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("check-t3-now");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  // 找最后一条 agent 消息（Lead 指令之后的内容）
  const idx = body.lastIndexOf('Lead 续推指令');
  const after = idx >= 0 ? body.slice(idx + 10, idx + 1500) : null;
  return { generating: hasStop, len: body.length, after };
});
console.log(JSON.stringify(st, null, 1).slice(0, 2500));
await task.finish({ keep: [] });
