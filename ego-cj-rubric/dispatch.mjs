// CJ-RUBRIC-ALIGN dispatch to arena session 01a195cb
const task = await taskSpace('cj-rubric-align-dispatch');
const p1 = task.page('p1');

// Restore window (needed for reliable interaction)
try {
  const w = await p1.cdp("Browser.getWindowForTarget", {});
  if (w.bounds && w.bounds.windowState !== 'normal') {
    await p1.cdp("Browser.setWindowBounds", { windowId: w.windowId, bounds: { left: 0, top: 33, width: 1728, height: 1084, windowState: "normal" } });
    await p1.waitForTimeout(2000);
  }
} catch(e) { console.log('window restore skip:', e.message?.slice(0,60)); }

await p1.goto('https://arena.ai/agent/01a195cb-50ba-7cfa-9bcd-cdf74a614e63');
await p1.waitForTimeout(8000);

// Check for "继续工作" button (locked composer state)
const hasContinue = await p1.evaluate(() => {
  const btns = [...document.querySelectorAll('button')];
  return btns.some(b => b.textContent.trim() === '继续工作' && b.offsetParent !== null);
});
if (hasContinue) {
  console.log('Found 继续工作 button, clicking...');
  await p1.evaluate(() => {
    const btn = [...document.querySelectorAll('button')].find(b => b.textContent.trim() === '继续工作' && b.offsetParent !== null);
    if (btn) btn.click();
  });
  await p1.waitForTimeout(5000);
}

// Check for running indicator
const isRunning = await p1.evaluate(() => document.body.innerText.includes('Stop generating'));
console.log('isRunning:', isRunning);

if (isRunning) {
  console.log('Agent still running from previous task. Waiting...');
  // Poll until done (max 5 min)
  for (let i = 0; i < 10; i++) {
    await p1.waitForTimeout(30000);
    const still = await p1.evaluate(() => document.body.innerText.includes('Stop generating'));
    console.log(`poll ${i+1}: still running =`, still);
    if (!still) break;
  }
  // Re-check for continue button after run completes
  const hasCont2 = await p1.evaluate(() => {
    const btns = [...document.querySelectorAll('button')];
    return btns.some(b => b.textContent.trim() === '继续工作' && b.offsetParent !== null);
  });
  if (hasCont2) {
    await p1.evaluate(() => {
      const btn = [...document.querySelectorAll('button')].find(b => b.textContent.trim() === '继续工作' && b.offsetParent !== null);
      if (btn) btn.click();
    });
    await p1.waitForTimeout(5000);
  }
}

// Find the composer (tiptap ProseMirror or contenteditable)
const msg = `本任务只涉及 prompt-first-bench/arena/4a614e63-prompt-first-bench，忽略历史中其他仓库的消息。

新任务：CJ-RUBRIC-ALIGN（判官口径对齐）

请先执行：
git pull origin arena/4a614e63-prompt-first-bench

然后读取 tasks/TASK-cj-rubric-align.md，严格按其中步骤和仓库内 loop/prompt-first/ 阶段执行（01→04.5）。

核心目标：修改 experiments/stage-ablation/cross_judge.py 的 JUDGE_PROMPT，使本地 27B 判官与 arena 异源判官在 90 cell 上 M1 达到 spearman ρ≥0.6 + arm 排序一致。

注意：
- 你的沙箱无法访问 127.0.0.1:8787（本地 vLLM），所以 C2 步骤（本地重跑）由 Lead 补跑。你负责 A1/A2/B1-B3/C1/C3 设计+代码+调研，C2 交付冻结脚本即可。
- 产出落盘 loop-artifacts/stages/ + runs/
- 完成后 commit + push 到当前分支
- 回执必须含 repo URL + branch + commit_sha`;

const editorFound = await p1.evaluate((text) => {
  // Try tiptap ProseMirror first
  let ed = document.querySelector('.tiptap.ProseMirror');
  if (!ed) ed = document.querySelector('[contenteditable="true"]');
  if (!ed) return { found: false };
  ed.focus();
  return { found: true, tag: ed.tagName, cls: ed.className.slice(0, 50) };
}, msg);
console.log('editor:', JSON.stringify(editorFound));

if (!editorFound.found) {
  console.log('ABORT: no editor found');
  process.exit(1);
}

// Inject text via execCommand
await p1.evaluate((text) => {
  let ed = document.querySelector('.tiptap.ProseMirror') || document.querySelector('[contenteditable="true"]');
  ed.focus();
  document.execCommand('insertText', false, text);
}, msg);
await p1.waitForTimeout(2000);

// Verify text landed
const textLen = await p1.evaluate(() => {
  const ed = document.querySelector('.tiptap.ProseMirror') || document.querySelector('[contenteditable="true"]');
  return ed ? (ed.innerText || '').length : -1;
});
console.log('injected text length:', textLen);
if (textLen < 100) {
  console.log('ABORT: text too short, injection failed');
  process.exit(1);
}

// Click send
const sendClicked = await p1.evaluate(() => {
  const btn = [...document.querySelectorAll('button')].find(x => x.getAttribute('aria-label') === 'Send message');
  if (btn && !btn.disabled) { btn.click(); return true; }
  // Fallback: find any send-like button
  const alt = [...document.querySelectorAll('button')].find(x => /send|发送/i.test(x.textContent + ' ' + (x.getAttribute('aria-label')||'')));
  if (alt && !alt.disabled) { alt.click(); return 'alt'; }
  return false;
});
console.log('send clicked:', sendClicked);
await p1.waitForTimeout(5000);

// Verify: check for running indicator
const nowRunning = await p1.evaluate(() => document.body.innerText.includes('Stop generating'));
console.log('after send, isRunning:', nowRunning);

// Minimize window
try {
  const w = await p1.cdp("Browser.getWindowForTarget", {});
  if (w.bounds && w.bounds.windowState !== 'minimized') {
    await p1.cdp("Browser.setWindowBounds", { windowId: w.windowId, bounds: { windowState: "minimized" } });
    console.log('window minimized');
  }
} catch(e) { console.log('minimize skip:', e.message?.slice(0,60)); }

console.log('DISPATCH COMPLETE');