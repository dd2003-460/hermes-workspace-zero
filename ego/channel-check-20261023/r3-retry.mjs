// 重试 ERR_CONNECTION_RESET 的 4 站（换顺序、加长超时），并把 deepseek/glm 的真实状态判对
const task = await taskSpace("pf-bench-channel-round4");
const page = task.page("p1");
const OUT = "/tmp/prompt-first-bench/bench/evidence/round4-channel";
const fs = await import("node:fs/promises");

const sites = [
  { id: "chatgpt", url: "https://chatgpt.com" },
  { id: "aistudio", url: "https://aistudio.google.com" },
  { id: "gemini", url: "https://gemini.google.com" },
  { id: "perplexity", url: "https://perplexity.ai" },
];

const results = [];
for (const site of sites) {
  const r = { id: site.id, url: site.url };
  try {
    await page.goto(site.url, { timeout: 60000 });
    await page.waitForLoadState("domcontentloaded", { timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(6000);
    r.finalUrl = await page.url();
    r.title = await page.title();
    r.pageText = await page.evaluate(() => (document.body ? document.body.innerText : "").slice(0, 1000));
    await page.screenshot({ path: `${OUT}/${site.id}.png` });
    r.shot = `${OUT}/${site.id}.png`;
    const t = (r.pageText || "") + " " + (r.title || "");
    if (/attention required|cloudflare/i.test(r.title)) r.status = "blocked_cloudflare";
    else if (/connection was reset|ERR_CONNECTION/i.test(r.title)) r.status = "reset";
    else r.status = "loaded";
    r.pageTextHead = r.pageText.slice(0, 500);
  } catch (e) {
    r.status = "error";
    r.error = String(e).slice(0, 200);
    try {
      r.title = await page.title().catch(() => "");
      await page.screenshot({ path: `${OUT}/${site.id}-err.png` }).catch(() => {});
      r.shot = `${OUT}/${site.id}-err.png`;
      r.pageText = (await page.evaluate(() => (document.body ? document.body.innerText : "").slice(0, 400)).catch(() => ""));
      r.pageTextHead = r.pageText;
    } catch {}
  }
  results.push(r);
  console.log(`RETRY ${site.id}: ${r.status} ${r.title || ""} ${(r.error || "").slice(0, 80)}`);
  await page.waitForTimeout(3000);
}

const prev = JSON.parse(await fs.readFile(`${OUT}/probe-results.json`, "utf8"));
const merged = prev.map((p) => results.find((r) => r.id === p.id) || p);
await fs.writeFile(`${OUT}/probe-results.json`, JSON.stringify(merged, null, 2), "utf8");
console.log("SAVED merged probe-results.json");
console.log("SUMMARY:", merged.map((r) => `${r.id}=${r.status}`).join(" | "));
