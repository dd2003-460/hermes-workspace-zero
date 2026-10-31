// Round 4 路A 步骤2: 备用网页 LLM 通道逐站探测（7 站，每站 1 次简单 prompt 尝试）
const task = await taskSpace("pf-bench-channel-round4");
const page = task.page("p1");
const OUT = "/tmp/prompt-first-bench/bench/evidence/round4-channel";
const fs = await import("node:fs/promises");

const sites = [
  { id: "chatgpt", url: "https://chatgpt.com" },
  { id: "deepseek", url: "https://chat.deepseek.com" },
  { id: "glm", url: "https://chatglm.cn" },
  { id: "aistudio", url: "https://aistudio.google.com" },
  { id: "gemini", url: "https://gemini.google.com" },
  { id: "perplexity", url: "https://perplexity.ai" },
  { id: "lmarena", url: "https://arena.ai/agent" },
];

const results = [];

async function probe(site) {
  const r = { id: site.id, url: site.url };
  try {
    await page.goto(site.url, { timeout: 45000 });
    await page.waitForLoadState("domcontentloaded", { timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(5000);
    r.finalUrl = await page.url();
    r.title = await page.title();
    r.pageText = await page.evaluate(() => (document.body ? document.body.innerText : "").slice(0, 1200));
    const shot = `${OUT}/${site.id}.png`;
    await page.screenshot({ path: shot });
    r.shot = shot;

    // 分类
    const t = (r.pageText || "") + " " + (r.title || "");
    if (/cloudflare|attention required|access denied|blocked/i.test(r.title) || /cf-turnstile|verify you are human|challenge platform/i.test(t)) {
      r.status = "blocked_cloudflare";
    } else if (/sign in|log in|登录|登录|sign up|登录以/i.test(t)) {
      r.status = "needs_login";
    } else {
      r.status = "loaded";
    }

    // loaded 的站点：尝试简单 prompt
    if (r.status === "loaded") {
      r.promptAttempt = await tryPrompt(page, site.id, OUT);
    }
  } catch (e) {
    r.status = "error";
    r.error = String(e).slice(0, 300);
  }
  results.push(r);
  console.log(`SITE ${site.id}: ${r.status} ${r.finalUrl || ""} ${r.title || ""}`);
  return r;
}

async function tryPrompt(p, id, outDir) {
  const a = { id };
  try {
    const snap = await p.snapshot();
    a.snapHead = snap.slice(0, 2500);
    // 找输入框
    let inputSel = null;
    for (const sel of [
      "textarea",
      "div[contenteditable=true]",
      "input[type=text]",
      "[role=textbox]",
    ]) {
      const n = await p.evaluate((s) => document.querySelectorAll(s).length, sel);
      if (n > 0) { inputSel = sel; break; }
    }
    a.inputSel = inputSel;
    if (!inputSel) { a.result = "no_input"; return a; }

    await p.fill(inputSel, "回复 OK 两个词", { timeout: 10000 });
    await p.waitForTimeout(500);
    // 找发送按钮
    let sent = false;
    for (const sel of [
      "button[aria-label*=Send i], button[aria-label*=发送]",
      "button[aria-label*=Send]",
      "[data-testid=send-button]",
    ]) {
      const n = await p.evaluate((s) => document.querySelectorAll(s).length, sel);
      if (n > 0) {
        await p.click(sel, { timeout: 8000 }).catch(() => {});
        sent = true;
        a.sendSel = sel;
        break;
      }
    }
    if (!sent) {
      await p.press(inputSel, "Enter", { timeout: 8000 }).catch(() => {});
      a.sendSel = "Enter";
    }
    await p.waitForTimeout(15000);
    a.afterText = await p.evaluate(() => (document.body ? document.body.innerText : "").slice(-1500));
    a.result = /OK/i.test(a.afterText) ? "ok_reply" : "sent_no_ok";
    await p.screenshot({ path: `${outDir}/${id}-after.png` });
    a.afterShot = `${outDir}/${id}-after.png`;
  } catch (e) {
    a.result = "error";
    a.error = String(e).slice(0, 200);
  }
  return a;
}

for (const s of sites) {
  await probe(s);
}

await fs.mkdir(OUT, { recursive: true });
await fs.writeFile(`${OUT}/probe-results.json`, JSON.stringify(results, null, 2), "utf8");
console.log("SAVED: " + OUT + "/probe-results.json");
console.log("SUMMARY:", results.map((r) => `${r.id}=${r.status}${r.promptAttempt ? ":" + r.promptAttempt.result : ""}`).join(" | "));
