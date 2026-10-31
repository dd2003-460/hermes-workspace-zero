const task = await taskSpace(535);
const p1 = task.page("p1");
// Click the input area ("Ask anything…")
await p1.click('container:has-text("Ask anything")', { timeout: 5000 }).catch(async()=>{
  await p1.click('text=Ask anything');
});
await p1.waitForTimeout(1000);
await p1.screenshot({ path: "/Users/a1-6/Desktop/workspace/ego/arena-b8-20261024/arena-input-focused.png" });
console.log(await p1.snapshot());
