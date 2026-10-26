const task = await taskSpace("arena-b8-episodes-20261024");
const p1 = task.page("p1");
await p1.goto("https://arena.ai/agent");
await p1.waitForLoadState("domcontentloaded");
await p1.waitForTimeout(4000);
console.log({ spaceId: task.spaceId, url: await p1.url(), title: await p1.title() });
console.log(await p1.snapshot());
