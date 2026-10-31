const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("check-sent");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  // 找 Lead 续推指令出现的位置和上下文
  const idx = body.indexOf('Lead 续推指令');
  const ctx = idx >= 0 ? body.slice(Math.max(0,idx-100), idx+300) : null;
  // 消息时间戳（最后几条）
  const stamps = [...body.matchAll(/(\d+m \d+s|\d+h \d+m|\d+d) \| (yesterday|today|\d+ days? ago)/g)].map(m => m[0]).slice(-8);
  // 是否有 Stop 按钮（生成中）
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  return { found: idx >= 0, ctx, stamps, generating: hasStop };
});
console.log(JSON.stringify(st, null, 1));
await task.finish({ keep: [] });
