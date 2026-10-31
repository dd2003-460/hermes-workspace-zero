// 修正 DeepSeek 发送：文本已在输入框，点圆形 send 按钮（箭头图标，无文字 aria-label）
const task = await taskSpace("pf-bench-channel-round4");
const page = task.page("p1");
const OUT = "/tmp/prompt-first-bench/bench/evidence/round4-channel";

// 确认输入框里还有文本
const cur = await page.evaluate(() => {
  const els = [...document.querySelectorAll("textarea, div[contenteditable=true]")];
  return els.map((e) => (e.innerText || e.value || "").trim()).filter(Boolean);
});
console.log("INPUT HAS:", JSON.stringify(cur));

if (!cur.length || !cur.some((t) => t.includes("OK"))) {
  await page.fill("div[contenteditable=true]", "回复 OK 两个词", { timeout: 10000 });
  console.log("refilled");
}

// 点 send 按钮：用 snapshot 找 ref
const snap = await page.snapshot();
const idx = snap.lastIndexOf("回复 OK 两个词");
console.log("SNAP TAIL:\n", snap.slice(-2500));
