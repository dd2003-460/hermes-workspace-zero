import { writeFileSync } from "node:fs";

const DIR = "/Users/a1-6/Desktop/workspace/ego-b11-20261026";
const task = await taskSpace("b11-bili-20261026");
const p1 = task.page("p1");

const state = await p1.evaluate(() => {
  const out = { url: location.href, title: document.title, seasonId: "", mediaId: "", bvid: "", up: "" };
  const m = location.pathname.match(/video\/(BV\w+)/);
  if (m) out.bvid = m[1];
  // 从 window.__INITIAL_STATE__ 拿合集信息（B 站标准数据）
  try {
    const st = window.__INITIAL_STATE__ || {};
    const v = (st.videoData || {});
    if (v.aid) out.aid = v.aid;
    if (v.cid) out.cid = v.cid;
    if (v.owner && v.owner.name) out.up = v.owner.name;
    if (v.stat) out.stat = { view: v.stat.view, like: v.stat.like, coin: v.stat.coin, share: v.stat.share, duration: v.stat.duration };
    const s = st.seasonInfo || (st.season && st.season.data) || st.seasonData || {};
    if (s.season_id) out.seasonId = s.season_id;
    if (s.media_id) out.mediaId = s.media_id;
    if (s.name) out.seasonName = s.name;
    if (s.total_ep) out.totalEp = s.total_ep;
    if (s.sections && s.sections[0] && s.sections[0].episodes) {
      out.eps = s.sections[0].episodes.map(e => ({ bvid: e.bvid, title: e.title, duration: e.duration, id: e.id }));
    }
  } catch (e) { out.stateErr = e.message; }
  return out;
});

writeFileSync(DIR + "/round-03-state.json", JSON.stringify(state, null, 2));
console.log("URL=" + state.url);
console.log("BVID=" + state.bvid, "SEASON_ID=" + state.seasonId, "MEDIA_ID=" + state.mediaId);
console.log("SEASON_NAME=" + (state.seasonName || ""), "TOTAL_EP=" + (state.totalEp || ""));
console.log("UP=" + state.up, "STAT=" + JSON.stringify(state.stat || {}));
console.log("EPS_INLINE=" + (state.eps ? state.eps.length : "none"));
if (state.eps) console.log(JSON.stringify(state.eps, null, 1));
if (state.stateErr) console.log("STATE_ERR=" + state.stateErr);
