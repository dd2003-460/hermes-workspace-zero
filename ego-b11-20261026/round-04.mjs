import { writeFileSync } from "node:fs";

const DIR = "/Users/a1-6/Desktop/workspace/ego-b11-20261026";
const task = await taskSpace("b11-bili-20261026");
const p1 = task.page("p1");

// 第一步：递归搜索 __INITIAL_STATE__ 里 season/series/drama/ep 相关 key 路径
const stateScan = await p1.evaluate(() => {
  const hits = [];
  const st = window.__INITIAL_STATE__ || {};
  function walk(obj, path, depth) {
    if (!obj || typeof obj !== "object" || depth > 4) return;
    for (const k of Object.keys(obj)) {
      const p = path ? path + "." + k : k;
      const kl = k.toLowerCase();
      if (/season|series|drama|episode|part_|archive/.test(kl)) {
        let sample;
        try { sample = JSON.stringify(obj[k]).slice(0, 300); } catch (e) { sample = String(obj[k]).slice(0, 200); }
        hits.push({ path: p, sample });
      }
      if (typeof obj[k] === "object") walk(obj[k], p, depth + 1);
    }
  }
  walk(st, "", 0);
  const topKeys = Object.keys(st);
  return { topKeys, hits: hits.slice(0, 30) };
});

writeFileSync(DIR + "/round-04-state-scan.json", JSON.stringify(stateScan, null, 2));
console.log("TOP_KEYS=" + stateScan.topKeys.join(","));
console.log("HITS=" + stateScan.hits.length);
for (const h of stateScan.hits.slice(0, 20)) console.log(h.path + " :: " + h.sample);

// 第二步：JS 层直接点「展开合集详情」绕过 pointer 拦截
const clicked = await p1.evaluate(() => {
  const btn = document.querySelector('button[aria-label="展开合集详情"]');
  if (!btn) return { ok: false, why: "button not found" };
  btn.click();
  return { ok: true };
});
console.log("CLICK=" + JSON.stringify(clicked));
await p1.waitForTimeout(4000);

// 第三步：抓展开后的剧集链接
const list = await p1.evaluate(() => {
  const out = { links: [], texts: [] };
  const seen = new Set();
  const as = Array.from(document.querySelectorAll("a[href*='/video/BV']"));
  for (const a of as) {
    const h = a.href.split("?")[0];
    if (seen.has(h)) continue;
    seen.add(h);
    const t = (a.innerText || "").trim().replace(/\s+/g, " ").slice(0, 100);
    if (t) out.links.push({ t, h });
  }
  // 浮层里常见文本
  const f = document.querySelector("[class*='drama'], [class*='float'], [class*='season'], [class*='series']");
  if (f) out.texts.push((f.innerText || "").slice(0, 1500));
  return out;
});

writeFileSync(DIR + "/round-04-list.json", JSON.stringify(list, null, 2));
try { await p1.screenshot({ path: DIR + "/round-04.png" }); } catch (e) { console.log("shot err " + e.message); }
console.log("LINKS=" + list.links.length);
for (const l of list.links.slice(0, 30)) console.log(l.t + " || " + l.h);
if (list.texts.length) console.log("FLOAT_TEXT=" + list.texts[0].slice(0, 600));
