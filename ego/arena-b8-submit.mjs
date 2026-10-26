const { readFileSync } = await import("node:fs");
const promptText = readFileSync("/Users/a1-6/Desktop/workspace/d1-video-recreation/arena-prompts/batch8-episodes-v1.0.md", "utf8");

const task = await taskSpace("arena-b8-submit-v2");
const page = task.page("p1");
await page.goto("https://arena.ai/agent", { waitUntil: "domcontentloaded", timeout: 30000 });
await new Promise(r => setTimeout(r, 12000));

const ready = await page.evaluate(() => {
  const tiptap = document.querySelector(".tiptap.ProseMirror");
  const sendBtn = document.querySelector('button[aria-label="Send message"]');
  return { hasTiptap: !!tiptap, hasSend: !!sendBtn, bodyLen: document.body.innerText.length };
});
console.log("READY:", JSON.stringify(ready));

if (ready.hasTiptap && ready.hasSend) {
  await page.evaluate((text) => {
    const el = document.querySelector(".tiptap.ProseMirror");
    el.focus();
    el.innerText = text;
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }, promptText);
  await new Promise(r => setTimeout(r, 2000));
  await page.evaluate(() => {
    const btn = document.querySelector('button[aria-label="Send message"]');
    btn.click();
  });
  console.log("SENT");
  await new Promise(r => setTimeout(r, 5000));
  const after = await page.evaluate(() => ({
    url: location.href,
    bodyLen: document.body.innerText.length,
    bodyHead: document.body.innerText.slice(0, 300)
  }));
  console.log("AFTER:", JSON.stringify(after, null, 2));
} else {
  console.log("FAILED: tiptap or send button not found");
}
await task.finish({ keep: [] });
