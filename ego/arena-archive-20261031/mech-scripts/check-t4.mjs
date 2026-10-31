const sid = "01a1840f-b471-7f18-b90d-cb5fe174c209";
const task = await taskSpace("check-t4");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  const idx = body.lastIndexOf('Lead 续推指令');
  const ctx = idx >= 0 ? body.slice(Math.max(0,idx-150), idx+250) : null;
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  return { found: idx >= 0, ctx, generating: hasStop };
});
console.log(JSON.stringify(st, null, 1));
await task.finish({ keep: [] });
