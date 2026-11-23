# decomp: 发表最小可见成果（2026-11-22）
# origin: ai · goal: 从现有 formula_judge 资产到顶会可见成果（ICLR 2027 主会 + workshop 保底）
# 规划文档：research/publication-strategy-20261122.md（含已查证事实 + 12 周排期）
# 【2026-11-23 修正】ICLR 2027 窗口（abstract 2026-09-18 / paper 2026-09-25）已过期 59-66 天——publication-strategy-20261122.md 写于 11-22 但当时把截止算成"距今 12 周"（日期算术错误，9-25 在 11-22 之前）。**可达窗口重排：ICML 2027（abstract 2027-01-14 还有 52 天 / paper 2027-01-22 还有 60 天）为主会目标；ICLR 2028（预计 2027-09）为次选；workshop 保底不变（各 CFP 2027-01 发布）。** 12 周排期需按 ICML 60 天重排（W8-10 成文 → W6-7 起，W12 提交 → 1/14 前）。

## 分解树（正交子项）
1. **题集**（n≥10，每题 3-5 机械检查点，含 2-3 秩亏题）
   - 缺口：题面+gold 需 Lead 核验；秩亏题的"缺口判定"标准未定义
2. **对比实验**（LLM-judge vs 公式 judge，同题同输出）
   - 缺口：LLM-judge 的 prompt 需固定版本化（防口径漂移）；翻转率定义（同输出不同判分）
3. **统计层**（n≥3 consistency + bootstrap CI）
   - 缺口：CI 口径（每题独立 vs 池化）未定
4. **校准腿**（秩亏题：正确报缺口率 vs 幻觉率）
   - 缺口：与 D1-generalization 主线的 D3（幻觉率）维度如何共享数据
5. **自修复**（reward-only A/B，rounds_to_pass）
   - 缺口：轮数上限 5 是拍的，需消融
6. **成文**（9 页 + 双盲合规）
   - 缺口：related work 中 "Why Is RSI Hard to Verify?" 未读

## 任务表（派发只执行表内条目）
| # | 任务 | 执行者 | 状态 |
|---|---|---|---|
| P1 | 题集 10 题出题（arena 任务卡）+ Lead 核 gold | arena + Lead | **已交付+核验 11-23**（b148b12ed, 指纹一致, 10题47检查点 SymPy自检PASS, 落盘 tasks/T-PUB-1/; 7条方法学缺口登记, 阻塞项=#4 bool正则库） |
| P2 | 对比脚本（formula_judge + 27b judge prompt 版本化） | Lead/subagent | **完成 11-23**（scripts/formula_judge.py：机械 judge calc/fact/bool + reward_only + LLM judge prompt v1 + Wilson CI；冒烟通过：全对=5/5，错5%=正确判错。待 P1 题集落地后接真实输出跑） |
| P3 | 秩亏题 2-3 道设计（2026-11-23 D 纠正 + 11-23 晚 framing 修正：84% 是 healthy_gap_rate（已标 degraded 节点的分类质量），非模型发现缺口率；模型自发 gap_rate≈2%（10% 中 82% 来自 prompt 指示的 [待核验] 标签），rework fix rate≈1.6% 是 harness 机制弱点非 prompt 假象。裸 baseline 里元认知轴不可计算（无 node 字段），最接近代理=supp37 自发触发 6-49% + 本 A/B 裸 prompt 报缺口 1/3。秩亏题测"信息不足时正确报缺口/不编造"） | Lead | **已并入 P1 任务书**（T-PUB-1 含 3 道秩亏题 Q08/Q09/Q10，bool 判分字段已补 Lead 核 gold） |
| P4 | "Why Is RSI Hard to Verify?" 精读 note | subagent | **完成 11-23（勘误：真实论文=Frontis-MA1/OpenRSI arXiv 2607.28568，非 2607.13110；note 落盘 research/openrsi-frontis-ma1-note-20261123.md，含 5 条 limitation 碰撞分析）** |
| P5 | 统计口径定义（CI/翻转率/一致率） | Lead | **完成 11-23**（research/stats-protocol-20261123.md：Wilson CI + 按题聚类 + judge 族标注 + 秩亏三指标分开报） |
| P6 | 状态机提醒 A/B 实验（D 2026-11-23 第 2 问落地：裸 vs 元认知提醒词，测 harness 外部提醒补上的 control 量 Δ；3 道秩亏题 pilot） | Lead | **完成 11-23（v1 英文 + v2 中文提醒词复跑结论一致）**：报缺口率 1/3→3/3，不编造率 2/3→3/3；Q09 关键翻转=A 裸 prompt 用记忆 3.35TB/s 补全缺失带宽行编出 100tok/s+免责声明，B 提醒后不编。结论：识别缺口是模型内在能力(Q09免责声明证明)，主动报缺口是 harness 可注入控制(A/B翻转证明)。n=3 定性不定量 CI[44%,100%]；结果 tasks/T-PUB-1/rd-ab-results.json + rd-ab-v2.json，脚本 scripts/rd_state_machine_ab.py。full7 判分器修复后 33/35=94.3%（3 个单点 FAIL 全是判分器 bug：科学计数法+SI 单位换算，已修+6 测试过） |

## 留空（不编）
- ICLR 2027 workshop 论文截止：[待核验，预计 2027-01 发布]
- NeurIPS 2027 CFP 双盲政策：[待核验]
- 翻转率预期值：[无先验，跑完才有]
