const task = await taskSpace("arena-session-list");
const page = task.page("p1");
await page.goto("https://arena.ai/agent", { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 15000));
const info = await page.evaluate(() => {
  const body = document.body.innerText;
  const links = [...document.querySelectorAll('a[href*="/agent/"]')].map(a => ({ text: a.innerText.slice(0,80).replace(/\n/g,' '), href: a.href }));
  return { url: location.href, bodyLen: body.length, bodyHead: body.slice(0, 1500), nLinks: links.length, links: links.slice(0, 40) };
});
console.log(JSON.stringify(info, null, 2));
await task.finish({ keep: false });
