// count-tokens.js — R3.2 run2 成本结构测量脚本（token 实测锚点）
// 环境：node v22.22.3；依赖：gpt-tokenizer@2（registry.npmjs.org，npm i --no-save gpt-tokenizer）
// 用法：node bench/r3/run2/count-tokens.js > bench/r3/run2/token-counts.txt
// 输出：规则负载 / 任务书 / V0 vs V4 pilot 输出 / r1 工件 / r2 回执 的 o200k+cl100k token 数
const fs = require('fs');
const path = require('path');
const { encode: encO200k } = require('gpt-tokenizer/encoding/o200k_base');
const { encode: encCl100k } = require('gpt-tokenizer/encoding/cl100k_base');

const REPO = path.resolve(__dirname, '..', '..', '..');

function countFile(p) {
  const text = fs.readFileSync(p, 'utf8');
  return {
    file: path.relative(REPO, p),
    bytes: Buffer.byteLength(text, 'utf8'),
    o200k: encO200k(text).length,
    cl100k: encCl100k(text).length,
  };
}

function report(name, files) {
  const rows = files.map(countFile);
  console.log(`\n== ${name} ==`);
  for (const r of rows) console.log(`${r.file}\t${r.bytes}B\to200k=${r.o200k}\tcl100k=${r.cl100k}`);
  const s = rows.reduce((a, r) => ({ bytes: a.bytes + r.bytes, o200k: a.o200k + r.o200k, cl100k: a.cl100k + r.cl100k }), { bytes: 0, o200k: 0, cl100k: 0 });
  console.log(`TOTAL\t${s.bytes}B\to200k=${s.o200k}\tcl100k=${s.cl100k}`);
  return s;
}

const ruleFiles = fs.readdirSync(path.join(REPO, 'loop/prompt-first')).filter(f => f.endsWith('.md'))
  .map(f => path.join(REPO, 'loop/prompt-first', f))
  .concat([path.join(REPO, 'sop/arena-loop-pipeline.md')]);
report('RULE LOAD (loop/prompt-first/*.md + sop/arena-loop-pipeline.md)', ruleFiles);

report('BRIEFS', [
  path.join(REPO, 'tasks/003-self-optimization-tester.md'),
  path.join(REPO, 'bench/r3/run2/task-brief.md'),
  path.join(REPO, 'bench/self-opt-tester/new-goal-20261023.md'),
]);

const pilotDir = path.join(REPO, 'bench/runs/round3-research-pilot/qwen3.6-plus');
const s0 = report('V0 RUN OUTPUTS (bare prompt)', fs.readdirSync(pilotDir).filter(f => /v0-run1\.md$/.test(f)).map(f => path.join(pilotDir, f)));
const s4 = report('V4 RUN OUTPUTS (full 1-loop)', fs.readdirSync(pilotDir).filter(f => /v4-run1\.md$/.test(f)).map(f => path.join(pilotDir, f)));
console.log(`\nV4/V0 output-token ratio (o200k): ${(s4.o200k / s0.o200k).toFixed(2)}x  (${s0.o200k} -> ${s4.o200k})`);

// V4 pilot 发送 prompt 内嵌规则卡（## 发送 prompt 原文 代码块）
console.log('\n== V4 SENT-PROMPT EMBEDDED RULE CARD ==');
for (const f of fs.readdirSync(pilotDir).filter(f => /v4-run1\.md$/.test(f)).sort()) {
  const t = fs.readFileSync(path.join(pilotDir, f), 'utf8');
  const m = t.match(/## 发送 prompt 原文\s*\n+\s*```\n([\s\S]*?)\n```\n/);
  if (m) console.log(`${f}\tsent-prompt=${encO200k(m[1]).length} o200k tokens`);
}

const art = [];
for (const d of ['01', '02', '02.5', '03', '04', '04.5']) {
  const p = path.join(REPO, 'bench/self-opt-tester/loop-artifacts/stages', d);
  if (fs.existsSync(p)) fs.readdirSync(p).filter(f => f.endsWith('.md')).forEach(f => art.push(path.join(p, f)));
}
report('R1 LOOP ARTIFACTS (stages 01-04.5)', art);

report('R2 CROSS-CHECK RECEIPTS (web-llm)', fs.readdirSync(path.join(REPO, 'bench/self-opt-tester/r2/web-llm'))
  .filter(f => f.endsWith('.json')).map(f => path.join(REPO, 'bench/self-opt-tester/r2/web-llm', f)));

console.log('\nDONE exit 0');
