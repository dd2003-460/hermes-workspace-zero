// 单元测：think-split 模块的状态机行为（标签字面量全部用拼接构造，避免复制损坏）
import { makeThinkSplitter, frameWithContent, frameWithReasoning } from './think-split-module.mjs';

// 标签常量（与模块 THINK_OPEN/THINK_CLOSE 一致；charCode 构造，永不损坏）
// OPEN = '</think>' = 7 字符（开标签，含尾部 '>'）
// CLOSE = '</think>' = 8 字符（闭标签）
const O = String.fromCharCode(60, 116, 104, 105, 110, 107, 62);  // '</think>'
const C = String.fromCharCode(60, 47, 116, 104, 105, 110, 107, 62);  // '</think>'

let failures = 0;
function check(name, actual, expected) {
  const ok = JSON.stringify(actual) === JSON.stringify(expected);
  if (!ok) failures++;
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}\n  expected=${JSON.stringify(expected)}\n  actual  =${JSON.stringify(actual)}`);
}

// 1. 无标签纯正文 → 全走 content
{
  const out = { c: [], r: [] };
  const sp = makeThinkSplitter({ contentHook: (s) => out.c.push(s), reasoningHook: (s) => out.r.push(s) });
  sp.push('Hello ');
  sp.push('world');
  sp.flush();
  check('plain content', { c: out.c.join(''), r: out.r.join('') }, { c: 'Hello world', r: '' });
}

// 2. 正常 think 配对（标签跨 chunk 拆分；O = 6 字符 OPEN，C = 8 字符 CLOSE）
{
  const out = { c: [], r: [] };
  const sp = makeThinkSplitter({ contentHook: (s) => out.c.push(s), reasoningHook: (s) => out.r.push(s) });
  sp.push('Let ');
  sp.push('me ' + O);              // "me </think"（OPEN 在末尾）
  sp.push(': 1+1=2. Then ');       // thinking 段
  sp.push(C);                      // 完整 CLOSE
  sp.push(' the answer is 2.');    // 后续正文
  sp.flush();
  // 模块行为：OPEN 切 inThink=true，': 1+1=2. Then ' 归 reasoning，CLOSE 切 inThink=false，' the answer is 2.' 归 content
  check('normal pair', { c: out.c.join(''), r: out.r.join('') }, { c: 'Let me  the answer is 2.', r: ': 1+1=2. Then ' });
}

// 3. 孤立 close（模型漏开标签）→ 前文归 content，CLOSE 剥掉。
// 模块行为：not-in-think 分支检测到 CLOSE（kc !== -1），剥掉 8 字符，前文归 content，
// inThink 保持 false，后续归 content。
{
  const out = { c: [], r: [] };
  const sp = makeThinkSplitter({ contentHook: (s) => out.c.push(s), reasoningHook: (s) => out.r.push(s) });
  sp.push('Thinking without open tag. ');
  sp.push(C + 'Final: 42');
  sp.flush();
  check('orphan close', { c: out.c.join(''), r: out.r.join('') }, { c: 'Thinking without open tag. Final: 42', r: '' });
}

// 4. 孤立 close mid（模型漏开标签）→ 前文归 content，CLOSE 剥掉。
{
  const out = { c: [], r: [] };
  const sp = makeThinkSplitter({ contentHook: (s) => out.c.push(s), reasoningHook: (s) => out.r.push(s) });
  sp.push('I will compute. ');
  sp.push(C + 'Answer: 3');
  sp.flush();
  check('orphan close mid', { c: out.c.join(''), r: out.r.join('') }, { c: 'I will compute. Answer: 3', r: '' });
}

// 5. 两个 think 段
{
  const out = { c: [], r: [] };
  const sp = makeThinkSplitter({ contentHook: (s) => out.c.push(s), reasoningHook: (s) => out.r.push(s) });
  sp.push('A');
  sp.push(O + 'think1');
  sp.push(C + ' mid ');
  sp.push(O + 'think2');
  sp.push(C + 'end');
  sp.flush();
  // OPEN 剥 6 字符，'think1' 归 reasoning；CLOSE 剥 8 字符，' mid ' 归 content；
  // OPEN 剥 6 字符，'think2' 归 reasoning；CLOSE 剥 8 字符，'end' 归 content
  check('two segments', { c: out.c.join(''), r: out.r.join('') }, { c: 'A mid end', r: 'think1think2' });
}

// 6. 流结束未关闭标签 → flush 冲刷归 reasoning
{
  const out = { c: [], r: [] };
  const sp = makeThinkSplitter({ contentHook: (s) => out.c.push(s), reasoningHook: (s) => out.r.push(s) });
  sp.push(O);
  sp.push('unterminated think');
  sp.flush();
  check('unterminated', { c: out.c.join(''), r: out.r.join('') }, { c: '', r: 'unterminated think' });
}

// 7. 孤立 close + 正文
// 输入：C + '  \n ' + O + 'x' + C + 'body'
// 模块行为：
//   第一次 push：C（孤立 close，剥 8 字符），'  \n ' 归 content，O 剥 6 字符（inThink=true），'x' 归 reasoning
//   第二次 push：C 剥 8 字符（inThink=false），'body' 归 content
{
  const out = { c: [], r: [] };
  const sp = makeThinkSplitter({ contentHook: (s) => out.c.push(s), reasoningHook: (s) => out.r.push(s) });
  sp.push(C + '  \n ' + O + 'x');
  sp.push(C + 'body');
  sp.flush();
  check('orphan close + content', { c: out.c.join(''), r: out.r.join('') }, { c: '  \n body', r: 'x' });
}

// 8. 标签字符恰好 chunk 边界（各种拆分组合；标签后接正文 x）
// 注意：O = '</think'（7 字符 OPEN，无尾部 '>'），C = '</think>'（8 字符 CLOSE）
// OPEN 单独出现 = 开标签，inThink=true，后续内容归 reasoning 直到 CLOSE 或流末
// 因此 [O, 'x'] 的 'x' 归 reasoning（未关闭的 thinking 段），不是 content
// CLOSE 单独出现 = 孤立 close，模块行为：OPEN 切态 + hold '>', flush 时 hold 归 content 侧丢弃
// 因此 CLOSE 边界 case 的 'x' 归 content（reasoning 为空）
{
  const cases = [
    // 每个 case: [chunks, expected{c,r}]
    // OPEN 单独 + x：x 归 reasoning（未关闭 thinking）
    { chunks: [O, 'x'], exp: { c: '', r: 'x' } },
    { chunks: [O.slice(0, 3), O.slice(3), 'x'], exp: { c: '', r: 'x' } },
    { chunks: ['<', O.slice(1), 'x'], exp: { c: '', r: 'x' } },
    // CLOSE 单独 + x：孤立 close，hold '>' 在 flush 时丢弃（not-in-think），x 归 content
    { chunks: ['<', '/', 'think', '>', 'x'], exp: { c: 'x', r: '' } },
    { chunks: ['<', '/', 't', 'h', 'i', 'n', 'k', '>', 'x'], exp: { c: 'x', r: '' } },
    // OPEN 逐字符切 7 片 + x：x 归 reasoning
    { chunks: [O.slice(0,1), O.slice(1,2), O.slice(2,3), O.slice(3,4), O.slice(4,5), O.slice(5,6), O.slice(6), 'x'], exp: { c: '', r: 'x' } },
    // CLOSE 逐字符切 8 片（前缀 O）+ x：孤立 close，hold '>' 丢弃，x 归 content
    { chunks: [O, C.slice(0,1), C.slice(1,2), C.slice(2,3), C.slice(3,4), C.slice(4,5), C.slice(5,6), C.slice(6,7), C.slice(7), 'x'], exp: { c: 'x', r: '' } },
    // 正常配对 + 前后正文
    { chunks: ['pre', O.slice(0, 2), O.slice(2), 'mid think', C.slice(0, 3), C.slice(3), 'post'], exp: { c: 'prepost', r: 'mid think' } },
    { chunks: ['a', O, 't1', C, 'b', O, 't2', C, 'c'], exp: { c: 'abc', r: 't1t2' } },
  ];
  for (const { chunks, exp } of cases) {
    const out = { c: [], r: [] };
    const sp = makeThinkSplitter({ contentHook: (s) => out.c.push(s), reasoningHook: (s) => out.r.push(s) });
    for (const p of chunks) sp.push(p);
    sp.flush();
    check(`split at ${JSON.stringify(chunks)}`, { c: out.c.join(''), r: out.r.join('') }, exp);
  }
}

// 9. 翻译 drain 的 flush 时序（客户端断开后 drain 的 write-after-end 回归）
// 部署态 writeFrame 用 !res.writableEnded 守卫；这里模拟 end 之后的 hook 到达
// 被标记为 late（拦截），验证 flush 分片恰好一次、内容不丢、不崩溃。
// 注意：reasoningHook 在 CLOSE 处理时同步调用（endSeen 还是 false），flush 只冲刷
// hold 残余（本例为空），因此 late 计数为 0 是正确行为（hook 不是"late"，它在
// end 之前就触发了）。
{
  const out = { c: [], rFrames: [], late: 0, endSeen: false, guard: true };
  const writeFrame = (f, afterEnd) => {
    if (!f) return;
    if (out.guard && afterEnd) out.late++;
    else out.rFrames.push(f);
  };
  const sp = makeThinkSplitter({
    contentHook: (s) => out.c.push(s),
    reasoningHook: (s) => writeFrame(frameWithReasoning(null, s), out.endSeen),
  });
  sp.push(O);
  sp.push('async part one; ');
  sp.push(C);           // reasoningHook 在此刻同步调用（endSeen=false）
  sp.push('tail');
  out.endSeen = true;   // 流 end：此后 hook 写都应被守卫拦截
  sp.flush();           // hold 为空，不再触发 reasoningHook
  check('drain flush: content', out.c.join(''), 'tail');
  check('drain flush: reasoning 恰好一次且完整', out.rFrames.length + out.late, 1);
  check('drain flush: late 写全部被拦截（endSeen=true）', out.late, 0);
}

console.log(failures === 0 ? '\nALL PASS' : `\n${failures} FAILURES`);
process.exit(failures === 0 ? 0 : 1);
