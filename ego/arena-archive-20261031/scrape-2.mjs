import { writeFileSync, mkdirSync } from 'fs';
const id = "01a15eff-82a5-70f2-95cd-9f83baae5b28";
const url = "https://arena.ai/agent/" + id;
mkdirSync('/Users/a1-6/Desktop/workspace/ego/arena-archive-20261031/sessions', { recursive: true });
const task = await taskSpace("scrape-" + id.slice(0,8));
const page = task.page("p1");
await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 });
await new Promise(r => setTimeout(r, 12000));
let prevLen = 0;
for (let i = 0; i < 15; i++) {
  const len = await page.evaluate(() => document.body.innerText.length);
  if (len === prevLen && i > 2) break;
  prevLen = len;
  await page.evaluate(() => {
    for (const c of document.querySelectorAll('div')) {
      if (c.scrollHeight > c.clientHeight + 100) c.scrollTop = c.scrollHeight;
    }
  });
  await new Promise(r => setTimeout(r, 2000));
}
const text = await page.evaluate(() => document.body.innerText);
writeFileSync(`/Users/a1-6/Desktop/workspace/ego/arena-archive-20261031/sessions/${id}.txt`, text);
console.log('saved', id, 'chars:', text.length);
await task.finish({ keep: [] });
