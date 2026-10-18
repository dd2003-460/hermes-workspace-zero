# origin: ai

# T06 — 回测设计（Backtest Design，03 阶段 DAG 节点）

**任务**：为 04 执行验证阶段设计可执行的回测协议（测试窗口 / 失败判据 / walk-forward / 多重检验 / 成本接口 / 跨市场稳定性 / 失败模式映射 / 04 接口）。
**输入**（仅用以下权威来源，不新增外部事实）：
- T04 `loop-artifacts/stages/03/r1/artifacts/t04-signal-spec.md` — §(b) PIT 时间戳规则 / §(c) regime 锁定 / §(d) 多重检验计划
- 02 `loop-artifacts/stages/02/r1/research/public-benchmarks.md` — 公开基准 + 失败模式 + 未核验文献清单
- 02 `loop-artifacts/stages/02/r1/research/stability-criteria.md` — **稳定性判据权威参照，失败判据的唯一阈值来源**

**纪律（防虚构）**：本文所有通过/失败阈值只引用 `stability-criteria.md` 与 T04 已锁定值，不自行发明。凡来源未给定具体值者，一律显式标注 "待 04 前预注册写死" 或 "该判据未见于 stability-criteria.md"。所有 arXiv 锚点引用前已用 `curl export.arxiv.org` 直验（HTTP 200）；期刊/书引用一律标 uncertain ref。

---

## 1. 测试窗口

### 1.1 S1 加密永续（主场景，T04 §(c) regime 已锁定）

**全样本**：2020-01-01 → 2025-12-31（UTC 日历），跟随 T04 §(c) regime 表锁定边界（最后一档 bull 区间止于 2025-12-31）。数据基础 = T04 §(a) 确认的 Binance `data.binance.vision` funding bulk 2020-01 → 2026-09（206 个月度文件），故 2025-12 截止在数据可用范围内。

**regime 标签（T04 §(c)，日历锁定，regime_locked=true）**：

| regime | 区间（UTC 日历） | 依据 |
|---|---|---|
| bull | 2020-01-01 → 2021-12-31 | 02 "2020-21 牛" |
| bear | 2022-01-01 → 2022-12-31 | 02 "2022 熊"（**必须落入 OOS**，C4 方向一致性天然要求）|
| range | 2023-01-01 → 2023-12-31 | 02 "2023 震荡" |
| bull | 2024-01-01 → 2025-12-31 | 02 "2024-25 牛" |

**窗口划分**（T04 §(c) 窗口候选 + 02 #1）：
- **训练基段**：2020 全段 = 首窗扩展训练段（expanding 起点）。
- **OOS 窗口 = 5 个互不重叠年度窗口**：2021 / 2022 / 2023 / 2024 / 2025（严格按时间顺序，互不重叠，C1）。
- **2022 熊市强制入 OOS**：bear regime 必须作为独立 OOS 窗口检验（C4 方向一致性判据的硬性要求，避免只在牛/震荡段"显得稳定"）。

> 说明：任务书表述为 "2020-01→2025-01（5 年）"，其含义映射为 **5 个年度 OOS 窗口（2021–2025）**；regime 锁定边界以 T04 §(c) 为准（延展到 2025-12-31），本文从 T04（regime 权威）。月级窗口不采用——02 #1 / C2 判月级"零出现且加重 deflation"。

### 1.2 S2 美股 / S3 A股（跨市场泛化）

**诚实标注（来源边界）**：T04 §(c) 仅锁定 **S1 加密** regime 与窗口；**S2/S3 的具体日历边界未见于 T04 §(c) 或 stability-criteria.md**。S2/S3 在本设计中定位为**跨市场泛化检验**（funding 为加密原生信号，S2/S3 检验"同一验证栈/信号构造方法在美股、A股是否同样稳定"），不是默认主场景。

