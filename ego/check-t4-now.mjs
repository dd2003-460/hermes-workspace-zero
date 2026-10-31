const sid = "01a1840f-b471-7f18-b90d-cb5fe174c209";
const task = await taskSpace("check-t4-now");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  const idx = body.lastIndexOf('阶段 03 = pass');
  const after = idx >= 0 ? body.slice(idx, idx + 1200) : null;
  return { generating: hasStop, len: body.length, after };
});
console.log(JSON.stringify(st, null, 1).slice(0, 2200));
await task.finish({ keep: [] });
