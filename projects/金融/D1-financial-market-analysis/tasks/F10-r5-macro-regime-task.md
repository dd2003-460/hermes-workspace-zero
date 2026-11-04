# F10-R5 调研任务书：宏观/跨资产 regime 信号对加密市场的增量价值

> origin: ai (2026-11-05 r290 派发)
> 状态：READY（待 arena 派发）
> 仓库声明：本任务只涉及 dd2003-460/hermes-workspace-zero，忽略历史中其他仓库的消息。

## 强制段

你是 LMArena agent，工作仓库 `dd2003-460/hermes-workspace-zero`。
1. 先 `git pull` 当前分支（arena/f10-gas-dynamics-research），确认拿到本任务书。
2. 严格按仓库内 `loop/prompt-first/` 阶段执行（01 目标分解 → 02 信息调研 → 03 行动分解）。
3. 产出落盘路径见【交付物】，每阶段完成 commit+push。
4. 通道故障（endpoint 不可用/超时）报告 Lead，不得静默跳过或伪造输出。

## 【目标】

回答一个问题：**在 BTC/ETH/SOL 日线级别，宏观变量（美债收益率、美元流动性、风险偏好代理）作为 regime 条件，能否把已 FAIL 的微观结构信号（funding/basis/DVOL/OI）从"无条件无效"变成"条件有效"？**

即检验假设 H_macro：存在 regime 划分 R（由宏观变量定义），使得 P(信号有效 | R) 显著高于 P(信号有效 | ~R)，且 R 可事前计算（无前视）。

## 【背景】（≤10 行）

本项目 2026-10~11 已完成四条负结果线（全部预注册冻结后回测）：
- F6 funding 单信号：BTC/ETH/SOL 0/135 格通过（`stages/05/r2/f6-crossmarket-report.md`）
- F7 funding+basis 组合：|ρ|=0.30-0.39 信息冗余，3 市场全 FAIL（`stages/05/r3/f7-report.md`）
- F8 DVOL 方向信号：P1 corr +0.048 不显著，walk-forward 符号翻转（`stages/05/r4/f8_report.md`）
- F10-R4 温度→带宽预测：主判据弱 PASS（Brier 增量 0.002-0.011）+ 次判据 FAIL（方向正确率 13-15%）（`stages/05/r7/f10-r4-report.md`）

共同失败模式：无条件、全样本、日线频率。F8 报告指出候选 C = 宏观/跨资产 regime 增强是剩余未试维度。本任务是候选 C 的**调研先行**——先搞清楚文献和数据里有没有这个效应的证据，再决定值不值得花回测算力。

## 【SOP 索引】

- `sop/arena-loop-pipeline.md` §3.1 会话台账（本会话登记处）
- `projects/金融/D1-financial-market-analysis/tasks/TASKS.md`（F1-F10 全结论表）
- `projects/金融/D1-financial-market-analysis/loop-artifacts/stages/05/r4/f8_report.md`（候选 C 出处）
- `projects/金融/D1-financial-market-analysis/loop-artifacts/stages/05/r7/f10-r4-report.md`（最新负结果 + 机制诊断）

## 【实验设计】（调研型，非回测）

### Q1：文献证据（≥5 个独立来源，arXiv/期刊优先）

检索并交叉核验以下问题的已有研究：
1. 宏观变量（US 10Y yield / DXY / VIX / TED spread / risk-on-off proxy）对 crypto 收益的**条件预测力**——不是相关性，是"在 X regime 下微观信号才有效"这类交互效应。
2. crypto 特有的宏观敏感期：Fed 决议周、CPI 发布前后、QT/QE 切换窗口——事件研究文献。
3. 链上数据（active addresses / exchange flow / MVRV）与宏观变量的重叠度——如果链上已经编码了宏观信息，加宏观是冗余（重蹈 F7 覆辙）。
4. 已发表的 crypto × macro 因子模型（如 BIS 报告、学术 multi-factor model）里哪些宏观因子在 2022-2025 窗口存活。

每个来源记录：URL + 核心结论一句话 + 与本项目的关系（支持/反对/无关）+ conf（高/中/低）。

### Q2：数据可得性（免费源优先）

对每个候选宏观变量，确认可得的免费历史数据源：
- 变量名 / 频率 / 覆盖时间范围 / 源 URL / 是否需 API key / 大陆网络可达性
- 最低要求：日频、2020-01 起、无付费墙
- 候选清单（可扩展）：US 10Y yield、DXY、VIX、S&P500 收益、BTC dominance、stablecoin supply（Tether/USD Coin issuance）、global M2

### Q3：交互效应的事前检验设计（给回测用的，本轮不跑）

基于 Q1 文献，提出 ≤3 个具体的交互假设（格式：H: 当 [宏观条件] 时，[已有信号] 的 [指标] 会 [变化方向]），每个附：
- 理论依据（引用 Q1 来源编号）
- 所需数据字段
- 判定阈值（沿用 F6/F7 的 8 gate 协议）
- 若全部 FAIL 的收束判据

## 【失败降级】

- web 检索受限 → 降级为 arXiv API + 已知机构主页（BIS/Fed/NBER）直接抓取，conf 降一级标注
- 某变量数据源全断 → 记录断点，换同义代理（如 DXY 断则用 EURUSD 反推），标注 proxy
- 文献不足 5 个独立来源 → 如实报告数量，不凑数

## 【交付物】

1. `projects/金融/D1-financial-market-analysis/loop-artifacts/stages/05/r8/f10-r5-macro-survey.md` — 完整调研报告（Q1+Q2+Q3）
2. `projects/金融/D1-financial-market-analysis/loop-artifacts/stages/05/r8/macro-data-availability.json` — Q2 机器可读版（变量 × 源 × 状态矩阵）
3. 回执：repo URL + branch + commit_sha + 自报模型身份（如可知）

## 【给 Lead 的备注】

- 本任务是纯调研（1-loop 02 阶段性质），**不含回测**——回测决策等成璐看完调研后拍板（候选：继续 F10-R5 回测 / 收束归档 / 转候选 D 负结果报告）。
- 边界：不碰 T8/pfb 的任何文件；不修改 F1-F10 已有产物。
- 产出的 Q3 假设若被采纳进入回测，需走预注册冻结流程（human+ai 双签）。

## 补充（2026-11-05 本地核查）

**DVOL API 状态更新**：r7 报告称 Deribit `get_volatility_index_data` 已失效 → 2026-11-05 实测**已恢复**（BTC 小时数据正常返回，DVOL≈37.4）。Q2 数据可得性矩阵中 DVOL 行应标"可用"而非"失效"。若 R5 后续进入回测阶段，温度 T(t) 可恢复四件套（ATR/funding/vol/**DVOL**），与 R1 对齐。