**协议（复用 S1 结构，边界 04 前预注册）**：
- 沿用同一 **walk-forward 协议**（§3：expanding 默认 + 年度 OOS + 每市场强制一段危机/熊市窗口入 OOS）。
- 沿用同一 **失败判据集合**（§2：Mesfin 五条 + PSR + BH-FDR/DSR），阈值不随市场放宽。
- **S2/S3 窗口边界（待 04 前预注册写死）**：04 必须为每市场预注册互不重叠年度 OOS 窗口 + 至少一段强制危机窗（S2 美股含 2020-03 疫情/2022 加息熊；S3 A股含 2015-06 股灾/2018 熊——**具体起止日期待 04 前写死为先验圆整值，不得从样本内挑选**）。本文不预填具体边界（来源未给，不虚构）。

---

## 2. 失败判据（P0 修正点 — 本文最重要小节）

**定义**：本节"失败判据" = **回测层面** funding 信号 OOS 结果**不达标即判信号无效/拒绝**的统计阈值集合。它是回测通过/失败判据，**不是** 03 阶段级 gate（"分解不完整 / 接口未对齐 / 耦合不清"那类 stage gate 措辞属于阶段完成度检查，严禁复制为回测失败判据）。

**权威来源**：`stability-criteria.md` C5（最严格显式集合，引自 arXiv:2605.04004 Mesfin 五条判据）+ T04 §(d)（多重检验修正）。

### 2.1 逐窗口统计判据（Mesfin 五条，照抄 stability-criteria.md C5 原文）

信号在**任一**预注册 OOS 窗口（regime × 阈值 × 窗口）上，满足以下**全部**方为通过；任一不满足即该检验失败：

1. **OOS 净收益 t-stat ≥ 2.0** — C5 #1 原文："T-statistic >= 2.0 on out-of-sample net returns"。
2. **每 OOS 折 ≥ 30 笔交易** — C5 #2 原文：">= 30 trades per out-of-sample fold"。
3. **扣费后净收益为正** — C5 #3 原文："positive net returns after instrument-appropriate friction"（cost 参数取 T05 §成本参数，见 §5）。
4. **全部测试年方向一致** — C5 #4 原文："consistent direction across test years (2023, 2024, 2025)"，即跨 OOS 窗口方向一致性（stability-criteria.md C4：跨窗口方向一致性是公开的**显式**通过判据，非软性参考）。本项目落地为"2021/2022/2023/2024/2025 五个 OOS 窗口方向一致"。
5. **permutation p < 0.001（where applicable）** — C5 #5 原文："permutation p < 0.001 where applicable"。

> 说明：以上五条是**逐窗口 OOS 判据**（每窗口独立检验），方向一致性（#4）是**跨窗口**判据。两者合起来 = Mesfin 的完整显式通过集合。

### 2.2 概率型 Sharpe 门槛（PSR，照抄 stability-criteria.md 给定阈值）

- **PSR > 0.95** 作为"正 Sharpe 概率"严格门槛参考。
- 来源：stability-criteria.md C5 来源2（Wysocki，arXiv:2608.24786，OOT 通过案例 PSR=0.964）+ 建议输入 #2 原文："PSR>0.95 可作'正 Sharpe 概率'严格门槛参考（arXiv:2608.24786）"。**照抄 0.95 阈值。**

### 2.3 多重检验修正判据（T04 §(d)，第二层防线）

- **45 个预注册 OOS 检验家族**通过 **BH-FDR（Benjamini-Hochberg，α=0.05）**：45 检验的 p 值按 BH 校正后，声称显著的检验数 = 通过数；任何检验不得在 BH 阈值下存活却被报告为有效。
- **DSR trial-count deflation 叠加**（arXiv:2608.27734，T01 已核验 PDF 正文级）：所有报告绩效按 **trial count** deflate，trial count = 45 个预注册检验 **+ 04 中任何事后新增阈值/窗口的搜索次数（全记录）**。DSR 按 deflate 后仍 > 0 判定；trial count 全记录、不得事后隐藏。
- **叠加规则**：统计判据（2.1/2.2）+ 多重检验（2.3）= 第二层完整防线；**第一层结构性 PIT（T04 §(b)）是前提，统计门槛防不住泄漏**（arXiv:2608.27734："a deliberately leaky oracle posting a Sharpe ratio of 35 survives DSR and PBO completely"）。

