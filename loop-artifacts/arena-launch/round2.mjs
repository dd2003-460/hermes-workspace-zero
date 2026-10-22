const task = await taskSpace('arena-launch-prompt-first-20261022');
const p1 = task.page('p1');
await p1.click('@35', { label: 'open repo dropdown' });
await p1.waitForTimeout(1500);
console.log(await p1.snapshot());
