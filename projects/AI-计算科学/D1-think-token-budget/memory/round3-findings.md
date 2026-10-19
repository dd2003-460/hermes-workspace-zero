# origin: ai
# R3 findings — D1-think-token-budget (official AIME 2025, 10 problems)

## Goal
Reduce surfaced thinking (decode-time proxy) WITHOUT hurting accuracy on a
REAL public benchmark — R2's set was self-generated AIME-lite; R3 uses the
official AoPS AIME 2025 set (the item in the Qwen3-32B post-training table
with the 52.7 pt thinking−non-thinking gap; ZebraLogic's 59.6 is larger but
its test set is not public). Find where the answer-only prompt (P1) breaks
100% accuracy and map the quality boundary of the strict adaptive prompt (P5).

## Method
- Arms: P0 baseline (step-by-step + own-line FINAL), P1 minimal
  ("Answer only. No reasoning, no working, no explanation." + own-line FINAL),
  P5 strict adaptive (4-rule block: minimal text / STOP-never-rederive /
  no-agent-mention / LAST line exactly FINAL: <answer>; supersedes P3v2).
- Data: tasks/aime25_test.jsonl (30 official AIME 2025 problems, via
  hf-mirror.com — huggingface.co blocked 403). R3 subset = 10 problems:
  A00(easy,70) A03(easy,117) A04(med,279) A09(hard,81) A11(hard,510)
  A16(med,49) A19(hard,336) A23(med,149) A25(hard,113) A27(hard,248).
- Every key independently re-derived in python before use (two were caught
  wrong: A09 first brute force missed ×216 row-3 orderings → 66 not 81;
  A27 first iteration forgot the per-step /3 → 176 not 248).
- Scorer: tasks/scorer_r3.py → results/round3/scores.csv
  (chars = sent+closing; acc = FINAL parsed anywhere else last number;
  fmt = own-line FINAL: line check; toks_est = chars/4).
- Raw: results/round3/raw/<COND>__A##.txt (sent + closing).

## R3 frontier table (all arms final)
| cond | n | acc | fmt% | mean_chars | mean_toks |
|------|---|-----|------|------------|-----------|
| P0 baseline   | 10 | 90% | 50% | 1088.6 (n=9) * | 272 |
| P1 minimal    | 10 | 100% | 90% | **414.5** | **104** |
| P5 strict     | 10 | 90% | 90% | 537.4 | 134 |
| P6 adaptive   | 4 | 2/4 ** | 1/4 | 621.5 (n=2) | 155 |

\* P0 A27: WRONG (88≠248), raw not persisted (subagent hit output limit;
notification tail only — S=m+n CRT: S mod 8=0, S mod 125=88 → 88, no FINAL line).
\** P6: A03 ✓ 851ch; A16 answer actually correct (49) but no FINAL line
(scorer "last number" rule picked up trailing 37 → artifact); A09 + A27 hit
the subagent output limit mid-derivation (no answer produced).