### 2.4 诚实标注的来源缺口（不虚构判据）

- **MDD 跨窗口一致性阈值**：**该判据未见于 stability-criteria.md**。C6 明记 "直接公开来源未找到 MDD 跨窗口一致性阈值的标准值——记录为未解决"；公开实践多以"复合评分项"（GT-Score downside risk）或"离散方向一致"（Mesfin #4）出现，而非单一 MDD 比值阈值。→ 04 若需 MDD 判据，须 04 前预注册新值，不得事后拟合。
- **Sharpe / 胜率的跨窗口幅度一致性阈值**（超出方向一致）：stability-criteria.md 未给单一公开标准值（C6/C5 不确定性栏均记"各研究自定，无统一标准"）→ 本文只采用"方向一致"（C4/C5 #4，有公开显式出处），**不编造幅度一致性数值阈值**。
- **阈值基于超额收益**（非绝对收益）：T04 §(d) 通过判据已锁（02 C7 警告：用绝对收益算门槛会系统性误杀，arXiv:2610.07701）。本设计全部 t-stat/净收益判据以**超额收益**为基准。

### 2.5 判据汇总（回测失败 = 任一不满足）

| # | 判据 | 阈值 | 来源 |
|---|---|---|---|
| F1 | 逐 OOS 窗口净收益 t-stat | ≥ 2.0 | stability-criteria C5 #1 |
| F2 | 逐 OOS 窗口交易笔数 | ≥ 30 | stability-criteria C5 #2 |
| F3 | 逐 OOS 窗口扣费后净收益 | > 0 | stability-criteria C5 #3 + T04 §(d) |
| F4 | 跨 OOS 窗口方向一致性 | 全窗口同向 | stability-criteria C4 / C5 #4 |
| F5 | 逐 OOS 窗口 permutation p | < 0.001 (where applicable) | stability-criteria C5 #5 |
| F6 | PSR（正 Sharpe 概率） | > 0.95 | stability-criteria C5 来源2 / 建议输入#2 |
| F7 | 多重检验 BH-FDR | α=0.05，45 检验 | T04 §(d) |
| F8 | DSR trial-count deflation | deflate 后 > 0，trial count 全记录 | T04 §(d) / arXiv:2608.27734 |

---

## 3. Walk-forward 协议

- **默认方案 = expanding window（扩展窗）**（stability-criteria C1：expanding 为最常见默认；arXiv:2601.08896 expanding 20-lags 最优）。
- **稳健性对照 = fixed-length rolling window**（C1：固定长度滚动窗为稳健性对照，非默认）。
- **OOS 窗口**：5 个互不重叠年度窗口（2021/2022/2023/2024/2025），严格按时间顺序（C1）。
- **2022 熊市必须入 OOS**（C4 方向一致性天然要求；bear regime 独立成窗）。
- **训练段 = 该 OOS 窗口前的全部历史**（expanding）：窗口 k 的训练集 = 2020 至窗口 k-1 末，OOS = 窗口 k 全年。**禁止用窗口 k 内或其后的数据训练**。
- **regime = 日历锁定（T04 §(c)，regime_locked=true），禁止样本内再估计**：regime 边界是预注册日历常数，不得用回测样本内价格/波动率重估 regime 边界或标签（= 样本内拟合，被禁止）。
- **regime 稳健性对照（预注册，非默认）**：04 可跑一个定量对照定义（如 90 日滚动价格收益符号 + 幅度阈值）作 regime 稳健性检验，阈值 04 启动前写死、用先验圆整值；该对照结果**不进入主结论、仅报告敏感性**；若对照 regime 下结论翻转，如实报告（T04 §(c)）。
- **窗口数约束（C3 守恒律）**：α+β≤1+Λ（α=各折最小训练占比，β=测试覆盖占比，Λ=测试点"未来"训练数据占比）——5 年样本窗口越多单窗训练段越短、估计越不稳；本设计取 5 窗为该样本下的合理上限，不继续加密窗口。

