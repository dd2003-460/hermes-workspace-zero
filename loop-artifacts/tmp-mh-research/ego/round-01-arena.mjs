const task = await taskSpace('memory-hook-plugin');
const page = task.page('p1');
await page.goto('https://arena.ai/agent');
await page.waitForLoadState();
const s1 = await page.snapshot();
console.log('=== SNAPSHOT 1 (arena agent page) ===');
console.log(s1.slice(0, 4000));
