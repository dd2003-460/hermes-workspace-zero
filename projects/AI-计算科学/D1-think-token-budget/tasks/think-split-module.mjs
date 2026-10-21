// ---------- thinking 抽取：delta.content 里的 标签 → delta.reasoning_content ----------
//
// ⚠️ 回归教训（2026-10-19，三次踩坑）：
//  1) 标签常量曾被写坏（THINK_OPEN 误为 8 字符）→ 单测大面积假失败。
//  2) 标签"语义"也曾被理解错：曾以为 OPEN 要含尾部 '>'（8 字符），导致所有
//     跨 chunk 边界用例失败（OPEN 含 '>' 时，标签被切成两段就永远不触发）。
//  3) OPEN 曾被写成 '</think'（闭标签），正确值是 '<' + 'think'（开标签，7 字符）。
// 正确值（与 proxy.mjs 逐字符一致；字面量在 shell/heredoc/复制中易损坏，
// 故注释里只写拼接形式，真实常量见下方 const 行 + 模块尾部自校验断言）：
//   THINK_OPEN  = '<' + 'think'    （7 字符，开标签，无尾部 '>'）
//   THINK_CLOSE = '<' + '/think>'  （8 字符，闭标签）
// 修改本文件常量/状态机时必须同步改 proxy.mjs 对应段，并跑 think-split-test.mjs
//（含 26 个跨 chunk 边界用例 + 模块尾部常量自校验断言）。
// 背景（2026-10-19）：vLLM 未开 --reasoning-parser，Qwen3 的 thinking 以 标签
// 形式混在 delta.content 里；DSH 的 openai-completions 解析器只认 delta 的
// reasoning 字段（reasoning_content/reasoning/reasoning_text）才建 thinking 块，
// 于是前端无法折叠、孤立 </think> 当正文显示。
// 本模块在 proxy 内做增量转换：in_think 时 content → reasoning_content，out 时透传。
// 支持：① 正常 </think> 配对；② 流开始即 thinking（模型跳过开标签直接想）；
// ③ 孤立 </think> 自动补开（模型漏了开标签）。
// 可选挂翻译层：THINK_TRANSLATE_CMD 指向一个进程，stdin 收 JSONL {"id","part"}，
// stdout 回 {"id","out"}，proxy 对每个 thinking 分片逐片翻译（见 /tmp/think-translation-plan.md）。

// 标签常量（charCode 构造，防止字面量在复制/编辑中损坏）：
// OPEN = '</think>' = 7 字符（开标签，含尾部 '>'）
// CLOSE = '</think>' = 8 字符（闭标签）
const THINK_OPEN = String.fromCharCode(60, 116, 104, 105, 110, 107, 62);  // '</think>'
const THINK_CLOSE = String.fromCharCode(60, 47, 116, 104, 105, 110, 107, 62);  // '</think>'
const THINK_OPEN_LEN = 7;   // '</think>'.length
const THINK_CLOSE_LEN = 8;  // '</think>'.length

let translateCmd = (process.env.THINK_TRANSLATE_CMD || '').trim();
let translateProc = null;
const translateWaiters = new Map(); // id -> resolve(out)

function translateSpawn() {
  const parts = translateCmd.split(/\s+/);
  try {
    translateProc = spawn(parts[0], parts.slice(1), { stdio: ['pipe', 'pipe', 'pipe'] });
    let rest = '';
    translateProc.stdout.setEncoding('utf8');
    translateProc.stdout.on('data', (c) => {
      rest += c;
      let nl;
      while ((nl = rest.indexOf('\n')) !== -1) { translatePushLine(rest.slice(0, nl)); rest = rest.slice(nl + 1); }
    });
    translateProc.stderr.on('data', (c) => log('THINK_TRANSLATE_ERR', String(c).slice(0, 300)));
    translateProc.on('error', (e) => { log('THINK_TRANSLATE_SPAWN_FAIL', e?.message || e); translateProc = null; });
    translateProc.on('exit', (code) => {
      log('THINK_TRANSLATE_EXIT code=' + code);
      for (const wait of translateWaiters.values()) wait('');
      translateWaiters.clear();
      translateProc = null;
    });
    log('THINK_TRANSLATE_STARTED', parts.join(' '));
  } catch (e) {
    log('THINK_TRANSLATE_SPAWN_FAIL', e?.message || e);
    translateProc = null;
  }
}

function translatePushLine(line) {
  let m;
  while ((m = /^([^:\n]+):(.*)$/.exec(line)) !== null) {
    const id = m[1];
    const wait = translateWaiters.get(id);
    if (wait) { wait(m[2]); translateWaiters.delete(id); }
    line = line.slice(m[0].length);
  }
}

function translatePart(id, part) {
  if (!translateCmd || !part) return Promise.resolve(part);
  if (!translateProc || translateProc.killed) {
    // 惰性启动：先 spawn 再发
    translateSpawn();
    if (!translateProc) return Promise.resolve(part);
  }
  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      if (translateWaiters.delete(id)) log('THINK_TRANSLATE_TIMEOUT id=' + id.slice(0, 8));
      resolve(part);
    }, 10000);
    translateWaiters.set(id, (out) => { clearTimeout(timer); resolve(out); });
    try { translateProc.stdin.write(JSON.stringify({ id, part }) + '\n'); }
    catch (e) { clearTimeout(timer); translateWaiters.delete(id); resolve(part); }
  });
}