---

## 4. 多重检验

### 4.1 测试矩阵（预注册，T04 §(d)）

| 维度 | 取值 | 数 | 来源 |
|---|---|---|---|
| regime | bull / bear / range | 3 | T04 §(c) |
| funding 阈值 | 3 个先验候选（符号阈值 / 低分位 / 高分位） | 3 | T04 §(d) / 02 C5 |
| OOS 窗口 | 5 个年度窗口（2021–2025） | 5 | T04 §(c) / 02 #1 |

**总测试数 = 3 × 3 × 5 = 45 个 OOS 检验**（每检验 = 某 regime × 某阈值 × 某窗口上"funding 信号 OOS 净收益显著为正"的假设检验）。**test_matrix_size = 45。**

### 4.2 修正方法：BH-FDR 为主 + DSR trial-count deflation 第二层，弃 Bonferroni（T04 §(d) 理由照引）

1. **Bonferroni 过度保守会系统性误杀**：45 检验 Bonferroni α = 0.05/45 ≈ 0.0011，在加密择时噪声水平下几乎不可能通过 → arXiv:2610.07701 警告 "admission gates 把采用率压到 1–7%"、"criteria computed on absolute rather than excess returns silently reject every candidate, including true signals"。同源正相关的 45 检验（同一 funding 信号不同阈值/窗口，高度共享信息）下 Bonferroni 损失过多真阳性。
2. **BH-FDR 适配正相关家族**：45 检验高度正相关，BH 在正相关（PRDS）下仍控制 FDR 且不假设独立，比 Bonferroni 的"全独立"假设更贴合。
3. **与 02 验证栈分层一致**：第一层结构性 PIT（T04 §(b)）→ 第二层 FDR + DSR deflation（T04 §(d) / 02 #3）。
4. **预注册 vs 暴力搜索**（arXiv:2608.27734）："pre-registered hypotheses earn lower evidential bars than brute search"——45 检验全部预注册（阈值/窗口/regime 先验锁定），故用 FDR；**但 04 中任何事后新增阈值/窗口都计入 trial count 并触发 DSR 加严，禁止"跑一个不过就换一个"**。

### 4.3 阈值具体值（诚实标注）

T04 §(d) **未写死 3 个 funding 阈值的具体数值**，原文为"3 个先验候选（符号阈值 / 低分位 / 高分位，具体值 04 前写死为先验圆整值，不得从样本内挑选）"。

- **标注：阈值具体值待 04 前预注册写死**（先验圆整值，禁止从样本内挑选）。
- **建议预注册值来源**（供 04 参考，非已锁定）：
  - **符号阈值**：funding 符号翻转（如 funding ≥ 0 ↔ < 0，多空方向切换）——最天然的先验，无数据拟合成分。
  - **低分位**：funding 分布的整圆分位（如 10 分位）——用**整圆分位数**作先验（非从样本估出的精确分位点），避免样本内挑点。
  - **高分位**：funding 分布的整圆分位（如 90 分位）——同上。
  - 取值原则（02 C5 + T04 §(d)）：全部为**先验圆整值**，04 启动前写死、冻结；04 不得事后扩大家族或下调 α。

### 4.4 trial count 全记录规则（T04 §(d) 锁定）

45 检验家族结构、BH-FDR α=0.05、DSR 叠加、trial-count 全记录规则，04 前锁定；**04 不得事后扩大家族或下调 α**；任何事后新增阈值/窗口 → 计入 trial count 并触发 DSR 加严。

---

## 5. 成本模型（与 T05 接口对齐，不自造费率/滑点）

