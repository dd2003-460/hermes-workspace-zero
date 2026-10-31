const task = await taskSpace("arena-scrape-test");
const page = task.page("p1");
await page.goto("https://arena.ai/agent/01a17723-ee0c-7f4f-98ed-47d35630f950", { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 15000));
// 探查消息 DOM 结构
const info = await page.evaluate(() => {
  const body = document.body.innerText;
  // 找常见消息容器
  const cands = ['[class*="message"]', '[class*="chat"]', '[data-testid]', '.prose', 'article'];
  const counts = {};
  for (const sel of cands) { try { counts[sel] = document.querySelectorAll(sel).length; } catch(e){} }
  return { url: location.href, bodyLen: body.length, counts, bodyHead: body.slice(0, 800), bodyTail: body.slice(-800) };
});
console.log(JSON.stringify(info, null, 2));
await task.finish({ keep: [] });
