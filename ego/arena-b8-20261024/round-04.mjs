const task = await taskSpace(535);
const p1 = task.page("p1");
await p1.click('button:has-text("-orf")', { label: "open repo dropdown" });
await p1.waitForTimeout(1200);
await p1.fill('input[placeholder="Search repositories..."]', "bench");
await p1.waitForTimeout(2000);
await p1.screenshot({ path: "/Users/a1-6/Desktop/workspace/ego/arena-b8-20261024/arena-search-bench.png" });
console.log(await p1.snapshot());