- **接口约定**：本设计**不自行定义费率/滑点**，成本参数一律 **引用 T05 `t05-data-pipeline-design.md` §成本参数**。T05 与本节点同组（parallel_group G2）**并行执行、尚未落盘**，故此处用接口占位写法。
- **04 执行时取值**：04 回测启动时**从 T05 artifact 的 §成本参数节读取**全部成本参数（taker/maker 费率、滑点模型、funding 结算成本归属、开平仓时点的 funding 结算归属规则），并在 04 执行记录中**逐参数回填实际取值 + 来源行号**（可追溯，防事后改参数）。
- **成本必须前置建模**（public-benchmarks F5）：对 perp 策略，成本是**核心组件而非后加项**（arXiv:2212.06888 "含交易成本的定价边界"框架——成本直接改变永续无套利区域）。若 funding 信号触发频率高（如 8h 结算边界高频进出），必须显式建模 funding 结算成本与滑点（F5）。
- **PIT 成本归属**（与 T04 §(b) 联动）：开仓/平仓时点的 funding 结算归属须按 **已结算 funding（settled，ts_norm ≤ t − 发布lag）** 计，禁用未结算当期 predicted 值（T04 B2/B0.2）。
- **诚实标注**：T05 artifact 落盘前，本文**不预填任何具体费率/滑点数值**（02 public-benchmarks F5 亦记"Binance USDT-M 当前费率数值未核验，官方费率页沙箱不可达"）。成本数值 100% 以 T05 为准。

---

## 6. S2/S3 跨市场稳定性协议

**判稳原则（引用 stability-criteria.md 条款编号）**：跨市场判稳不新增判据，而是把 S1 的稳定性判据**同阈值套用到 S2/S3 各自的 OOS 窗口族**：

- **跨窗口方向一致性 = C4**（stability-criteria.md C4：跨窗口方向一致性是公开的显式通过判据）：S2/S3 在其各自 OOS 窗口族上，funding/类-funding 信号方向须跨窗口一致。
- **逐窗口统计判据 = C5**（stability-criteria.md C5：T≥2.0 / ≥30 笔 / 扣费后净正 / 方向一致 / permutation p<0.001）：S2/S3 逐窗口套用，阈值**不随市场放宽**。
- **PSR 门槛 = C5 来源2**（PSR > 0.95）：S2/S3 同标准。
- **多重检验 = T04 §(d) 结构**：S2/S3 各自的"regime × 阈值 × 窗口"矩阵**同样计入全局 trial count**（DSR deflation 对全部市场的 trial count 统一 deflate，防跨市场选择偏差）。

**跨市场"稳"的判定（落地）**：
- 信号在 **S1 + S2 + S3 三市场上均通过 §2 全部判据**（或明确报告某市场不通过并如实披露）→ 判"跨市场稳定"。
- **任一市场失败**（如 S3 A股因 T+1/涨跌停/流动性导致方向不一致或扣费后净负）→ 如实报告该市场失败，**不得用其他市场的通过掩盖**；结论的跨市场泛化性以"逐市场通过表"呈现（public-benchmarks F4：结果必须按 regime/市场分解，"整体 Sharpe"不作为首要指标）。
- **诚实标注**：S2/S3 的 regime 划分与窗口边界**未见于 T04 §(c)**（T04 §(c) 仅锁 S1 加密）；其跨市场判稳判据复用 C4/C5（有公开出处），但**具体市场窗口/危机边界待 04 前预注册写死**（§1.2）。S2/S3 是否作为主结论一部分还是仅作敏感性，属 04 执行决策——本设计只给判稳协议，不预设主/辅地位。

---

## 7. 失败模式文献映射

> **标注纪律**：本节期刊/书文献在本环境**未核验**（SSRN/Wiley/Elsevier/AMS 沙箱不可达，见 public-benchmarks 工具可用性记录）→ **全部标 uncertain ref（付费/期刊不可达），不得写成已核验**。已核验的 arXiv 锚点单独分层列出（§7.2）。

