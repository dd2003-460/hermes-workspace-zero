const sid = "01a1840f-b471-7f18-b90d-cb5fe174c209";
const task = await taskSpace("check-t4v3");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/" + sid, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(p => setTimeout(p, 15000));
const st = await page.evaluate(() => {
  const body = document.body.innerText;
  const hasStop = !!document.querySelector('button[aria-label*="Stop" i]');
  // 找 reCAPTCHA 是否还在
  const recaptcha = body.includes('Security Verification') || body.includes('reCAPTCHA');
  // 最后几条消息时间戳
  const stamps = [...body.matchAll(/(\d+m \d+s|\d+h \d+m) \| (yesterday|today|\d+ days? ago|just now)/g)].map(m => m[0]).slice(-6);
  return { generating: hasStop, recaptcha, stamps };
});
console.log(JSON.stringify(st, null, 1));
await task.finish({ keep: [] });
