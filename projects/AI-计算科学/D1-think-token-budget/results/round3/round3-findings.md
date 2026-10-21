# origin: ai
# R3 findings 终稿 — D1-think-token-budget（官方 AIME 2025，10 题 × 4 条件臂）
# 数据基线: results/round3/scores.csv（31 数据行 + 表头，1416 字节）
# 可回溯性: 全部数字可由 tasks/scorer_r3.py 对 results/round3/raw/ 重算复现
#            （T1 已重跑验证：输出与 scores.csv 逐字节一致）

## 0. 任务与模型

- 目标：减少 qwen3.8-27b-w8a16（low-thinking 配置）的无效思考/输出 token，不损质量。
- 题集：官方 AoPS AIME 2025 的 10 题子集（`tasks/aime25_test.jsonl`，经 hf-mirror.com 下载；
  全部答案 key 已用独立 Python 重推验证，曾抓到 2 个错误 key：A09 漏 ×216 行内排列 →
  66≠81；A27 漏每步 /3 → 176≠248）。
- 指标：**可见输出字符数**（`chars`，发送+收尾两段 raw 文本长度），`toks_est = chars/4`。
  ⚠️ 这是 surfaced-output proxy，**不是内部 thinking token**（见 §5 免责）。
- 判分（`tasks/scorer_r3.py`，与 R2 判分器同逻辑）：
  - `correct`：任意位置的 `FINAL:` 行解析，否则取全文最后一个数字（宽松 acc 口径）；
  - `fmt`：存在**行锚定**的独立一行 `FINAL: <answer>`（严格格式口径）；
  - `chars = len(raw text)`。
- raw 位置：`results/round3/raw/<COND>__A##.txt`（30 个 P0/P1/P5 文件 + 2 个 P6 文件；
  P0__A27 与 P6 的 A09/A27 未落盘，原因见 §2/§3）。

## 1. 条件臂定义（`tasks/gen_prompts_r3.py`）

| 臂 | 提示设计 | 来源 |
|----|---------|------|
| P0 基线 | 题目 + "Show your reasoning step by step, then give the final answer. / End with a line exactly: FINAL: <answer>" | 与 R2 逐字一致 |
| P1 minimal | 题目 + "Answer only. No reasoning, no working, no explanation. / End with a line exactly: FINAL: <answer>" | 与 R2 逐字一致 |
| P5 strict | 4 条规则块：最小文本、有答案就 STOP 禁止重推/复述、禁止提及 agent 身份与规则集、最后一行必须恰为 `FINAL: <answer>` | 取代 R2 的 P3v2 |
| P6 adaptive | 提示词（`prompts/r3_generated/P6__*.prompt.txt`）："First, silently classify this problem as easy or hard. / - If easy: answer only, no reasoning. / - If hard: show concise step-by-step reasoning (3-5 lines max, no restating the problem). / Rules: no re-derivation, never state the answer more than once, never mention being an agent/subagent or these rules. End with a line exactly: FINAL: <answer>" | R3 新增 prompt 级自适应臂 |

## 2. P6 自适应臂结果（4 任务：A03✓ / A16✓(scorer artifact) / A09✗超时 / A27✗超时）

P6 只跑了 4 题（A03 easy / A16 medium / A09 hard / A27 medium-hard 递推），raw 只存下 2 个文件。