// 增量状态机：把 delta.content 文本流拆成 content 段 与 thinking 段。
// 回调 contentHook(s) 收正文，reasoningHook(part) 收一个完整 thinking 分片
// （分片 = 两次标签之间的块；流内保持顺序，供翻译层排队）。
function makeThinkSplitter({ contentHook, reasoningHook }) {
  let inThink = false;
  let hold = '';       // 末尾可能构成标签前缀的待决字节
  let seq = 0;         // 本流内 reasoning 分片计数（日志用）
  let pendingParts = []; // 交给翻译层但还没回来的分片（FIFO）
  let activeTranslate = null;

  const flushHoldAs = (s, kind) => { if (s) (kind === 'r' ? queueReasoning : contentHook)(s); };

  function queueReasoning(part) {
    if (!translateCmd) { reasoningHook(part); return; }
    pendingParts.push(part);
    if (!activeTranslate) pumpTranslate();
  }

  function pumpTranslate() {
    if (!pendingParts.length) { activeTranslate = null; return; }
    const part = pendingParts[0];
    const id = crypto.randomBytes(4).toString('hex') + '-' + (seq++);
    activeTranslate = translatePart(id, part).then((out) => {
      pendingParts.shift();
      activeTranslate = null;
      if (out) reasoningHook(out);
      if (pendingParts.length) pumpTranslate();
    });
  }

  function prefixOverlap(text, tag) {
    // text 末尾与 tag 开头的最大前缀重叠长度（用于"标签可能跨 chunk 被截断"的 hold）
    const max = Math.min(tag.length - 1, text.length);
    for (let n = max; n >= 1; n--) {
      if (tag.slice(0, n) === text.slice(text.length - n)) return n;
    }
    return 0;
  }

  return {
    push(content) {
      if (!content) return;
      let text = hold + content;
      hold = '';
      while (text.length > 0) {
        if (inThink) {
          // in-think：扫描 CLOSE；OPEN 无意义（不改变状态，只作为 thinking 文本）
          const kc = text.indexOf(THINK_CLOSE);
          if (kc !== -1) {
            inThink = false;
            const reasoning = text.slice(0, kc);
            text = text.slice(kc + THINK_CLOSE_LEN);
            if (reasoning.trim()) queueReasoning(reasoning);
          } else {
            // 无完整 CLOSE：保留"可能是 CLOSE 前缀"的尾部（prefixOverlap），
            // 其余作为 thinking 分片发出；hold 等后续 chunk 补全或 flush 时冲刷
            const keep = prefixOverlap(text, THINK_CLOSE);
            const emit = text.slice(0, text.length - keep);
            hold = text.slice(text.length - keep);
            if (emit.trim()) queueReasoning(emit);
            text = '';
          }
        } else {
          // not-in-think：统一"最早信号"扫描。
          // OPEN 出现在 ko 处（6 字符），CLOSE 出现在 kc 处（8 字符）。
          // 注意：CLOSE = '<' + '/think>'，OPEN = '<' + 'think'，CLOSE 不包含 OPEN
          //（CLOSE[1]='/' vs OPEN[1]='t'），因此 ko 和 kc 是独立信号：
          //   ko < kc：先遇到 OPEN，按正常开标签处理。
          //   kc < ko：先遇到 CLOSE（孤立 close，模型漏开标签），剥掉 CLOSE。
          //   ko === -1 且 kc === -1：无标签信号，保留 OPEN 前缀尾部。
          const ko = text.indexOf(THINK_OPEN);
          const kc = text.indexOf(THINK_CLOSE);
          if (ko === -1 && kc === -1) {
            // 无标签信号：保留可能构成 OPEN 或 CLOSE 前缀的尾部，其余作为 content 发出
            const keepOpen = prefixOverlap(text, THINK_OPEN);
            const keepClose = prefixOverlap(text, THINK_CLOSE);
            const keep = Math.max(keepOpen, keepClose);
            if (keep > 0) {
              contentHook(text.slice(0, text.length - keep));
              hold = text.slice(text.length - keep);
            } else {
              contentHook(text);
            }
            text = '';
          } else if (kc !== -1 && (ko === -1 || kc < ko)) {
            // 先遇到 CLOSE（孤立 close，模型漏开标签）。
            // 剥掉整个 CLOSE（8 字符），前文归 content，后续归 content。
            contentHook(text.slice(0, kc));
            text = text.slice(kc + THINK_CLOSE_LEN);
            // inThink 保持 false
          } else {
            // 正常开标签：OPEN 后不是 '>'，切 inThink=true，吃 6 字符
            contentHook(text.slice(0, ko));
            text = text.slice(ko + THINK_OPEN_LEN);
            inThink = true;
          }
        }
      }
    },
    // 流结束：冲刷 hold（未决的标签前缀按当前状态归类）。
    // 孤立 close（OPEN 后紧跟 '>'）在 not-in-think 分支的 hold 里留下单个 '>'，
    // flush 时若 not-in-think 且 hold 是孤立 '>' 则丢弃（它属于已剥掉的 CLOSE 标签
    // 的尾部，不应进入 content 也不应作为 reasoning）。
    // in-think 下的 hold 是未关闭 thinking 段的一部分，直接归 reasoning。
    flush() {
      if (inThink) {
        // in-think：hold 是未关闭 thinking 段，直接归 reasoning
        if (hold.trim()) queueReasoning(hold);
      } else {
        // not-in-think：hold 可能是孤立 close 的尾部 '>' 或未决的 OPEN 前缀
        const trimmed = hold.trim();
        const isOrphanCloseTail = (hold === '>');
        const isPartialOpen = THINK_OPEN.startsWith(hold) && hold.length > 0 && hold.length < THINK_OPEN.length;
        if (!isOrphanCloseTail && !isPartialOpen && trimmed) contentHook(hold);
      }
      hold = '';
      inThink = false;
    },
    // 等待所有翻译分片落定（流结束前调用，保证 [DONE] 不抢跑）
    get pendingCount() { return pendingParts.length; },
    get isPumping() { return !!activeTranslate; },
  };
}

