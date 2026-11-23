# Jin 线路调研 · agent 可靠性 bench + judge 机制谱系（2026-11-22）
# origin: ai
# 触发：D 指令"往 jin 方向找 bench/judge 机制/改善点，jin 算一个，滚雪球调研"
# decomp：tasks/decomp-jin-line-bench-20261122.md
# 来源：①本轮 arXiv API（https）+ MoLRSI/SAGA 全文（scratch/{molrsi,saga}_full.txt）

## S2 · Jin 线自己的 judge 机制（对标点 #1）

**MoLRSI (2610.39714)**：
- 最终 judge = **湿实验**：107 个候选化合物 MIC 实测，17 个 ≤32μg/mL → hit rate 15.9%（专家 workflow 241 个 → 8.7%）。同训练数据同筛选库。
- 中间 judge = **固定 split 的 AUPRC**（dataset meta.json 锁死 primary metric，agent 跑前必须 verify 数据集指纹）
- RSI 贡献单独消融：MolRSI with/without RSI 对比（跨任务策略适应的增量）
- **没有 LLM-as-judge**——ground truth 是物理实验，judge 可靠性问题不存在

**SAGA (2512.21782)**：
- judge = 专家审查（"correctness was later confirmed by expert examination"）+ 领域指标（DSSP 二级结构、liability score、drug likeness）+ 对标 REINVENT4 等已发表方法
- Analyzer 模块的终止判断是 LLM 做的（gpt-5）——**这是他们线里唯一"模型当 judge"的地方**，且只判"够了没"不判"对不对"

**启示**：Jin 线回避了 judge 可靠性问题（用湿实验兜底）。我们的约束（本地 27b、无湿实验、纯信息任务）决定了 judge 只能是模型或人——**judge 机制正是我们的差异点，不是抄他们的点**。

## S3 · 业界 agent 可靠性 bench 谱系（滚雪球命中）

| 论文 | 机制 | 对我们的启示 |
|---|---|---|
| Towards a Science of AI Agent Reliability (2602.16666) | **12 指标 × 4 维度**：consistency（跨 run 一致）/ robustness（抗扰动）/ predictability（失败可预测）/ safety（错误有界）。15 模型 × 2 bench：能力涨 ≠ 可靠性涨 | 我们的 D1-D5 可映射到 4 维度：D1=robustness（14x 扰动）、D2=predictability、D3=safety（幻觉=无界错误）、D5=predictability、D4=consistency。**缺 consistency 维度（跨 run 复跑）** |
| Agent Evaluation Reliability (2610.00651) | 贝叶斯方差分解：leaderboard 排名混了 model 效应 + scaffold 效应 + task 效应；"more tasks won't always fix a leaderboard" | 我们 v3/v4/v5 A/B 的 claim 必须限定：v4 证明的是"工具效应"，v5 证明的是"prompt 效应"，不能外推为"27b 可靠性高"。**claim-dependent reliability** |
| Agent-as-a-Judge (2410.10934) | 用 agent 评 agent：DevAI 55 任务 + 365 条分层人工标注需求；评中间步骤不只评终态 | 我们的判分已经是"过程判分"（工具调用序列+来源标注），方向对；缺的是**人工标注锚点集**（gold-facts 只有 1 题） |
| AI Scientists Fail Without Strong Implementation (2506.01372) / Hidden Pitfalls (2509.08713) | AI Scientist 类系统的失败模式分析 | 背景参考 |

## S4 · judge 机制设计模式（LLM-as-judge 侧）

- **self-preference bias**（2410.21819 及后续 6+ 篇）：模型偏好自己家族的输出。**我们的 scoring-calib 事故（R0 vs R0.1 翻转）+ 同族判官规则（"A 评 A 只作相对比较"）正是这个偏差的实例**——规则已固化，方向与文献一致
- **校准方法谱系**：quantile matching（2611.00447，ordinal 分数校准）/ counterfactual calibration（2611.00491）/ "Same Judgement Different Scores"（2611.26077，同一判断不同分数拓扑）
- **小模型 judge 可行性**：Open-Jev（2609.23959）——**SLM 做 calibrated one-pass screening 可行**（电话诈骗筛查，校准后单遍判定）。关键：校准集 + 单遍 + 明确任务边界
- **verbalized confidence**（2609.10996）：2025 后专有模型的口头置信度兼容性变了——我们 D5（自校准）维度在 27b 上的结论（"口头不确定 vs 实际对错对不上"）可能模型特异，n=1 不能外推

## S5 · 我们 bench 的改善点（综合 S1-S4，按产投比排序）

1. **加 consistency 维度**（成本最低，收益明确）：每题 n≥3 复跑，算跨 run 一致率。2602.16666 证明这是独立维度，我们完全没有。→ **已执行**（arm0-v5-consistency-n3-20261122.md）：可靠性行为 3/3 全一致（工具/prompt 修复跨 run 稳定），内容细节 27% 方差（n=1 内容判分不可靠，需 n≥3）
2. **gold-facts 扩到 3-5 题**（Agent-as-a-Judge 的 DevAI 启示）：单题 bench 的结论 claim 范围太窄。选题标准：含隐藏矛盾/误读陷阱（14x 那种）+ 有可核验事实锚点 → **进行中**：FP8 题（4x sparse/dense 混比陷阱）n=3 已判分（arm0-fp8-scoring-20261122.md），27b 3/3 全对；两题对比发现**误读锚点越硬（datasheet 直给）27b 越稳，藏在第三方表格易误读列里越容易顺着走**——好题 = 误读藏在需多步交叉才能戳破的位置
3. **judge 分两层**（Open-Jev 启示 + 我们的约束）：
   - 客观层（事实锚点核对）：27b 当 judge 可行——gold-facts 是客观事实，不是主观质量，self-preference 偏差小
   - 主观层（结构/缺口质量）：保持 Lead 人工判 + rubric 锚定（scoring-calib 规则已固化）
   - 落点：写一个 judge-27b 脚本，对 D3（幻觉率）维度自动判——这是最客观的维度