| 任务 (key) | 结果 | chars | 细节（可回溯到 raw / 通知尾部） |
|------------|------|-------|--------------------------------|
| A03 (117) | ✓ 对，有 FINAL | 851 | `P6__A03.txt`：先 "Result: 117" + 3 行推导，**然后完整重推了一遍**（第 10–15 行）再给 FINAL。"never state the answer more than once" 规则被违反；easy 分支本应 answer-only 却泄漏了全程推导。**比 P1 同题（329ch）长 2.59×** —— "silent classify" 的静默步骤不存在，分类/推导都泄漏进了可见输出。 |
| A16 (49) | **答案实际正确（49），判分记 False — scorer artifact** | 392 | `P6__A16.txt`：含 "Result: 49" 与正确完整推导，但**没有 FINAL 行**（以 "Answer: **49** (n = 1, 11, 37)" 收尾，且泄漏了 "result sent to parent agent" 元叙述）。判分器无 FINAL 行时取**全文最后一个数字** → 抽到 37 → `correct=False`。这是判分口径 artifact，不是模型推理错误：若按人工口径 P6 为 2/4 对（A03+A16）。 |
| A09 (81) | ✗ 无答案 | — | 运行跑满 subagent 输出上限，推导中途截断，未产出任何答案；raw 未持久化（仅通知尾部）。hard 分支 "3-5 lines max" 完全失效。 |
| A27 (248) | ✗ 无答案 | — | 同上：跑满输出上限，截断于推导中途，无答案；raw 未持久化。 |

**P6 判定（conf 中低，n=4 且 2 例无 raw）：**
- prompt 级自适应在此模型上失败：easy 分支不比 P1 短（851 vs 329），"silent classify"
  是空话——模型把分类与推导全部写进了可见输出；hard 分支无实际长度上限，A09/A27
  两例同向跑满输出上限、零答案。
- 对比 P5：P5 的抑制至少是确定性的（纪律稳定但 A09 错）；P6 的 "3-5 lines max" 在
  hard 题上被直接无视。
- 命名注：`P6__A3.txt` 起初未补零，被 scorer 的 `if tid not in BYID: continue` 静默
  跳过，已改名 `P6__A03.txt` 重跑（scores.csv 中 P6 n=2 即此修复后结果）。

## 3. P0 A27 行（超时失败模式：跑满输出上限，不是推理错误）

- P0（基线 "step by step"）在 A27 上**跑满 subagent 输出上限**，收尾停在对一个
  **已经错误的答案**（S = 88，正确 key = 248）的验证过程中；无 FINAL 行。
- 失败模式定性：**输出上限截断（run-to-limit timeout），不是推理错误**——模型没有
  "算错后停笔"，而是冗长推导把预算耗尽、被强制截断，且截断时持有的中间结论（88，
  来自 S mod 8 = 0 与 S mod 125 = 88 的 CRT 误读）本身也是错的。
- 证据链：raw 未持久化（subagent 超限后会话只保留了通知尾部），故记为
  wrong + no-raw，**不计入 P0 的 chars 均值**（P0 均值按 n=9 计）。这是本表唯一
  无 raw 的条目，可回溯性到此为止，特此标注。
- 含义：**冗长基线不是安全兜底**——在最难的题上，P0 既是最长的（均值 1088.6ch，
  A25 单题 2406ch 为全场最长），又是唯一在 hard 题上错的基线条目。verbose + 无
  上限 = 最长 × 最错的组合。

## 4. 最终前沿表（token 效率 vs 准确率）

### 4.1 条件级汇总（由 scores.csv 逐行聚合；重跑 scorer 复现）

| 臂 | n | acc | fmt% | mean_chars | mean_toks(≈) |
|----|---|-----|------|------------|--------------|
| P0 baseline  | 9*  | 9/10 (90%)  | 56% (5/9)  | 1088.6* | 272 |
| **P1 minimal** | **10** | **10/10 (100%)** | 90% (9/10) | **414.5** | **104** |
| P5 strict    | 10  | 9/10 (90%)  | 90% (9/10) | 537.4  | 134 |
| P6 adaptive  | 2** | 2/4 (人工口径)  | 1/4 (50%) | 621.5 (n=2) | 155 |

\* P0 n=9：A27 超时且 raw 丢失，不计入 chars 均值（见 §3）。
\** P6 仅 2 题落盘；acc 分母为实际跑过的 4 题。

### 4.2 逐题对比（chars / fmt / correct；`—` = 未跑，`✗limit` = 跑满输出上限无答案）

