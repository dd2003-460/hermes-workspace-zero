import { readFileSync } from "node:fs";
const text = readFileSync("/Users/a1-6/Desktop/workspace/ego/arena-b8-20261024/prompt-b8.txt", "utf8");
const task = await taskSpace(535);
const p1 = task.page("p1");
await p1.click('[contenteditable="true"]', { timeout: 5000 });
await p1.waitForTimeout(600);
const ok = await p1.evaluate((t) => {
  const el = document.querySelector('[contenteditable="true"]');
  if (!el) return { err: "no editor" };
  el.focus();
  const dt = new DataTransfer();
  dt.setData("text/plain", t);
  const ev = new ClipboardEvent("paste", { clipboardData: dt, bubbles: true, cancelable: true });
  el.dispatchEvent(ev);
  return { charsAfter: el.innerText.length };
}, text);
await p1.waitForTimeout(1500);
const verify = await p1.evaluate(() => {
  const el = document.querySelector('[contenteditable="true"]');
  return { len: el ? el.innerText.length : -1, head: el ? el.innerText.slice(0, 80) : "" };
});
await p1.screenshot({ path: "/Users/a1-6/Desktop/workspace/ego/arena-b8-20261024/arena-prompt-inserted.png" });
console.log("paste:", JSON.stringify(ok));
console.log("verify:", JSON.stringify(verify));