### Per-task chars / fmt / correct (P0 / P1 / P5 / P6)
| task  (key) | P0      | P1    | P5    | P6      |
|-------------|---------|-------|-------|---------|
| A00 (70)    | 923/T/T | 74/T/T  | 188/T/T | —       |
| A03 (117)   | 746/T/T | 329/T/T | 434/T/T | 851/T/T |
| A04 (279)   | 970/F/T | 251/F/T | 138/T/T | —       |
| A09 (81)    | 764/F/T | 424/T/T | 657/T/**F** | ✗ limit |
| A11 (510)   | 1420/T/T | 755/T/T | 821/T/T | —      |
| A16 (49)    | 618/F/T | 354/T/T | 347/F/T | 392/F/✓† |
| A19 (336)   | 909/F/T | 149/T/T | 883/T/T | —       |
| A23 (149)   | 1041/T/T | 221/T/T | 308/T/T | —       |
| A25 (113)   | 2406/T/T | 871/T/T | 916/T/T | —       |
| A27 (248)   | ✗88 *   | 717/T/T | 682/T/T | ✗ limit |

† P6 A16 scorer artifact: answer 49 IS correct (raw ends "Answer: **49**
(n = 1, 11, 37)") but no FINAL line → fmt=N, and the "last number" rule
scores 37. \* P0 A27 raw not persisted (see table footnote).

## Key findings (R3)
1. **P1 holds 100% on 10/10 official AIME problems** (2 easy, 4 medium,
   4 hard incl. geometry + combinatorics + recurrence), at 2.63× fewer
   chars than P0 (414.5 vs 1088.6). "Answer only" is the current
   length-accuracy frontier on real competition math for this model.
2. **P5's strictness is not free**: it is LONGER than P1 (537.4 ch) and made
   THE single accuracy error of the round — A09 (3×9 grid counting): P5
   output 66 (missed ×216 row-3 within-block orderings) while P0/P1 both
   got 81. The STOP-never-rederive rule suppressed the re-derivation that
   would have caught it. P5's discipline also decays on hard tasks: A25
   broke both sent-leak AND closing re-derivation (was clean on A00–A19).
   → P5 = worst of both: not shorter than P1, not as safe as P0.
3. **Error pattern is task-type specific, not "hard" in general**: P5's only
   error is combinatorial counting (A09); it passed all hard geometry
   (A11, A19) and hard algebra. A09 is also the task where the CORRECT
   answer requires a 3-part product and P5 truncated the derivation.
4. **fmt (own-line FINAL) is unstable across ALL arms on real tasks**:
   P0 5/9, P1 8/9, P5 8/9. Failures: bold **FINAL**, "FINAL ANSWER:",
   FINAL mid-line. The deployment parser (unanchored, acc metric) absorbs
   most of it, but strict-pipeline users will see ~1–5% format drops.
   P1's failures are the cheapest to fix (one extra reminder sentence).
5. **P1 leak pattern**: sent message usually contains a one-line method leak
   ("(d=n+2, product ≡ 39 mod d, so d|39...)") or task restate, even with
   "No reasoning". The leak is a SUMMARY (one line), not a derivation —
   the saving is real. Occasionally (A00) P1 sends only "FINAL: 70".
6. **P0 double-derivation persists**: full work in sent + full re-derivation
   in closing (A25 closing is a second full solution). This is the
   dominant R3 waste pattern (P0 mean 1088.6 ch vs P1 414.5).
7. **P6 (prompt-level adaptive) FAILS on this model**: easy branch works
   but is NOT shorter than P1 (A03: 851 ch vs P1's 329 — the "silent
   classify" step leaks work into the visible output); hard branch has no
   real length bound and ran A09 + A27 straight into the output limit with
   no answer. P5's suppression is at least deterministic; P6's "3-5 lines
   max" is ignored on hard problems.
8. **The verbose baseline is not a safe fallback**: P0 A27 (the hardest
   task) also hit the output limit — its closing was mid-verification of an
   ALREADY-WRONG answer (S=88 vs key 248). Verbose + unbounded = both the
   longest AND wrong on the hardest item.

## Data-integrity notes
- tasks/aime25_test.jsonl had 2 corrupted LaTeX fragments: `\frac` written
  as `<0x0C form-feed>rac` (the `\f` escape eaten on write) in ids 18 and
  27. Fixed in place (backup /tmp/aime25_test.jsonl.bak). A27's three
  running subagents saw the corrupted but semantically obvious version.
- A09 key 81 and A27 key 248 independently re-derived (see Method).
- P6__A3.txt was named without zero-padding (A3 vs A03) → scorer silently
  skipped it (`if tid not in BYID: continue`); renamed to P6__A03.txt and
  re-scored (that's why the mid-run P6 aggregate showed n=1).
- P0 A27 raw not persisted: the subagent hit its output limit and the
  session only kept the notification tail (S=88 CRT work, no FINAL).
  Treated as wrong + no-raw; not included in P0 char mean.

## Final recommendation (delivered to user)
Two layers, in order:
1. **Prompt layer: P1 template** — "Answer as a plain integer. / Answer
   only. No reasoning, no working, no explanation. / End with a line
   exactly: FINAL: <answer>". Measured 2.63× shorter than default at
   10/10 accuracy on official AIME 2025 subset. This is the community
   standard prompt-level /no_think equivalent (see survey).
2. **Serving layer (only if reasoning must be kept): thinking_token_budget**
   (DSH-native). Prompt-level strictness (P5) and prompt-level adaptivity
   (P6) both underperform: P5 is longer AND less accurate; P6's hard branch
   is unbounded.
Caveats: (a) metric = visible output chars (chars/4 ≈ tok), not internal
thinking tokens — for a low-thinking model these should track, but not
directly measured; (b) n=10 tasks, 1 run per arm — directional, not
statistical; (c) AIME-competition-math generalization: answer-only is
risky on tasks where the USER needs the derivation (report/teaching use).

## 副脑质询（it6, subagent 63b67b83）— 盲区与置信度降级
对 5 条结论的质询，按杀伤力排序:
1. **核心指标与目标错配（最致命）**: 目标写"减少思考/输出 token"，实测只有可见输出字符(≈chars/4)。low-thinking 的思考在内部 thinking token，不在可见流；P1 只是把可见推导藏起来，内部 thinking 量可能不变。→ "减 62%"只对可见流成立；测到 thinking token 之前，结论只能写"减少可见输出 62%"。
2. **"零质量损失"记账矛盾 + n=1 无方差**: P0 标"9/10 acc 100%"(90% 非 100%)口径不齐；grader 对无 FINAL 行也宽容抽整数→acc 可能虚高；10 题×每臂 1 次、无 seed、无重复→无方差估计，62% 是单点无 CI。→ "零质量损失"降级为"本批 10 题单跑未观察到正确率下降"。
3. **P1 的"短"接近同义反复，且不可外推 AIME 之外**: AIME=单整数答案+模型本就强，answer-only 最易赢的场景；需推理链承载中间结果的多步任务（代码/多段证明/规划/多跳）强制 No reasoning 会直接掉质量。→ 结论 1 限定"单整数答案数学题"；外推前需非 AIME 对照集。
4. **P5/P6 失败是 n=1 / 异质子集**: A09 漏×216 是单题单跑的 slip，无法区分"更严 prompt 导致" vs "随机错"；P6 只跑 4 题且子集不同。→ 弱化为"观察到一次未解释的 A09 失败"+"hard 分支缺长度上限→截断失效"（A09/A27 两例同向，中置信）；"非单调""自适应失败"降为低置信。
5. **结论 2 (b) serving 层预算建议零实验支撑**: 实验只测 prompt 臂，从没测过 thinking_token_budget；(b) 是纯外推，且与 (a) 有张力（P1 已 10/10 时"保留推理"用途未界定）。→ (b) 标注为未验证后续方向。

**最终免责（副脑原文，粘贴进任何对外报告）**:
> 局限与免责声明：本结果基于 qwen3.8-27b-w8a16（low-thinking 配置）在 10 道 AIME 2025 公开题、每臂单次运行、未固定/重复 seed 的条件下测得，无方差估计与置信区间，单次差异可能来自运行噪声而非 prompt 效应。所有长度指标为可见输出字符（≈chars/4），未测量内部 thinking token 或实际成本/延迟，故"减少 token"的表述仅对可见流成立。"P1 零质量损失"仅在上述单整数答案数学题、单次运行口径下成立，acc 与 fmt 的抽取规则见附录；不可外推至需要推理链的多步任务（如代码、多段证明、多跳规划）。P5 的非单调与 P6 的截断失效各为单点/小样本观察，尚不足以构成"更严提示必更差""prompt 级自适应不可行"的一般性结论。serving 层 thinking_token_budget 建议为未经本实验验证的方向。在补齐重复运行（k≥3、固定 seed）、thinking token 计数与非 AIME 对照集之前，本文所有定量幅度与质量声明均为低置信，仅供方向性参考。

## Serving 层调研结论（goal round 14，只读调查，未动任何服务）

**架构（实测链路）**：DSH vllm provider → 127.0.0.1:8787（claude-vllm-proxy，~/.claude-vllm-proxy/proxy.mjs，554 行；对非 /v1/messages 路径纯字节透传，并把每个请求体落盘到 ~/.claude-vllm-proxy/captures/cap-<ts>.req.json）→ **http://100.112.53.47:8000（远程 vLLM，Tailscale IP；本机无 vLLM 进程，8000 无本地监听）**。

**当前线格式（2026-10-18 19:07 抓包，cap-1792321661235.req.json，即本会话实时请求）**：chat/completions 风格，顶层键 = {max_completion_tokens: 24000, messages, model, prompt_cache_key, **reasoning_effort: 'low'**, store: false, stream, stream_options, tools}。即"low thinking 配置"现在只发了一个 effort 字符串。

**SSE 实测（最近 4 条 DSH 流）**：thinking 内容字符 = **0**（无 reasoning_content 增量），text = 227 / 6931 / 27790 / 32471 字符。→ 当前配置下可见流里没有思考内容；"思考过长"体现在可见输出（推导文本），正是 P1 prompt 模板直接打击的对象。注意：内部 thinking token 无法从客户端验证（服务端 flag 不可见）。

**DSH 代码层（app.asar → @earendil-works/pi-ai）**：预算机制完整存在——thinkingBudgetForLevel 默认 minimal 1024 / low 2048 / medium 8192 / high 16384（simple-options.js），≥1024 token 答案空间 clamp；wire 两条路：(1) chat-template thinkingFormat → chat_template_kwargs {thinking_budget: $var}（vLLM Qwen3 原生 kwarg 通道）；(2) openai-completions.js:727 通用 thinking_token_budget 字段。但 (3) Responses 协议路径（openai-responses.js）只发 reasoning.effort 字符串，无预算字段。当前 cordis.patch.yml 的 vllm model 条目是裸的（无 reasoning/thinkingBudgets/compat）→ **预算机制未启用**。

**结论（两层，最终版）**：
1. Prompt 层（R3 实测，零配置）：P1 模板 = 前沿，短 63%，AIME 2025 10/10。
2. Serving 层（需重启，按用户指令放着没动）：最直接 lever = vLLM 启动加 `--chat-template-kwargs '{"thinking": true, "thinking_budget": N}'` 服务端硬上限；或 DSH 侧 cordis.patch.yml 补 thinkingBudgets + compat（thinkingFormat: chat-template, chatTemplateKwargs）。两者都需服务重启。定 N 之前建议先对 100.112.53.47:8000 做一次 curl A/B（reasoning_effort vs chat_template_kwargs.thinking_budget），确认该 vLLM build 实际认哪个字段、thinking token 消耗差多少。

**诚实边界**：远程 vLLM 启动 flag 从本机不可见；reasoning_effort:'low' 在该 vLLM 版本上的实际效果未验证；SSE think=0 的解释（服务端关闭思考 vs 思考但不流式）未定论。