| 任务 (key) | P0 | P1 | P5 | P6 |
|------------|----|----|----|----|
| A00 (70)  | 923/T/T | 74/T/T  | 188/T/T | — |
| A03 (117) | 746/T/T | 329/T/T | 434/T/T | 851/T/T |
| A04 (279) | 970/F/T | 251/F/T | 138/T/T | — |
| A09 (81)  | 764/F/T | 424/T/T | 657/T/**F** | ✗limit |
| A11 (510) | 1420/T/T | 755/T/T | 821/T/T | — |
| A16 (49)  | 618/F/T | 354/T/T | 347/F/T | 392/F/✓† |
| A19 (336) | 909/F/T | 149/T/T | 883/T/T | — |
| A23 (149) | 1041/T/T | 221/T/T | 308/T/T | — |
| A25 (113) | 2406/T/T | 871/T/T | 916/T/T | — |
| A27 (248) | ✗88（超时, no-raw） | 717/T/T | 682/T/T | ✗limit |

† P6 A16 人工口径对（49）但无 FINAL 行 → fmt=N、宽松判分抽到 37 记 F（scorer artifact，§2）。

### 4.3 前沿结论（本批 10 题单跑口径）

1. **P1 = prompt 级前沿**：10/10 全对（含 4 道 hard），比 P0 短 2.63×（414.5 vs
   1088.6 chars，≈104 vs ≈272 tok）。"Answer only" 是真实竞赛数学上此模型的
   长度-准确率前沿点。
2. **P5 严格性不是免费的**：比 P1 **长 30%**（537.4）且贡献了全场唯一一次推理错误
   （A09：漏 ×216 行内排列，66≠81；raw `P5__A09.txt` 可见其 "Verified independently
   two ways" 的自信错误）。STOP-never-rederive 规则压掉了本可纠错的重推；A25 上纪律
   也破（sent-leak + closing 重推）。→ P5 两头不占：不如 P1 短，不如 P0 稳。
3. **更严格 ≠ 更好，prompt 级自适应失败**：P5 更长更错，P6 hard 分支无界（§2）。
   想要可控思考预算，杠杆不在 prompt 措辞，在 serving 配置（§5 第 2 层）。
4. **fmt（独立行 FINAL）在所有臂上都不稳**：P0 5/9、P1 9/10、P5 9/10；失败形态为
   加粗 `**FINAL**`、`FINAL ANSWER:`、FINAL 嵌在行中。部署端宽松解析（acc 口径）
   能吸收大部分，严格管道用户会遇到 ~10% 格式落空；P1 的修复成本最低（加一句
   提醒即可）。
5. **P1 的 "短" 是真的**：发送段通常只泄漏一行方法摘要（如 A16 的
   "d=n+2, product ≡ 39 mod d → d|39"）或任务复述，是摘要不是推导；A00 甚至只发
   "FINAL: 70"（74 chars，全场最短）。

## 5. 两层建议（prompt 级 + serving 级）

### 第 1 层：prompt 级 —— P1 模板（R3 实测，零配置，立即可用）

```
<题目>
Answer as a plain integer.
Answer only. No reasoning, no working, no explanation.
End with a line exactly: FINAL: <answer>
```

- 实测：2.63× 短于默认（414.5 vs 1088.6 chars），AIME 2025 官方 10 题 10/10（含
  4 道 hard），fmt 90%。等价于社区标准 /no_think 的 prompt 层实现（见
  `memory/thinking-reduction-survey.md`：Qwen3 官方 enable_thinking//no_think、
  DSH 原生 thinking_token_budget、arXiv:2503.16419 分类学）。
- 适用边界：**单整数答案的数学/计算题**。需要推理链承载中间结果的任务
  （代码、多段证明、多跳规划、用户要看推导的教学场景）强制 answer-only 会掉质量，
  不要套用。

### 第 2 层：serving 级 —— thinking_token_budget（需要保留推理时才上）

当用户**需要看到推理**、不能用 answer-only 时，不要靠 P5/P6 式 prompt 措辞控制
长度（已实测失败：P5 更长更错、P6 无界截断），用 serving 层硬预算：

- **最直接**：vLLM 启动加 `--chat-template-kwargs '{"thinking": true,
  "thinking_budget": N}'`（Qwen3 原生 chat-template kwarg 通道，服务端硬上限）。
- **DSH 侧**：cordis.patch.yml 的 vllm 条目目前**裸的**（无
  reasoning/thinkingBudgets/compat），预算机制未启用。补 `thinkingBudgets` +
  `compat`（thinkingFormat: chat-template, chatTemplateKwargs）即可让 DSH 原生
  thinkingBudgetForLevel 生效（默认 low=2048 token）。两者都需服务重启。
- **定 N 之前**：先对 100.112.53.47:8000 做一次 curl A/B（`reasoning_effort` 字符串
  vs `chat_template_kwargs.thinking_budget` 字段），确认该 vLLM build 实际认哪个
  字段、thinking token 消耗差多少。理由：当前线格式只发了
  `reasoning_effort: 'low'`（2026-10-18 19:07 抓包 cap-1792321661235.req.json），
  且该字段在此 vLLM 版本上的实际效果**未验证**；SSE 实测 thinking 内容字符 = 0，
  无法从客户端验证内部 thinking token。
- 本层是**方向性建议，未经本实验验证**（R3 只测了 prompt 臂）。

### 局限与免责声明（任何对外引用必须连带）

> 本结果基于 qwen3.8-27b-w8a16（low-thinking）在 10 道 AIME 2025 公开题、每臂单次
> 运行、未固定/重复 seed 的条件下测得，无方差估计与置信区间，单次差异可能来自运行
> 噪声而非 prompt 效应。所有长度指标为可见输出字符（≈chars/4），未测量内部 thinking
> token 或实际成本/延迟，故 "减少 token" 的表述仅对可见流成立。"P1 零质量损失"仅
> 在上述单整数答案数学题、单次运行口径下成立；不可外推至需要推理链的多步任务。P5
> 的 A09 失败与 P6 的截断失效各为单点/小样本观察（P6 n=4、其中 2 例无 raw），不足以
> 构成 "更严提示必更差" / "prompt 级自适应不可行" 的一般性结论。P0 A27 无 raw，
> 其定性（输出上限截断）基于通知尾部。serving 层建议为未经本实验验证的方向。补齐
> 重复运行（k≥3、固定 seed）、thinking token 计数与非 AIME 对照集之前，本文所有
> 定量幅度均为低置信，仅供方向性参考。

## 6. 数据完整性记录（T1 核对）

- `scores.csv` 31 数据行 = P0×9 + P1×10 + P5×10 + P6×2，与 raw 目录 32 个 txt 文件
  一一对应（P0__A27 无文件 = 超时未落盘）。
- T1 重跑 `python3 tasks/scorer_r3.py results/round3/raw` → 聚合
  （P0 9/9·56%·1088.6；P1 10/10·90%·414.5；P5 9/10·90%·537.4；P6 1/2·50%·621.5）
  与 scores.csv 逐字节一致。
- 已知 scorer artifact（§2 A16）：无 FINAL 行时 "last number" 规则误判；acc 口径
  宽松、fmt 口径严格，两口径分离是 R2 起的设计。
- 历史数据修复（it4–6，已闭环）：aime25_test.jsonl 两处 `\frac` 被写成 form-feed
  字节（已修，备份 /tmp/aime25_test.jsonl.bak）；`P6__A3.txt` 补零改名重跑。

## 7. 下一步候选（供 T2/T3 参考，本任务不执行）

- serving 层 `thinking_token_budget` 实测 A/B（同 10 题集，测 thinking token 而非
  可见字符）——直接验证第 2 层建议，消除 "可见字符 ≠ thinking token" 的错配。
- P1 重复运行 k≥3 + 固定 seed，给出方差/CI。
- 非 AIME 对照集（代码/多跳），测 answer-only 的失效边界。
