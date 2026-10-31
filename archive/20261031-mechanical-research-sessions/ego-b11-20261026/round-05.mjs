import { writeFileSync, mkdirSync } from "node:fs";

const DIR = "/Users/a1-6/Desktop/workspace/ego-b11-20261026";
const COVERS = DIR + "/refs/opus55/covers";
mkdirSync(COVERS, { recursive: true });

const task = await taskSpace("b11-bili-20261026");
const p1 = task.page("p1");

// 提取完整合集数据（ugc_season）
const season = await p1.evaluate(() => {
  const st = window.__INITIAL_STATE__ || {};
  const v = st.videoData || {};
  const u = v.ugc_season || {};
  const out = {
    seasonId: u.id || v.season_id,
    title: u.title,
    intro: u.intro,
    cover: u.cover,
    mid: u.mid,
    eps: []
  };
  const secs = u.sections || [];
  for (const s of secs) {
    for (const e of (s.episodes || [])) {
      out.eps.push({
        id: e.id, aid: e.aid, bvid: e.bvid, cid: e.cid,
        title: e.title, pic: e.pic, duration: e.duration,
        arcPic: e.arc ? e.arc.pic : null
      });
    }
  }
  return out;
});

writeFileSync(DIR + "/round-05-season.json", JSON.stringify(season, null, 2));
console.log("TITLE=" + season.title);
console.log("SEASON_ID=" + season.seasonId + " MID=" + season.mid);
console.log("EP_COUNT=" + season.eps.length);
for (let i = 0; i < season.eps.length; i++) {
  const e = season.eps[i];
  console.log("[" + String(i + 1).padStart(2, "0") + "] " + e.title + " || BV=" + e.bvid + " || " + e.duration + "s");
}
console.log("INTRO_START>>>");
console.log((season.intro || "").slice(0, 1500));
console.log("<<<INTRO_END");

// 下载所有封面（Node fetch，绕开页内 CORS）
const https = (u) => (u ? u.replace(/^http:/, "https:") : "");
let ok = 0, fail = 0;
for (let i = 0; i < season.eps.length; i++) {
  const e = season.eps[i];
  const url = https(e.pic);
  if (!url) continue;
  try {
    const r = await fetch(url);
    if (!r.ok) { fail++; console.log("cover " + (i + 1) + " HTTP " + r.status); continue; }
    const buf = Buffer.from(await r.arrayBuffer());
    writeFileSync(COVERS + "/ep" + String(i + 1).padStart(2, "0") + ".jpg", buf);
    ok++;
  } catch (err) { fail++; console.log("cover " + (i + 1) + " ERR " + err.message); }
}
// 合集封面
try {
  const rc = await fetch(https(season.cover));
  if (rc.ok) writeFileSync(COVERS + "/_season-cover.jpg", Buffer.from(await rc.arrayBuffer()));
} catch (e) { console.log("season cover ERR " + e.message); }
console.log("COVERS_OK=" + ok + " FAIL=" + fail);