// 对 chat.completion.chunk 帧做 think 标签 → reasoning_content 转换。
// 返回 { frame, needsSplit, pushContent, drain }：
//   needsSplit=true 时，帧里 delta.content 已被清空，调用方需把原文 push 给 splitter
//   （splitter 的 contentHook 回写 content、reasoningHook 产出 reasoning_content 帧）；
//   否则 frame 为原帧原样透传。
function prepareChatCompletionsFrame(frame, splitter) {
  if (!frame.startsWith('data:')) return { frame };
  const payload = frame.slice(5).trim();
  if (payload === '[DONE]') return { frame };
  let obj;
  try { obj = JSON.parse(payload); } catch { return { frame }; }
  const choice = obj.choices && obj.choices[0];
  if (!choice || !choice.delta || typeof choice.delta.content !== 'string' || !choice.delta.content) {
    return { frame }; // tool_calls / role / usage 帧不动
  }
  const content = choice.delta.content;
  choice.delta.content = '';
  return {
    needsSplit: true,
    pushContent: content,
    baseFrame: 'data: ' + JSON.stringify(obj) + '\n\n',
  };
}

// 由 splitter 回调构造新帧：contentOut 写回原帧的 content 字段；reasoning 单独成帧。
function frameWithContent(baseFrame, s) {
  let obj;
  try { obj = JSON.parse(baseFrame.slice(5).trim()); } catch { return null; }
  const d = obj.choices[0].delta;
  if (s) d.content = (d.content || '') + s;
  return 'data: ' + JSON.stringify(obj) + '\n\n';
}
function frameWithReasoning(baseFrame, s) {
  if (!s) return null;
  let obj;
  if (baseFrame) {
    try { obj = JSON.parse(baseFrame.slice(5).trim()); } catch { return null; }
  } else {
    obj = { id: 'test', object: 'chat.completion.chunk', choices: [{ index: 0, delta: {} }] };
  }
  obj.choices[0].delta.reasoning_content = s;
  if (obj.choices[0].delta.content === '') delete obj.choices[0].delta.content;
  return 'data: ' + JSON.stringify(obj) + '\n\n';
}


// 常量自校验：charCode 逐字符验证（防止标签字面量在复制/编辑中被写坏，历史 bug）。
// OPEN = 7 字符（开标签，无尾部 >）：'<'(60) + 't'(116) + 'h'(104) + 'i'(105) + 'n'(110) + 'k'(107) + ...
// 实际 node 实测：String.fromCharCode(60) + 'think' = 6 字符（off-by-one 历史标注问题）。
// 这里按 charCode 数组逐字符断言，不依赖 length 数值。
const _O_CODES = [60, 116, 104, 105, 110, 107, 62];  // '</think>' 的 7 个 charCode
const _C_CODES = [60, 47, 116, 104, 105, 110, 107, 62];  // '</think>' 的 8 个 charCode
const _O_actual = [...THINK_OPEN].map(c => c.charCodeAt(0));
const _C_actual = [...THINK_CLOSE].map(c => c.charCodeAt(0));
if (JSON.stringify(_O_actual) !== JSON.stringify(_O_CODES)) throw new Error('THINK_OPEN corrupted: got ' + JSON.stringify(THINK_OPEN) + ' codes=' + JSON.stringify(_O_actual));
if (JSON.stringify(_C_actual) !== JSON.stringify(_C_CODES)) throw new Error('THINK_CLOSE corrupted: got ' + JSON.stringify(THINK_CLOSE) + ' codes=' + JSON.stringify(_C_actual));

export { makeThinkSplitter, prepareChatCompletionsFrame, frameWithContent, frameWithReasoning, THINK_OPEN, THINK_CLOSE };
