const task = await taskSpace(535);
const p1 = task.page("p1");
await p1.click('button:has-text("-orf")');
await p1.waitForTimeout(1800);
await p1.screenshot({ path: "/Users/a1-6/Desktop/workspace/ego/arena-b8-20261024/arena-dropdown-open.png" });
console.log(await p1.snapshot());
