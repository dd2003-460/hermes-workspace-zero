// Round 4 路A 步骤1: arena.ai 封禁检查（1 次简单 run）
const task = await taskSpace("pf-bench-channel-round4");
const page = task.page("p1");
const shot = "/Users/a1-6/Desktop/workspace/ego/channel-check-20261023/arena.png";

await page.goto("https://arena.ai/text/direct", { timeout: 45000 });
await page.waitForLoadState("domcontentloaded", { timeout: 30000 }).catch(() => {});
await page.waitForTimeout(4000);

const state = {
  url: await page.url(),
  title: await page.title(),
};

// Cloudflare challenge 判定
const cfText = await page.evaluate(() => {
  const t = document.body ? document.body.innerText : "";
  return t.slice(0, 1500);
});
state.cfCheck = {
  hasChallenge: /verify you are human|cf-turnstile|just a moment|cloudflare|challenge/i.test(cfText + state.title),
  bodyHead: cfText.slice(0, 600),
};

console.log("STATE:", JSON.stringify(state, null, 2));

if (state.cfCheck.hasChallenge) {
  await page.screenshot({ path: shot }).catch(() => {});
  console.log("RESULT: BLOCKED_CLOUDFLARE");
  console.log("SHOT:", shot);
  console.log(await page.snapshot({ scope: "full_page" }).catch(() => "snapshot failed"));
} else {
  // 页面正常：尝试 1 次简单 run
  console.log("PAGE OK — attempting simple run");
  const snap = await page.snapshot();
  console.log("SNAP:\n", snap.slice(0, 4000));
  await page.screenshot({ path: shot }).catch(() => {});
  console.log("SHOT:", shot);
  // 先落盘状态，下一轮再发消息（避免单脚本超时）
}