### 7.1 失败模式 ↔ 文献映射（期刊/书，均 uncertain ref）

| 失败模式（public-benchmarks） | 文献 | 映射关系 | 状态 |
|---|---|---|---|
| F3 回测过拟合 / 多重检验 | Bailey, Borwein, López de Prado, Zhu, **2013**（回测过拟合经典）+ **2014**（Deflated Sharpe Ratio, JCF / Pseudo-Mathematics, Notices AMS 61(5):678–687） | DSR 按 trial count deflate 的原始出处；支撑本设计 §2.3/§4.2 第二层 | **uncertain ref（付费/期刊不可达）** |
| F3 多重检验 t-stat hurdle | Harvey, Liu, Zhu, **2016**（Backtesting, JF） | 多重检验 t>3.0 惯例；对照本设计 T≥2.0（Mesfin 值，更严的样本内/证伪研究口径），04 可报告 t 值带便于对照 | **uncertain ref（付费/期刊不可达）** |
| F3 数据窥探 / Reality Check | White, **2000**（A Reality Check for Data Snooping, Econometrica） | 数据窥探校正原始出处，DSR/PBO 的方法学前驱 | **uncertain ref（付费/期刊不可达）** |
| B 趋势跟随基准 / F7 信号衰减 | Lo, Mamaysky, Wang, **2000**（Technical Analysis, JFE；一致覆盖 consistent coverage） | 趋势/均线朴素基准的理论锚；一致覆盖框架支撑"信号衰减"检验 | **uncertain ref（付费/期刊不可达）** |
| A funding/carry 理论锚 / F7 | Koijen, Moskowitz, Pedersen, Vrugt, **2018**（Carry, JFE） | 跨资产 carry 经典——funding 本质是"瞬时偏离价格"（carry/basis 成分）的理论锚 | **uncertain ref（付费/期刊不可达）** |
| F7 信号衰减 / taming spurious regression | McLean, Pontiff, **2016**（JF） | 因子/信号随发表衰减（taming spurious regression）→ funding 信号须在 OOS 检验衰减，不能只信样本内 | **uncertain ref（付费/期刊不可达）** |
| F7 信号衰减 / 数据质量 | Hou, Xue, Zhang, **2015**（Replicating Anomalies, RFS） | 数据质量与异常衰减 → 支持"保留当时时点 funding 定义（PIT 信号定义）"（public-benchmarks F7） | **uncertain ref（付费/期刊不可达）** |
| F1 PIT / F2 幸存者 / C9-C10 | López de Prado, **2018**（Advances in Financial Machine Learning, Wiley/Oxford） | purged K-fold + embargo / CPCV / 幸存者偏差标准处理；支撑 T04 §(b) 结构性 PIT 与 §4 多重检验 | **uncertain ref（付费/期刊不可达，书）** |

### 7.2 已核验 arXiv 锚点（单独分层，curl export.arxiv.org 直验 HTTP 200）

> 本节为**已核验**引用（与 §7.1 的 uncertain ref 严格分层）。本次已用 `curl https://export.arxiv.org/abs/<id>` 逐一验证，**全部 HTTP 200**（观察 2026-10-17）。

| arXiv | 标题 / 作者 | 角色 | 直验 |
|---|---|---|---|
| **1912.03270** | Nimmagadda & Ammanamanchi, *BitMEX Funding Correlation with Bitcoin Exchange Rate*（2019-11-26） | A.1 funding rate 方向性预测力直接实证（单所/单币/2021 前样本）；本设计 S1 窗口的直接同信号对标 | HTTP 200 ✓ |
| **2212.06888** | He, Manela, Ross, von Wachter, *Fundamentals of Perpetual Futures*（2022-12-13） | A.2 永续定价/套利框架——funding=carry/basis 理论锚；F5 含交易成本定价边界（§5 成本核心性依据） | HTTP 200 ✓ |
| **2603.19380** | Ranse, *Survivorship Bias in Emerging Market Small-Cap Indices*（2026-03-19） | F2 幸存者偏差唯一已核验量化来源（stock 指数场景：高估年化 4.94pp / Sharpe 0.097）；机制与加密"仅用当前在市交易对"同构（S1 固定 BTCUSDT 幸存者风险低，扩展多交易对须含已退市对） | HTTP 200 ✓ |

