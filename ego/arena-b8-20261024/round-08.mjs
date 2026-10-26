const task = await taskSpace(535);
const p1 = task.page("p1");
// Try clicking the pfb option by role=option text (dropdown may still be open with bench filter)
const tryClick = async (sel) => {
  try { await p1.click(sel, { timeout: 4000 }); return sel; } catch { return null; }
};
let used = await tryClick('[role="option"]:has-text("prompt-first-bench")')
        || await tryClick('li:has-text("prompt-first-bench")')
        || await tryClick('[role="listbox"] >> text=prompt-first-bench');
console.log("clicked via:", used);
if (!used) {
  // reopen + search + click
  await p1.click('button:has-text("-orf")');
  await p1.waitForTimeout(1500);
  await p1.fill('input[placeholder="Search repositories\u2026"]', "bench");
  await p1.waitForTimeout(2000);
  used = await tryClick('[role="option"]:has-text("prompt-first-bench")') || await tryClick('li:has-text("prompt-first-bench")');
  console.log("retry clicked via:", used);
}
await p1.waitForTimeout(2000);
await p1.screenshot({ path: "/Users/a1-6/Desktop/workspace/ego/arena-b8-20261024/arena-pfb-selected.png" });
console.log(await p1.snapshot());