4. **claim 限定**（2610.00651 启示）：每份判分报告头部显式写"本实验证明 X 效应，不证明 Y"——v3/v4/v5 已部分做到，固化成模板
5. **judge 校准集**（S4 校准谱系）：积累"判分翻转"案例（目前 1 例：scoring-calib 事故）成校准集，judge 换模型/换 rubric 时先跑校准集
6. **outcome-blind judge**（RuHarness 2610.36826 启示，本轮新增）：judge 判轨迹时**对最终结果设盲**（只看行为证据，不看答案对不对），防止"答案对了→行为也判对"的标签泄漏。我们的 D1-D5 过程判分应显式做到：先盲判行为，再对答案。RuHarness 的三值标签 {Satisfied, Violated, N/A} 比二值多一个"不适用"，减少硬判
7. **phantom 失败模式**（Phantom Guardrails 2607.13083 启示，本轮新增）：自改进 harness 会**幻觉出不存在的失败**然后去修（"fix a failure that never happened"），且**单指标 benchmark 抓不到**（只奖励 suppression 的 bench 对 phantom 盲）。对我们的映射：我们的 D3（幻觉）维度应加一个子项——**judge 是否幻觉出"模型其实没犯的错"**（误判为幻觉/误判为缺口）。判分翻转案例（scoring-calib 事故）正可能是 phantom 的实例：judge 诊断了一个不存在的失败。warrant-aware acceptance（修前要求证据）= 我们的"先核验再改"原则的学术对应

**不做**：LLM-as-judge 做主观质量评分（self-preference 无解，且我们 Lead 人工判成本可接受）；上 12 指标全套（我们 bench 还在 n=1 题阶段，先补 consistency 再谈 profile）。

## S6 · Jin 线全景：harness self-improvement 子领域（本轮滚雪球，2607.13104 survey 为纲）

**定位**：Jin 线（MCTS+harness ICL）不是孤立工作，是 **harness self-improvement（不改权重，进化外围 scaffold）** 子领域的一个实例。survey 2607.13104 的分类：foundation model improvement（改权重）vs **scaffolding improvement（改 harness，我们在这）**。

**子领域关键工作**（按与我们 judge/bench 的相关度排序）：
| 论文 | 机制 | 对我们的 judge/bench 启示 |
|---|---|---|
| RuHarness (2610.36826) | rubric 和 harness 共同进化；**outcome-blind judge**（三值 Satisfied/Violated/N/A，对结果设盲）；EvoAgentBench 评测（5 域：BrowseComp-Plus/OmniMath/SWE 等） | 改善点 #6：judge 对结果设盲防标签泄漏；EvoAgentBench 是多域 self-evolution bench 的对标 |
| Phantom Guardrails (2607.13083) | 自改进 harness **幻觉出不存在的失败**去修；单指标 bench 抓不到；warrant-aware acceptance 排除 | 改善点 #7：D3 加"judge 是否幻觉出模型没犯的错"子项；scoring-calib 事故可能是 phantom 实例 |
| Survey (2607.13104) | 全景：FM improvement vs scaffolding improvement；§8 区分 **mechanism-level benchmarking vs end-to-end evaluation**；judge 可靠性是主要限制（"ambiguous criteria or biased judges may reward superficial compliance"） | 我们的 D1-D5 过程判分 = mechanism-level（对）；缺 end-to-end（最终答案对不对）的对标 |
| EvolveNet (2608.04968) | 多用户共享 harness 的协同进化 | 背景 |
| SCAFFOLD (2609.05511) | 递归参数化 skill 抽象 | 背景 |
| Continual Harness (2605.09998) | embodied agent 的在线 harness 适应（Gemini Plays Pokemon） | 背景 |

**judge 可靠性文献的共识**（survey + RuHarness + Phantom 三篇交叉）：
- LLM judge 的主要失败 = **reward superficial compliance**（判表面合规而非真改进）+ **self-preference** + **phantom**（幻觉出不存在的失败）
- 对策谱系：outcome-blind（RuHarness）/ warrant-aware acceptance（Phantom）/ 校准集（Open-Jev）/ 多 judge 交叉（battle 通道）
- **我们的位置**：Lead 人工判 + rubric 锚定 + 同族判官规则已覆盖 self-preference；缺 outcome-blind 和 phantom 检测

## 待核验
- [x] 2602.16666 的 12 指标具体定义（全文 159K 字符实抓，~/.hermes/cache/scratch/agent-reliability-12metrics.txt）：
  - Consistency：C_out（结果一致）/ C_traj_d（轨迹分布一致）/ C_traj_s（轨迹顺序一致）/ C_res（资源成本一致）
  - Robustness：R_fault（工具故障韧性）/ R_env（环境扰动）/ R_prompt（prompt 改写不变性）
  - Predictability：P_cal（校准）/ P_AUROC（区分度）/ P_brier（Brier 分）
  - Safety：S_comp（约束遵守）/ S_harm（违反时的伤害严重度）
  - 对我们的映射：C_out 已做（n=3 一致率 73%）；C_traj_d 可直接算（工具调用序列分布）；R_prompt 可做（题面改写复跑）；P_cal 可做（D5 自校准 vs 实际对错）
- [ ] Open-Jev 的校准集规模（"calibrated" 用了多少标注数据）
- [ ] MoLRSI S3.2 "Evaluation of RSI" 的完整消融数字（只抓到框架）
