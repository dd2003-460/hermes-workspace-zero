// 点 DeepSeek 发送按钮 ref=26（箭头），等回复，读对话内容
const task = await taskSpace("pf-bench-channel-round4");
const page = task.page("p1");
const OUT = "/tmp/prompt-first-bench/bench/evidence/round4-channel";

await page.click("@26", { timeout: 10000, label: "click send arrow" });
console.log("clicked send");

// 等 URL 变化（新会话）或正文出现回复
try {
  await page.waitForURL("**/a/chat/s/**", { timeout: 30000 });
  console.log("URL:", await page.url());
} catch (e) {
  console.log("no url change:", String(e).slice(0, 100));
}
await page.waitForTimeout(20000);

const out = await page.evaluate(() => {
  const all = document.body.innerText.split("\n").map((s) => s.trim()).filter(Boolean);
  return { url: location.href, lines: all.length, last30: all.slice(-30) };
});
console.log(JSON.stringify(out, null, 2));
await page.screenshot({ path: `${OUT}/deepseek-reply.png` });
console.log("SHOT:", `${OUT}/deepseek-reply.png`);
