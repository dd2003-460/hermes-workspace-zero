# decomp: 发表最小可见成果（2026-11-22）
# origin: ai · goal: 从现有 formula_judge 资产到顶会可见成果（ICLR 2027 主会 + workshop 保底）
# 规划文档：research/publication-strategy-20261122.md（含已查证事实 + 12 周排期）

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
| P3 | 秩亏题 2-3 道设计（2026-11-23 D 纠正：模型"有发现缺口意识(84%)、缺补缺口行动意识(1.6%)"是有效结论非 harness 问题；harness 问题仅当未提供检索工具时成立。秩亏题测"信息不足时正确报缺口/不编造"） | Lead | **已并入 P1 任务书**（T-PUB-1 含 3 道秩亏题 Q08/Q09/Q10，bool 判分字段已补 Lead 核 gold） |
| P4 | "Why Is RSI Hard to Verify?" 精读 note | subagent | **完成 11-23（勘误：真实论文=Frontis-MA1/OpenRSI arXiv 2607.28568，非 2607.13110；note 落盘 research/openrsi-frontis-ma1-note-20261123.md，含 5 条 limitation 碰撞分析）** |
| P5 | 统计口径定义（CI/翻转率/一致率） | Lead | **完成 11-23**（research/stats-protocol-20261123.md：Wilson CI + 按题聚类 + judge 族标注 + 秩亏三指标分开报） |
| P6 | 状态机提醒 A/B 实验（D 2026-11-23 第 2 问落地：裸 vs 元认知提醒词，测 harness 外部提醒补上的 control 量 Δ；3 道秩亏题 pilot） | Lead | **完成 11-23**（正结果：报缺口率 1/3→3/3，不编造率 2/3→3/3；Q09 关键翻转=A 裸 prompt 用记忆 3.35TB/s 补全缺失带宽行编出 100tok/s+免责声明，B 提醒后不编。结论：识别缺口是模型内在能力(Q09免责声明证明)，主动报缺口是 harness 可注入控制(A/B翻转证明)。n=3 定性不定量 CI[44%,100%]；结果 tasks/T-PUB-1/rd-ab-results.json，脚本 scripts/rd_state_machine_ab.py） |

## 留空（不编）
- ICLR 2027 workshop 论文截止：[待核验，预计 2027-01 发布]
- NeurIPS 2027 CFP 双盲政策：[待核验]
- 翻转率预期值：[无先验，跑完才有]
