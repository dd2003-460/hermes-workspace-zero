const t = await taskSpace('memory-hook-plugin');
const p = t.page('p1');
// 等生成停止：Send message 按钮重新出现（生成中是 Stop generating）
const ok = await p.waitForFunction(
  () => {
    const btn = document.querySelector('button[aria-label="Send message"]');
    return !!btn;
  },
  undefined,
  { timeout: 420000, polling: 5000 }
);
console.log('stopped', ok);
await p.waitForTimeout(3000);
const s = await p.snapshot({ scope: 'full_page' });
const fs = await import('node:fs/promises');
await fs.writeFile('/Users/a1-6/Desktop/workspace/loop-artifacts/tmp-mh-research/ego/snap4.txt', s);
console.log('len', s.length);
