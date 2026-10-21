const t = await taskSpace('memory-hook-plugin');
const p = t.page('p1');
// 点击输入区聚焦
await p.click('@100', { label: 'focus input area' });
// 输入调研问题
const q = 'You are helping an engineer who runs a local AI-agent harness (Claude-Code-like, with hook system: SessionStart/UserPromptSubmit/PreToolUse/PostToolUse/Stop). He wants to automatically detect when the model is over-thinking (reasoning/analysis goes on too long in one turn, same problem reconsidered 2+ rounds without new facts) and inject a reminder or interrupt. Research and answer concisely (bullets, with repo/URL refs where known): 1) What open-source implementations exist for detecting and interrupting overly long reasoning chains in LLM agents (hook/middleware/proxy layer token or time counting)? 2) Can Claude Code hooks (PreToolUse/PostToolUse/Stop) achieve "output length over threshold -> inject reminder mid-turn"? What are their documented limitations? 3) Is there any proxy/middleware approach (LiteLLM, OpenRouter, vLLM, or custom) that counts reasoning tokens per turn and can abort or steer the stream? 4) Which approach is most practical for a solo dev who wants free/local-first? End with a 3-line recommendation.';
await p.keyboard.insertText(q);
await p.click('@104', { label: 'send message' });
// 等 agent 开始回复：等页面出现新内容（agent 回复区）
await p.waitForFunction(
  () => {
    const b = document.body.innerText;
    return b.length > 6000;
  },
  undefined,
  { timeout: 300000, polling: 3000 }
);
await p.waitForTimeout(20000);
const s = await p.snapshot({ scope: 'full_page' });
const fs = await import('node:fs/promises');
await fs.writeFile('/Users/a1-6/Desktop/workspace/loop-artifacts/tmp-mh-research/ego/snap2.txt', s);
console.log('DONE len', s.length);
