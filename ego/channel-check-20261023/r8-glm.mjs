// GLM 未登录：确认输入是否可发（大概率弹登录）
const task = await taskSpace("pf-bench-channel-round4");
const page = task.page("p1");
const OUT = "/tmp/prompt-first-bench/bench/evidence/round4-channel";

await page.goto("https://chatglm.cn", { timeout: 60000 });
await page.waitForLoadState("domcontentloaded", { timeout: 30000 }).catch(() => {});
await page.waitForTimeout(5000);

const info = await page.evaluate(() => {
  const els = [...document.querySelectorAll("textarea, div[contenteditable=true], [role=textbox]")];
  return els.map((e) => ({ tag: e.tagName, ce: e.getAttribute("contenteditable"), ph: e.getAttribute("placeholder") || "" })).slice(0, 6);
});
console.log("INPUTS:", JSON.stringify(info));

// 尝试 fill（找主输入框）
let sel = null;
for (const s of ["textarea", "div[contenteditable=true]", "[role=textbox]"]) {
  const n = await page.evaluate((x) => document.querySelectorAll(x).length, s);
  if (n > 0) { sel = s; break; }
}
console.log("SEL:", sel);
if (sel) {
  try {
    await page.fill(sel, "回复 OK 两个词", { timeout: 8000 });
    await page.waitForTimeout(1000);
    // 尝试回车发送
    await page.press(sel, "Enter", { timeout: 8000 }).catch((e) => console.log("press err:", String(e).slice(0, 80)));
    await page.waitForTimeout(5000);
    const after = await page.evaluate(() => ({
      url: location.href,
      loginPopup: /登录|扫码|手机号|密码/.test(document.body ? document.body.innerText : ""),
      textTail: (document.body ? document.body.innerText : "").slice(-600),
    }));
    console.log("AFTER:", JSON.stringify(after, null, 2));
    await page.screenshot({ path: `${OUT}/glm-after.png` });
    console.log("SHOT:", `${OUT}/glm-after.png`);
  } catch (e) {
    console.log("FILL/SEND FAILED:", String(e).slice(0, 200));
  }
}