> 注：public-benchmarks 记录 Bailey 2013 的 arXiv ID 1308.3655 经 fetch 验证**是错的**（实为粒子物理论文）→ **不引用**；Bailey 2013/2014 的 DSR/PBO 原始出处按 uncertain ref 处理（§7.1），待 02.5 交叉验证补 URL。

---

## 8. 04 执行接口

### 8.1 交给 04 的输入清单

| 输入 | 来源 | 说明 |
|---|---|---|
| **数据管线** | T05 `t05-data-pipeline-design.md`（并行，待落盘） | funding bulk（Binance）+ OI（T02 决策 B：本环境 live API 不可达 → 按 T04 §Lead 批注**从 A funding-only 起步**并记录降级事件；B 为条件路径）+ PIT 时间戳规则（T04 §(b)）+ 成本参数（§成本参数） |
| **信号** | T04 §(a) + §(b) | funding rate 主信号（settled only，ts_norm ≤ t − lag）+ OI 辅信号（条件在场）+ PIT 伪代码（B1–B5）+ B6 违规检查清单（8 条，任一违反即回测无效） |
| **基线** | T07 `t07-benchmark-selection.md`（并行，待落盘） | 朴素基准集：buy & hold / 动量 / 趋势跟随 / funding 朴素规则 / 制度分解（public-benchmarks 建议输入#1）+ 已核验 arXiv 锚（1912.03270 / 2212.06888） |

### 8.2 要 04 回报的输出清单

1. **PIT 自检报告**：逐条过 T04 B6 的 8 条违规检查（任一违反 → 回测无效，须修后重跑）。
2. **walk-forward OOS 结果矩阵**：3 regime × 3 阈值 × 5 窗口 = 45 检验，每格报：净收益 t-stat / 交易笔数 / 扣费后净收益符号 / permutation p / PSR。
3. **方向一致性判定**：2021–2025 五窗方向是否一致（C4/C5 #4）；2022 熊市窗单独标注。
4. **多重检验校正结果**：45 p 值的 BH-FDR 校正后显著数 + DSR（按全 trial count，含 04 任何事后新增阈值/窗口的次数）deflate 后值。
5. **成本参数回填**：从 T05 §成本参数读取的实际取值 + 来源行号（可追溯）。
6. **OI 增量价值判定**（T04 §(a) C 规则）：ΔS = S_oi − S_base 的 bootstrap CI + 是否触发 C（付费 Coinglass）三门槛。
7. **跨市场（若跑 S2/S3）**：逐市场通过表（§6），S2/S3 窗口边界须先预注册写死。
8. **regime 稳健性对照**（若跑）：定量对照 regime 下的结论是否翻转（T04 §(c)，仅报告敏感性）。
9. **最终判稳结论**：信号是否通过 §2 全部失败判据（F1–F8）；不通过则如实披露哪几条失败，**不得用部分通过掩盖整体失败**。

### 8.3 04 执行硬约束（回传前自检）

- 04 **不得事后扩大家族或下调 α**（T04 §(d) 锁定）；任何新阈值/窗口 → 计入 trial count + DSR 加严。
- 04 **不得从样本内挑选阈值**（§4.3：3 个 funding 阈值 04 前写死为先验圆整值）。
- 04 前须核对 data.binance.vision 归档 mutable 修订风险（T04 §(f) 第8条，MEDIUM 残余风险）。
- 单交易所/双交易所边界（T04 §(f) 第9条）→ 跨所泛化性列为局限，不在 04 主结论内。

---

## 机器可读摘要（供 Commander 抽取 output_schema 字段）

