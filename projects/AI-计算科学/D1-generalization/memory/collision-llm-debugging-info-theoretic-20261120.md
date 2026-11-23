# 撞车调研：LLM 调试策略 vs 信息论最优（2026-11-20）
# origin: ai
# 来源①：arXiv API (https://export.arxiv.org) 本轮实查，5 组查询。

## 问题
"LLM agent 不会自发用信息论最优的调试策略"——这个窄主张新不新？

## 命中（arXiv 实查）
**信息论最优的理论侧（已存在，2020 起）**
- Information-theoretic User Interaction: Significant Inputs for Program Synthesis (2006.12638, 2020)
  → 信息论最优查询在 program synthesis 的理论框架，**早于 LLM 时代**。理论不是新的。
- Interactive Program Induction with Language Model Priors (2611.18485, 2026-11)
  → 最新，把 LM prior 接进 interactive program induction，直接相关。
- How Much Evidence Should a Coding Agent's Self-Correction Carry? Adaptive Dirichlet Evidence (2610.08514, 2026-10)
  → 量化 self-correction 证据权重，和"语义归纳 vs 系统查询"直接相关。

**CodeARC 本体**
- CodeARC: Benchmarking Reasoning Capabilities of LLM Agents for Inductive Program Synthesis (2503.23145, 2025)
  → 就是我们在跑的 benchmark。

**differential testing + LLM（实操侧，活跃）**
- Guided Debugging of Auto-Translated Code Using Differential Testing (2501.09475, 2025)
- DiffSpec: Differential Testing with LLMs using NL Specs (2410.04249, 2024)
- LLMs in the Heart of Differential Testing (2404.03664, 2024)

**LLM debugging 策略（实操侧，成熟）**
- Teaching LLMs to Self-Debug (2304.05128, 2023)
- Debug like a Human: LLM Debugger via Verifying Runtime Step-by-step (2402.16906, 2024)
- DebugBench (2401.04621, 2024)

## novelty 判断（带证据，不凭记忆）
1. **宽泛"理论/实操割裂"**：老主题，不新（泛化 gap 等）。
2. **"信息论最优查询"理论**：2020 就有（2006.12638），**不新**。
3. **真正可能新的交叉点**：
   - 理论（信息论最优）已有 + benchmark（CodeARC）已有 + LLM 实操（differential testing）已有
   - **但"用 CodeARC 实证 LLM 语义归纳 vs 信息论最优查询的 gap"这个对照实验，没查到直接撞车**
   - 即：理论框架没被 LLM 实操验证过——2020 那篇是理论，CodeARC 是 benchmark 但没做信息论最优对照
   - **conf 0.6**：n=5 的 27b trace 是初步实证，撞车查询可能漏（"optimal query + program synthesis" 返回空，说明这个精确交叉点文献稀疏，但也可能我查询词没覆盖到）

## 核验结果（2026-11-20 读 abstract 确认）
- [x] 2611.18485：Bayesian 理论框架（后验集中），**未做 LLM 实操对照**
- [x] 2610.08514：量化 self-correction 证据权重（Dirichlet），**未做"语义归纳 vs 最优查询"对照**
- [x] 两篇都**没做**"LLM 语义归纳 vs 信息论最优查询"的实证对照 → **gap 确认存在**
- 待补：换查询词再扫一轮（"Bayesian optimal"/"information gain"+agent+debugging），防漏

## 补充查询（防漏，2026-11-20 第二轮）
- `information gain + agent + debugging`：no results
- `query strategy + program synthesis`：no results
- `Bayesian optimal + code generation`：5 条但均非"最优查询策略"（RL 对齐/prompt 优化/多 agent 调参）
→ 精确交叉点（LLM 实操 × 信息论最优查询的实证对照）文献确实稀疏，gap 判断维持。

## 公平对照核验（2026-11-20）
- CodeARC `src/evaluate.py` 默认 mi=30, mdr=1（mdr=0 仅 sft_distillation）= 论文 o3-mini 52.7% 参考配置
- → 27b 的 0/5 与 52.7% 是**公平对照**，差距真实（n=5，n=20 重跑中 proc_f1d50177bcf5）
- 这强化了"割裂"实证：同配置下 27b 语义归纳栽边界 + 语法崩，o3-mini 52.7%

## 主张修正（2026-11-20 晚，chat 测试 + 跨域探针实证）
- 原主张"LLM 不会自发用信息论最优调试策略"**过强**，被两组实验反驳：
  1. chat 测试：27b 无上下文纯 chat 回答"100/1e4/1e6 行工程怎么排查"，自发给出 git bisect/模块二分/数据二分/可观测性驱动，按规模分档
  2. 跨域探针：27b 无提示自发命中率 6/6（教科书 2/2 + 新编场景 4/4，ODE/动力系统/SIS）
- **修正后主张**：割裂不在策略选择（27b 自发知道正确策略），在**受限 oracle 反馈下的规则归纳容量**——edge prompt 逼它系统探边界后 4/5 仍错，探了但归纳不出规则。
- 大工程二分 = 高频启发式复述（训练数据里有），与 CodeARC 失败不矛盾。
- 详见 `crossdomain-probe-27b-20261120.md`。

## 结论
不是全新方向，但**"理论已有 + benchmark 已有 + 但两者没被对照实证"这个 gap 是真实的**——值得做的不是"提出信息论最优"（有了），而是**实证 LLM 在这个 gap 里到底差多少 + oracle 反馈信息设计能补多少**。这正好接 D 的"信息密度"偏好。
