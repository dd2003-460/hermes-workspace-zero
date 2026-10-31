// DeepSeek（已登录）+ GLM（未登录）详细状态确认
const task = await taskSpace("pf-bench-channel-round4");
const page = task.page("p1");
const OUT = "/tmp/prompt-first-bench/bench/evidence/round4-channel";

const report = {};

// --- DeepSeek ---
await page.goto("https://chat.deepseek.com", { timeout: 60000 });
await page.waitForLoadState("domcontentloaded", { timeout: 30000 }).catch(() => {});
await page.waitForTimeout(5000);
report.deepseek = {
  url: await page.url(),
  title: await page.title(),
  loginCheck: await page.evaluate(() => {
    const b = document.body ? document.body.innerText : "";
    return {
      hasLoginBtn: /登 录|登录|Sign in|Log in/i.test(b) && !/新对话|开启新对话/.test(b),
      hasChatUI: /开启新对话|新对话|输入问题/.test(b),
      hasUserMenu: !!document.querySelector('[class*=avatar], [class*=user], [class*=account]'),
      textHead: b.slice(0, 300),
    };
  }),
};
console.log("DEEPSEEK:", JSON.stringify(report.deepseek.loginCheck, null, 2));
await page.screenshot({ path: `${OUT}/deepseek-detail.png` });

// --- GLM ---
await page.goto("https://chatglm.cn", { timeout: 60000 });
await page.waitForLoadState("domcontentloaded", { timeout: 30000 }).catch(() => {});
await page.waitForTimeout(5000);
report.glm = {
  url: await page.url(),
  title: await page.title(),
  loginCheck: await page.evaluate(() => {
    const b = document.body ? document.body.innerText : "";
    return {
      hasLoginBtn: /登录|Sign in|Log in/.test(b),
      hasChatUI: /和我聊聊天吧|新对话/.test(b),
      textHead: b.slice(0, 300),
    };
  }),
};
console.log("GLM:", JSON.stringify(report.glm.loginCheck, null, 2));
await page.screenshot({ path: `${OUT}/glm-detail.png` });

console.log("DONE");
