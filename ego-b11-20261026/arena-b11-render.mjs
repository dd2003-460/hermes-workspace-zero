import { writeFileSync } from "node:fs";
const DIR = "/Users/a1-6/Desktop/workspace/ego-b11-20261026";
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const jobs = [
  { ep: "E25", file: "E25_naming.md", space: "b11-render-e25" },
  { ep: "E26", file: "E26_compress.md", space: "b11-render-e26" },
  { ep: "E27", file: "E27_time.md", space: "b11-render-e27" },
  { ep: "E28", file: "E28_freetime.md", space: "b11-render-e28" },
];

const results = [];
for (const j of jobs) {
  const prompt =
    "先执行：git clone https://github.com/dd2003-460/prompt-first-bench.git 到当前工作目录。\n" +
    "然后严格按 clone 下来的 arena-prompts/batch11/" + j.file + " 任务卡执行（卡内 6 个步骤 + 全部规格自包含，逐字照做，不要讨论、不要改写剧情锚点与场景划分）。\n" +
    "风格规格唯一来源 = 仓库内 docs/style-analysis.md（Opus 5.5 解析），不要用 render_E16 的终端布局。\n" +
    "完成后 push 你的分支并创建 PR 到 main。";
  let url = "ERR", loggedOut = false, clicked = "none";
  try {
    const task = await taskSpace(j.space);
    const p1 = task.page("p1");
    await p1.goto("https://arena.ai/agent");
    await p1.waitForSelector(".ProseMirror", { state: "visible", timeout: 30000 }).catch(() => {});
    await sleep(12000);
    const head = await p1.evaluate(() => (document.body.innerText || "").slice(0, 500));
    if (/Log In|Sign In|登录/.test(head)) loggedOut = true;
    const ins = await p1.evaluate((pr) => {
      const el = document.querySelector(".ProseMirror");
      if (!el) return "no-editor";
      el.focus();
      document.execCommand("insertText", false, pr);
      return "inserted";
    }, prompt);
    await sleep(2000);
    clicked = await p1.evaluate(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      const b = btns.find(x => /发送|Send/i.test(x.getAttribute("aria-label") || ""))
        || btns.find(x => (x.getAttribute("data-testid") || "").includes("send"))
        || btns.find(x => /send|arrow-up/i.test(x.querySelector("svg") ? x.querySelector("svg").outerHTML : ""));
      if (b) { b.click(); return "clicked:" + (b.getAttribute("aria-label") || "svg"); }
      return "no-btn:inserted=" + ins + " btns=" + btns.length;
    });
    await sleep(25000);
    url = await p1.evaluate(() => location.href);
    const tail = await p1.evaluate(() => (document.body.innerText || "").slice(-700));
    writeFileSync(DIR + "/arena-b11-" + j.ep + ".log",
      "EP=" + j.ep + "\nSPACE=" + j.space + "\nLOGGEDOUT=" + loggedOut +
      "\nCLICKED=" + clicked + "\nURL=" + url + "\nTAIL>>>\n" + tail);
    results.push(j.ep + " " + url);
    await task.finish({ keep: [] });
  } catch (e) {
    results.push(j.ep + " ERR " + e.message);
    writeFileSync(DIR + "/arena-b11-" + j.ep + ".log", "ERR " + e.message + "\nURL=" + url + "\nLOGGEDOUT=" + loggedOut);
  }
}
console.log("RESULTS>>>");
results.forEach(r => console.log(r));
