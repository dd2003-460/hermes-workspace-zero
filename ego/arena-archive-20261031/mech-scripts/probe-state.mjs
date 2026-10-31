const sid = "01a18404-6fb4-742d-8890-0a1fa8c1fe6b";
const task = await taskSpace("probe-state");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  const nLead = body.split('Lead 续推指令').length - 1;
  // 最后一条消息附近内容
  const lastIdx = body.lastIndexOf('just now');
  return { generating: hasStop, leadCount: nLead, tail: body.slice(-400) };
});
console.log(JSON.stringify(st, null, 1));
await task.finish({ keep: [] });
