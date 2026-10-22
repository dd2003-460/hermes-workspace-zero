const task = await taskSpace('arena-launch-prompt-first-20261022');
const p1 = task.page('p1');
await p1.goto('https://arena.ai/agent');
await p1.waitForLoadState('domcontentloaded');
await p1.waitForTimeout(3000);
console.log(await p1.snapshot());
