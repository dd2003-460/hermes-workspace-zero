// DeepSeek 已登录 → 试 1 次简单 prompt，确认响应质量
const task = await taskSpace("pf-bench-channel-round4");
const page = task.page("p1");
const OUT = "/tmp/prompt-first-bench/bench/evidence/round4-channel";

await page.goto("https://chat.deepseek.com", { timeout: 60000 });
await page.waitForLoadState("domcontentloaded", { timeout: 30000 }).catch(() => {});
await page.waitForTimeout(4000);

// 点"开启新对话"开干净会话
try {
  await page.click("text=开启新对话", { timeout: 8000 });
} catch (e) {
  console.log("newchat click failed:", String(e).slice(0, 120));
}
await page.waitForTimeout(3000);

// 找输入框并发送
const inputInfo = await page.evaluate(() => {
  const els = [...document.querySelectorAll("textarea, div[contenteditable=true], [role=textbox]")];
  return els.map((e) => ({ tag: e.tagName, role: e.getAttribute("role"), ce: e.getAttribute("contenteditable"), ph: e.getAttribute("placeholder") || "" })).slice(0, 8);
});
console.log("INPUTS:", JSON.stringify(inputInfo));

let sel = "div[contenteditable=true]";
if (inputInfo.find((i) => i.ce === "true" || i.tag === "DIV")) sel = "div[contenteditable=true]";
else if (inputInfo.find((i) => i.tag === "TEXTAREA")) sel = "textarea";

await page.fill(sel, "回复 OK 两个词", { timeout: 10000 });
await page.waitForTimeout(800);
// 发送按钮
const sent = await page.evaluate(() => {
  const btns = [...document.querySelectorAll("button")];
  const b = btns.find((x) => /send|发送/i.test(x.getAttribute("aria-label") || "") || /send/i.test(x.innerHTML));
  if (b) { b.click(); return b.getAttribute("aria-label") || "clicked"; }
  return null;
});
console.log("SEND:", sent);
await page.waitForTimeout(20000);

const after = await page.evaluate(() => {
  const b = document.body ? document.body.innerText : "";
  return b.slice(-800);
});
console.log("AFTER:", after);
await page.screenshot({ path: `${OUT}/deepseek-after.png` });
console.log("SHOT:", `${OUT}/deepseek-after.png`);
const ok = /OK/i.test(after);
console.log("DEEPSEEK_RUN:", ok ? "SUCCESS_OK_REPLY" : "NO_OK_SEEN");
