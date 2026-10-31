const task = await taskSpace("arena-b8-check-r10e");
const page = task.page("p1");
await page.goto("https://arena.ai/agent", { waitUntil: "domcontentloaded", timeout: 30000 });
await new Promise(r => setTimeout(r, 20000));
const info = await page.evaluate(() => {
  const body = document.body.innerText;
  const stopBtn = !!document.querySelector('button[aria-label*="Stop" i]');
  const noChanges = body.includes("No Changes");
  const branchPushed = body.includes("Branch pushed");
  const sessionLinks = [...document.querySelectorAll('a[href*="/agent/"]')].slice(0, 5).map(a => ({
    text: a.innerText.slice(0, 100),
    href: a.href
  }));
  return { stopBtn, noChanges, branchPushed, sessionLinks, bodyLen: body.length, bodyHead: body.slice(0, 500) };
});
console.log(JSON.stringify(info, null, 2));
await task.finish({ keep: false });
