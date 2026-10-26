// Round 02: get the FULL session list.
// (a) probe JSON API endpoints (page context, has auth cookies)
// (b) scroll the session list to force lazy-load, then re-extract all anchors
const task = await taskSpace("arena-cleanup-20261024");
const page = task.page("p1");

// --- (a) API probe ---
const probe = async () => {
  const cands = ["/api/agent", "/api/agents", "/api/agent/sessions", "/api/sessions", "/api/chat/sessions", "/api/user/sessions"];
  const out = [];
  for (const u of cands) {
    try {
      const r = await fetch(u, { headers: { accept: "application/json" } });
      const txt = await r.text();
      out.push({ u, status: r.status, len: txt.length, head: txt.slice(0, 300) });
    } catch (e) {
      out.push({ u, err: String(e).slice(0, 120) });
    }
  }
  return out;
};
const apiProbe = await page.evaluate(probe);

// --- (b) find scrollable containers ---
const containers = await page.evaluate(() => {
  const all = Array.from(document.querySelectorAll("*"));
  const sc = all.filter(el => {
    const s = getComputedStyle(el);
    return (s.overflowY === "auto" || s.overflowY === "scroll") && el.scrollHeight > el.clientHeight + 20;
  }).map(el => ({
    tag: el.tagName, cls: (el.className || "").toString().slice(0, 80),
    id: el.id, sh: el.scrollHeight, ch: el.clientHeight,
    anchors: el.querySelectorAll('a[href*="/agent/"]').length
  }));
  return sc.sort((a, b) => b.anchors - a.anchors).slice(0, 8);
});

// --- scroll the best container (most anchors) to load all ---
let scrollResult = null;
if (containers.length) {
  scrollResult = await page.evaluate(async () => {
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const all = Array.from(document.querySelectorAll("*"));
    const cands = all.filter(el => {
      const s = getComputedStyle(el);
      return (s.overflowY === "auto" || s.overflowY === "scroll") && el.scrollHeight > el.clientHeight + 20;
    });
    // pick the container that contains the most /agent/ anchors
    cands.forEach(el => el._n = el.querySelectorAll('a[href*="/agent/"]').length);
    cands.sort((a, b) => b._n - a._n);
    const el = cands[0];
    if (!el) return { scrolled: false };
    let prev = 0, same = 0;
    for (let i = 0; i < 60 && same < 4; i++) {
      el.scrollTop = el.scrollHeight;
      await sleep(350);
      const cur = el.querySelectorAll('a[href*="/agent/"]').length;
      if (cur === prev) { same++; } else { same = 0; prev = cur; }
    }
    const anchors = Array.from(el.querySelectorAll('a[href*="/agent/"]')).map(a => a.getAttribute("href"));
    return { scrolled: true, sh: el.scrollHeight, ch: el.clientHeight, anchorCount: anchors.length, sample: anchors.slice(0, 5) };
  });
}

// --- final full extraction ---
const finalAnchors = await page.evaluate(() => {
  const anchors = Array.from(document.querySelectorAll('a[href*="/agent/"]')).map(a => a.getAttribute("href"));
  const uniq = Array.from(new Set(anchors));
  return { total: uniq.length, hrefs: uniq };
});

console.log(JSON.stringify({ apiProbe, containers, scrollResult, finalAnchors }, null, 1));
await page.screenshot({ path: "/Users/a1-6/Desktop/workspace/ego/arena-cleanup-20261024/full-list.png" });
