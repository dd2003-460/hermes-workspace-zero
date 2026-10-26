import { readFileSync, writeFileSync } from "node:fs";

const DIR = "/Users/a1-6/Desktop/workspace/ego-b11-20261026";
const card = readFileSync("/Users/a1-6/Desktop/workspace/pfb/arena-prompts/batch11/style-analysis-task.md", "utf8");
const prompt = "请先 clone https://github.com/dd2003-460/prompt-first-bench （main 分支），然后严格按下方任务卡执行全部 6 步并 push 分支开 PR。任务卡如下：\n\n" + card;

const task = await taskSpace("b11-style-parse-20261026");
const p1 = task.page("p1");
await p1.goto("https://arena.ai/agent", { waitUntil: "domcontentloaded", timeout: 60000 }).catch((e) => console.log("goto warn: " + e.message));
await p1.waitForSelector(".ProseMirror", { state: "visible", timeout: 30000 }).catch(() => {});
await new Promise((r) => setTimeout(r, 12000));

const bodyText = await p1.evaluate(() => document.body.innerText || "");
const loggedIn = !/Log In|Sign In/.test(bodyText.slice(0, 3000));
console.log("LOGGED_IN=" + loggedIn);
if (!loggedIn) {
  writeFileSync(DIR + "/arena-01-need-login.png", null);
  console.log("NEED_LOGIN — 停止");
  await task.finish({ keep: [] });
  process.exit(1);
}

const filled = await p1.evaluate((text) => {
  const el = document.querySelector(".ProseMirror");
  if (!el) return false;
  el.focus();
  document.execCommand("insertText", false, text);
  return true;
}, prompt);
console.log("FILLED=" + filled);
await new Promise((r) => setTimeout(r, 2000));

const sent = await p1.evaluate(() => {
  const btns = Array.from(document.querySelectorAll("button"));
  const target = btns.find((b) =>
    /发送|Send/i.test(b.getAttribute("aria-label") || "") ||
    (b.getAttribute("data-testid") || "").includes("send") ||
    /send|arrow-up/i.test(b.querySelector("svg") ? b.querySelector("svg").outerHTML : "")
  );
  if (!target) return "NO_SEND_BUTTON";
  target.click();
  return "CLICKED";
});
console.log("SEND=" + sent);
await new Promise((r) => setTimeout(r, 25000));

const url = await p1.url();
console.log("SESSION_URL=" + url);
const tail = await p1.evaluate(() => (document.body.innerText || "").slice(-600));
writeFileSync(DIR + "/arena-01-tail.txt", "URL: " + url + "\n\n--- tail 600 ---\n" + tail);
console.log(tail.slice(-300));
await task.finish({ keep: [] });
