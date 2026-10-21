const t = await taskSpace('memory-hook-plugin');
const p = t.page('p1');
const r = await p.evaluate(() => {
  // 找到对话消息区（含 "Reasoning budget exceeded" 的容器是答案区）
  const all = Array.from(document.querySelectorAll('div, section, article'));
  // 策略：找包含 "recommendation" 且文本最长的元素
  let best = null;
  for (const el of all) {
    const txt = el.innerText || '';
    if (txt.includes('1)') && (txt.includes('proxy') || txt.includes('llama.cpp')) && txt.length > 2000) {
      if (!best || el.innerText.length < best.length) best = el.innerText;
    }
  }
  // 备选：整个 main/center 区域
  const main = document.querySelector('main') || document.querySelector('[role="main"]');
  return { answer: best, mainLen: main ? main.innerText.length : -1, bodyLen: document.body.innerText.length };
});
const fs = await import('node:fs/promises');
if (r.answer) {
  await fs.writeFile('/Users/a1-6/Desktop/workspace/loop-artifacts/tmp-mh-research/ego/answer.txt', r.answer);
  console.log('ANSWER_LEN', r.answer.length);
} else {
  console.log('NO_ANSWER_FOUND mainLen', r.mainLen, 'bodyLen', r.bodyLen);
  const txt = await p.evaluate(() => document.body.innerText);
  await fs.writeFile('/Users/a1-6/Desktop/workspace/loop-artifacts/tmp-mh-research/ego/body.txt', txt);
  console.log('BODY_DUMPED', txt.length);
}
