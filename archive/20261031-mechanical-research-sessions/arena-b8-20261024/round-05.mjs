const task = await taskSpace(535);
const p1 = task.page("p1");
await p1.screenshot({ path: "/Users/a1-6/Desktop/workspace/ego/arena-b8-20261024/arena-state-now.png" });
console.log(await p1.snapshot());
