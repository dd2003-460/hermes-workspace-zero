const task = await taskSpace(535);
const p1 = task.page("p1");
await p1.waitForTimeout(5000);
await p1.screenshot({ path: "/Users/a1-6/Desktop/workspace/ego/arena-b8-20261024/arena-submit-confirm.png" });
console.log("URL:", await p1.url());
console.log(await p1.snapshot());
