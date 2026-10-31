// Round 04: re-navigate to arena, load the FULL session list (scroll to defeat lazy-load/virtualization), extract all /agent/ hrefs
const task = await taskSpace("arena-cleanup-20261024");
const page = task.page("p1");

await page.goto("https://arena.ai/agent", { waitUntil: "networkidle" }).catch(e => console.log("goto catch:", String(e).slice(0,120)));
await page.waitForTimeout(2500);

console.log("URL after goto:", await page.url());

// Helper: collect current /agent/ anchors as a Set of hrefs
const collect = () => page.evaluate(() => {
  const s = new Set();
  document.querySelectorAll('a[href*="/agent/"]').forEach(a => s.add(a.getAttribute("href")));
  return Array.from(s);
});

let seen = new Set(await collect());
console.log("initial anchors:", seen.size);

// Find scrollable containers (re-check now that page is real)
const contInfo = await page.evaluate(() => {
  const all = Array.from(document.querySelectorAll("*"));
  return all.filter(el => {
    const s = getComputedStyle(el);
    return (s.overflowY === "auto" || s.overflowY === "scroll") && el.scrollHeight > el.clientHeight + 10;
  }).map(el => ({
    tag: el.tagName, cls: (el.className || "").toString().slice(0, 60),
    sh: el.scrollHeight, ch: el.clientHeight,
    anchors: el.querySelectorAll('a[href*="/agent/"]').length
  })).sort((a,b) => b.anchors - a.anchors).slice(0, 6);
});
console.log("scrollable containers:", JSON.stringify(contInfo, null, 1));

// Scroll each candidate container; collect anchors incrementally until stable
for (const c of contInfo.filter(c => c.anchors > 0)) {
  const progress = await page.evaluate(async (sel) => {
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const all = Array.from(document.querySelectorAll("*"));
    const cand = all.filter(el => {
      const s = getComputedStyle(el);
      return (s.overflowY === "auto" || s.overflowY === "scroll") && el.scrollHeight > el.clientHeight + 10;
    });
    cand.forEach(el => el._n = el.querySelectorAll('a[href*="/agent/"]').length);
    cand.sort((a,b) => b._n - a._n);
    const el = cand[0];
    if (!el) return { ok:false };
    let prev = 0, same = 0;
    for (let i = 0; i < 80 && same < 5; i++) {
      el.scrollTop = el.scrollHeight;
      await sleep(300);
      const cur = el.querySelectorAll('a[href*="/agent/"]').length;
      if (cur === prev) same++; else { same = 0; prev = cur; }
    }
    return { ok:true, finalSh: el.scrollHeight, finalCh: el.clientHeight };
  }).catch(e => ({ ok:false, err:String(e).slice(0,120) }));
  console.log("scroll progress:", JSON.stringify(progress));
  const now = await collect();
  now.forEach(h => seen.add(h));
}

// Also try scrolling the window itself as a fallback
await page.evaluate(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  let prev = 0, same = 0;
  for (let i = 0; i < 40 && same < 5; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    await sleep(300);
    const cur = document.querySelectorAll('a[href*="/agent/"]').length;
    if (cur === prev) same++; else { same = 0; prev = cur; }
  }
});
(await collect()).forEach(h => seen.add(h));

const all = Array.from(seen);
console.log("TOTAL unique /agent/ sessions found:", all.length);
console.log(JSON.stringify(all, null, 1));

// print for capture (ESM has no require)
console.log("ALL_HREFS_JSON_START");
console.log(JSON.stringify(all));
console.log("ALL_HREFS_JSON_END");
