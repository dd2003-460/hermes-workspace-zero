const task = await taskSpace(535);
const p1 = task.page("p1");
// Confirm repo button shows prompt-first-bench
const repoText = await p1.evaluate(() => {
  const btns = Array.from(document.querySelectorAll('button'));
  const repo = btns.find(b => b.textContent.includes('dd2003-460'));
  return repo ? repo.textContent.trim() : "NOT FOUND";
});
console.log("repo button:", repoText);
if (!repoText.includes("prompt-first-bench")) {
  console.log("ABORT: repo not prompt-first-bench, not submitting");
  process.exit(0);
}
await p1.screenshot({ path: "/Users/a1-6/Desktop/workspace/ego/arena-b8-20261024/arena-before-submit.png" });
// Submit
await p1.click('button[aria-label="Send message"]', { timeout: 5000 });
await p1.waitForTimeout(4000);
await p1.screenshot({ path: "/Users/a1-6/Desktop/workspace/ego/arena-b8-20261024/arena-after-submit.png" });
console.log("SUBMITTED. url:", p1.url());
