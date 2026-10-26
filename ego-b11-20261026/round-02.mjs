import { writeFileSync } from "node:fs";

const DIR = "/Users/a1-6/Desktop/workspace/ego-b11-20261026";
const task = await taskSpace("b11-bili-20261026");
const p1 = task.page("p1");

// 点击「展开合集详情」（原生 CSS，ego-browser 不暴露 locator()）
await p1.click('button[aria-label="展开合集详情"]');
await p1.waitForTimeout(4000);

const info = await p1.evaluate(() => {
  const out = { url: location.href, videoLinks: [], titles: [] };
  const seen = new Set();
  const as = Array.from(document.querySelectorAll("a[href*='bilibili.com/video/']"));
  for (const a of as) {
    const t = (a.innerText || "").trim().replace(/\s+/g, " ");
    if (!t || t.length < 4) continue;
    if (seen.has(a.href)) continue;
    seen.add(a.href);
    out.videoLinks.push({ t: t.slice(0, 90), h: a.href.split("?")[0] });
  }
  const items = Array.from(document.querySelectorAll("[class*='video-card'], [class*='episode'], [class*='list-item'], [class*='item-title']")).slice(0, 60);
  for (const it of items) {
    const txt = (it.innerText || "").trim().replace(/\s+/g, " ");
    if (txt && txt.length > 5 && txt.length < 150) out.titles.push(txt);
  }
  return out;
});

writeFileSync(DIR + "/round-02-info.json", JSON.stringify(info, null, 2));
try { await p1.screenshot({ path: DIR + "/round-02.png" }); } catch (e) { console.log("shot err " + e.message); }

console.log("URL=" + info.url);
console.log("LINKS=" + info.videoLinks.length);
for (const v of info.videoLinks.slice(0, 40)) console.log(v.t + " || " + v.h);
console.log("=== titles sample ===");
console.log(JSON.stringify(info.titles.slice(0, 40), null, 1));