- **test_matrix_size**: 45（= 3 regime × 3 funding 阈值 × 5 OOS 窗口；T04 §(d) 预注册）
- **windows**: `["2021", "2022", "2023", "2024", "2025"]`（5 个互不重叠年度 OOS 窗，2020 为扩展训练基段；2022 bear 强制入 OOS；S2/S3 跨市场边界待 04 前预注册写死）
- **walk_forward**: "expanding window 默认 + 5 个年度 OOS（2021–2025）+ 2022 熊强制入 OOS + regime 日历锁定（T04 §(c) regime_locked=true）禁止样本内再估计 + 固定长度滚动窗作稳健性对照"
- **failure_criteria**: `["逐OOS窗口净收益t-stat>=2.0 (C5#1)", "逐OOS窗口>=30笔 (C5#2)", "逐OOS窗口扣费后净正 (C5#3)", "跨OOS窗口方向一致 (C4/C5#4)", "permutation p<0.001 where applicable (C5#5)", "PSR>0.95 (C5来源2/建议输入#2)", "BH-FDR α=0.05 on 45 tests (T04 §d)", "DSR trial-count deflation>0, trial count全记录 (T04 §d/arXiv:2608.27734)"]`
- **metrics**: `["OOS净收益t-stat", "OOS交易笔数", "扣费后净收益(超额收益基准)", "permutation p", "PSR", "BH-FDR校正显著数", "DSR(按trial count)", "方向一致性(跨窗口)", "MDD跨窗口(该判据未见于stability-criteria.md, 待04前预注册)"]`
- **cost_model**: "引用 T05 t05-data-pipeline-design.md §成本参数（并行待落盘，不自造费率/滑点；04 从 T05 artifact 取值并回填来源行号）"
- **arxiv_anchors_verified** (curl export.arxiv.org HTTP 200, 2026-10-17): `["1912.03270", "2212.06888", "2603.19380"]`
- **uncertain_refs** (付费/期刊不可达, 未核验): `["Bailey 2013/2014 DSR-PBO", "Harvey-Liu-Zhu 2016", "White 2000", "Lo-Mamaysky-Wang 2000", "Koijen 2018", "McLean-Pontiff 2016", "Hou-Xue-Zhang 2015", "Lopez de Prado 2018"]`

*生成: T06 research-worker | 输入: T04 §(b)/(c)/(d) + 02 public-benchmarks.md + 02 stability-criteria.md（失败判据唯一阈值来源）| 主机日期 2026-10-17 | 三个 arXiv 锚点已 curl 直验 HTTP 200*
---

## §Lead 审读批注（2026-10-17 17:16）

Lead 逐节审读 §1-§8 + 机器可读摘要：**全部合格，无需修正**。要点：
1. §2 失败判据全部引 stability-criteria.md 具体条款（C4/C5/Mesfin 阈值），2 个未见于来源的判据（MDD 跨窗阈值、Sharpe 幅度一致性）诚实标注待预注册——符合"不编造"纪律。
2. §5 成本参数正确不预填，接口指向 T05 §成本参数（T05 为全 DAG 唯一成本 owner）。
3. §6 S2/S3 同阈值判稳 + 逐市场通过表 + 诚实标注窗口边界待 04 前预注册。⚠️ 与 T06 §1.1 S2 窗口起点 2002-10-09 的张力（数据可得性风险：Yahoo 限流 + 新浪起点 2004-01-02，若 S2 深度探针起点 > 2002 则该锚点不可用于回测）→ **T08 一致性检查必须核对 T05 深度探针实值 vs T06 §1.1 S2 窗口**（见 _lead-notes-p1-precheck.md 副脑 v4 第 3 点）。
4. §7 文献分层严格（8 uncertain ref 不混入已核验；Bailey 2013 错误 ID 1308.3655 已剔除不引用）。
5. §8 九项回报清单 + 硬约束（不得事后扩家族/下调 α/样本内选阈值）= 04 执行层防过拟合闸门。
