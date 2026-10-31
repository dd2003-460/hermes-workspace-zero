import { writeFileSync } from "node:fs";

const DIR = "/Users/a1-6/Desktop/workspace/ego-b11-20261026";

const task = await taskSpace("b11-bili-20261026");
const p1 = task.page("p1");

await p1.goto("https://b23.tv/MRSYvTQ", { waitUntil: "domcontentloaded", timeout: 60000 });
await p1.waitForTimeout(12000); // hydration 等待（教训：3s 太早）

const info = await p1.evaluate(() => {
  const out = {
    url: location.href,
    title: document.title,
    up: "",
    cards: [],
    videoLinks: []
  };
  const upSel = [".up-name", "[class*='upName']", ".bili-video-card__info--author .bili-video-card__info--link", "[class*='author-name']", "[class*='uname']"];
  for (const s of upSel) {
    const el = document.querySelector(s);
    if (el && el.innerText) { out.up = el.innerText.trim(); break; }
  }
  const listSel = ".video-list-item, .list-item, .bili-video-card, [class*='video-card'], [class*='video-card__info'], .opus-video-card, [class*='series-item']";
  const cards = Array.from(document.querySelectorAll(listSel)).slice(0, 40);
  for (const c of cards) {
    const a = c.querySelector("a[href*='/video/'], a[href*='av']");
    const tEl = c.querySelector("[class*='title']");
    const dEl = c.querySelector("[class*='duration'], [class*='dur']");
    out.cards.push({
      title: (tEl ? tEl.innerText : c.innerText || "").trim().replace(/\s+/g, " ").slice(0, 100),
      dur: dEl ? dEl.innerText.trim() : "",
      href: a ? a.href : ""
    });
  }
  out.videoLinks = Array.from(document.querySelectorAll("a[href*='bilibili.com/video/']")).slice(0, 50)
    .map(a => ({ t: (a.innerText || "").trim().replace(/\s+/g, " ").slice(0, 70), h: a.href }));
  return out;
});

writeFileSync(DIR + "/round-01-info.json", JSON.stringify(info, null, 2));

try {
  await p1.screenshot({ path: DIR + "/round-01.png" });
} catch (e) {
  console.log("screenshot err: " + e.message);
}

const snap = await p1.snapshot();
writeFileSync(DIR + "/round-01-snap.txt", typeof snap === "string" ? snap : JSON.stringify(snap, null, 2));

console.log("URL=" + info.url);
console.log("TITLE=" + info.title);
console.log("UP=" + info.up);
console.log("CARDS=" + info.cards.length + " VIDEO_LINKS=" + info.videoLinks.length);
console.log(JSON.stringify(info.cards.slice(0, 15), null, 1));
if (info.cards.length === 0) {
  console.log("VIDEO_LINKS_SAMPLE=" + JSON.stringify(info.videoLinks.slice(0, 10), null, 1));
}
