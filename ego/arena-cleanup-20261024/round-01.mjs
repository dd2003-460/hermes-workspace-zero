const task = await taskSpace("arena-cleanup-20261024");
const page = task.page("p1");
console.log("URL:", await page.url());
const items = await page.evaluate(() => {
  const anchors = Array.from(document.querySelectorAll('a[href*="/agent/"]'));
  const out = anchors.map(a => ({
    href: a.getAttribute("href"),
    text: (a.innerText || "").replace(/\s+/g, " ").slice(0, 100)
  }));
  const uuidRe = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;
  const all = Array.from(document.querySelectorAll('div,li,button,a,span'));
  const uuidEls = [];
  const seen = new Set();
  for (const el of all) {
    const t = (el.innerText || "");
    const m = t.match(uuidRe);
    if (m && !seen.has(m[0])) {
      seen.add(m[0]);
      uuidEls.push({ tag: el.tagName, uuid: m[0], text: t.replace(/\s+/g, " ").slice(0, 80) });
    }
  }
  return { anchorCount: out.length, anchors: out.slice(0, 80), uuidCount: uuidEls.length, uuidEls: uuidEls.slice(0, 80) };
});
console.log(JSON.stringify(items, null, 1));
