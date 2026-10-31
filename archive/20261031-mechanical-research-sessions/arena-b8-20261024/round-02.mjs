const task = await taskSpace(535);
const p1 = task.page("p1");
// Click the repo selector to inspect current binding and options
await p1.click("button:has-text('dd2003-460')", { label: "click repo selector" });
await p1.waitForTimeout(1500);
console.log(await p1.snapshot());
