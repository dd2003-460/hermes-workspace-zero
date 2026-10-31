const task = await taskSpace(535);
const p1 = task.page("p1");
const shot = await p1.screenshot({ path: "/Users/a1-6/Desktop/workspace/ego/arena-b8-20261024/arena-repo-dropdown.png" });
console.log("screenshot saved", shot);
// Try clicking the repo dropdown via its ref text and capture immediately
await p1.click('button:has-text("-orf")', { label: "open repo dropdown" });
await p1.waitForTimeout(2500);
const shot2 = await p1.screenshot({ path: "/Users/a1-6/Desktop/workspace/ego/arena-b8-20261024/arena-after-click.png" });
console.log("after-click screenshot saved", shot2);
console.log(await p1.snapshot());
