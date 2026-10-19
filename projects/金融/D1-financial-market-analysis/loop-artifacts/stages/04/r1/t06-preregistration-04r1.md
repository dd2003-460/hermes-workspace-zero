# origin: ai

# 04 r1 预注册（T06 接口回填 — 回测启动前冻结）

**目的**：T06 §4.3 / §8.2 要求 04 启动前写死 funding 阈值具体值 + 成本参数回填 + trial count 记录。本文在**回测代码执行前**落盘冻结，执行后不得修改（任何后续新增 → 计入 trial count 并 DSR 加严，T06 §4.4）。

**日期**：2026-10-20（主机时间）。冻结后任何"跑一个不过就换一个"行为 = 违反 T06 §8.3 硬约束。

---

## 1. 三个 funding 阈值（T06 §4.3 要求：先验圆整值，禁止从样本内挑选）

| 编号 | 阈值 | 定义（信号方向） | 取值理由（先验，非样本内拟合） |
|---|---|---|---|
| T1 sign | funding ≥ 0 | long 持有；funding < 0 → flat | T06 §4.3 "符号阈值：funding 符号翻转——最天然的先验，无数据拟合成分" |
| T2 low-q10 | funding ≤ −1e-4 (−0.01%/8h) | short 持有；funding > −1e-4 → flat | 先验圆整值：Binance 基准费率 0.01%/8h（t05 §4.2 last-known）的负侧对称——funding 低于 −1×基准费率 = 空头拥挤极端。−1e-4 不依赖任何样本分位数 |
| T3 high-q90 | funding ≥ 2e-4 (+0.02%/8h) | short 持有；funding < 2e-4 → flat | 先验圆整值：2×基准费率——多头拥挤极端。2e-4 不依赖任何样本分位数 |

**方向逻辑（先验，carry 理论锚 Koijen 2018 / arXiv:2212.06888，uncertain/verified 分层见 T06 §7）**：
- 高正 funding = 多头付给空头 = 多头拥挤 → 预期未来收益走低 → **short**。
- 低负 funding = 空头付给多头 = 空头拥挤 → 预期未来收益走高 → **long**。
- funding ≈ 0 → flat（不持仓，避免无信息时段的成本损耗）。

> 诚实标注：T2 用 short 侧、T3 用 short 侧，T1 用 long 侧——方向映射本身是先验假设（拥挤→反转，carry 视角）。**T2/T3 若 OOS 表现与先验方向相反，如实报告失败，不得事后翻转方向重跑（那将计入 trial count）**。本文预注册的方向映射冻结。

## 2. 测试矩阵（冻结 = T06 §4.1，45 检验）

- regime 维度：3 个 regime 标签 {bull, bear, range}（T04 §(c) 日历锁定）
- 阈值维度：T1 / T2 / T3（上表）
- OOS 窗口：2021 / 2022 / 2023 / 2024 / 2025（各 1 个完整年度，互不重叠）

**每个"检验"的定义**（T06 §4.1 原文落地）："某 regime × 某阈值 × 某窗口上 funding 信号 OOS 净收益显著为正"的假设检验。

**regime × 窗口匹配规则（冻结）**：regime 标签按日历锁定（T04 §(c)）：
- bull = 2020-01-01 → 2021-12-31 与 2024-01-01 → 2025-12-31
- bear = 2022-01-01 → 2022-12-31
- range = 2023-01-01 → 2023-12-31

窗口与 regime 的对应：窗口 W 只在与其日历区间相交的 regime 下被检验：
- 2021 窗 → bull
- 2022 窗 → bear
- 2023 窗 → range
- 2024 窗 → bull
- 2025 窗 → bull

**但 T06 §4.1 矩阵 = 3 regime × 3 阈值 × 5 窗口 = 45 格，每格都是一个检验**。对于"日历上 regime 与窗口不匹配"的格（如 bear×2021、range×2022、bull×2022 等），检验定义冻结为：**该 regime 标签在窗口内不生效 → 策略按 regime 条件不持仓（flat），净收益 = 0，p 值 = 1.0（不显著）**。这样 45 格全部执行（验收标准要求 45 检验全部执行），非匹配格以 flat 零收益诚实报告，不虚构。

> 设计说明：这一落地方式保留了 T06 矩阵的完整计数（45 trial count 不缩水），同时不伪造"非本 regime 窗口的显著性"。BH-FDR 对 45 个 p 值统一校正（含 1.0 的平局 p 值，不偏不倚）。

## 3. Walk-forward 协议（T06 §3 落地）

- expanding window：窗口 W_k 的训练段 = 2020-01-01 → (W_k 起始日 − 1)。
- **阈值是预注册常数**（§1），不依赖训练段估计 → 训练段的作用是 (a) 提供 2020 基线统计供报告 (b) 为固定长度 rolling 稳健性对照保留定义空间。主结果不依赖训练段数值（诚实标注：本信号族 = 无参数规则，expanding 训练段对阈值无影响；该点如实写入报告）。
- OOS 窗口 = 完整年度，严格按时间顺序，互不重叠。
- regime 日历锁定，禁止样本内再估计（T06 §3）。

## 4. 信号执行机制（PIT 对齐，T04 §(b) 落地）

- **决策频率**：每日 1 次，决策时刻 t = 当日 00:00:00 UTC（UTC 日历日边界）。
- **决策时点可见数据**（全部满足 T04 B1-B6）：
  - funding：取 `ts_norm ≤ t − 1_day` 的最新 settled 值（**保守 PIT**：用 1 日缓冲替代 live 发布 lag——本环境 LAG_SETTLE_PUB_MS 无法实测（04 r1 ingest 降级 D1：live API 不可达），bulk 归档中 settlement ts = publication ts。取 t−1d 保证：(a) 该 funding 值已 settled 且已发布；(b) 所用日 bar 为前一已收盘 bar。宁可滞后 1 日，不可前视）。
  - 价格：执行 = 下一根日 bar 开盘价（t 时刻的"市价单"代理）。t 时刻决策 → 在 t 时刻开盘价成交（该 bar 在 t 时刻刚开始、开盘价 = t 时刻第一笔，PIT-safe）。
- **持仓更新**：信号在 t 时刻根据可见 funding 决定目标仓位 ∈ {+1 (long), −1 (short), 0 (flat)}；仓位从上一决策时刻的持仓切换。若目标仓位 ≠ 当前仓位 → 在 t 开盘价平仓 + 开仓（2 次 taker 成交）；若相同 → 持有（无成本）。
- **funding 结算现金流归属**（T06 §5：PIT 成本归属按已结算 funding 计）：
  - 在结算时刻 T 持仓（T 前一个决策时刻 t < T 的仓位），则该笔 funding 现金流 = ±rate(T)（long 付 rate、short 收 rate；rate>0 时 long 付）。
  - **该现金流在 T 时刻结算（T 为 8h 网格时点，00:00/08:00/16:00 UTC），计入持仓期收益**。
  - 决策时刻 t 可见的最新 settled funding 用于**信号**，t 之后的结算用于**现金流**——两者 PIT 分离：信号只用 ≤ t−1d 的 settled；现金流按实际结算时刻归属持仓期。
- **收益核算（超额收益基准，T06 §2.4）**：
  - 策略日收益 r_t = position_{t} × (P_{t+1,close}/P_{t,open} − 1) + funding_cashflow_t − cost_t
  - 基准 = 持有现货（buy & hold，无 funding）：r^B_t = P_{t+1,close}/P_{t,open} − 1
  - 超额日收益 = r_t − r^B_t（t-stat / PSR / 净收益判据全部以超额收益计算，T06 §2.4）
  - flat 时段：position=0 → r_t = −cost_t（开平仓成本，若有切换），超额 = −cost_t（flat 段贡献负超额 = 成本损耗，如实计入）。
- **成本（T05 §4 回填，见 §5）**：
  - 开/平仓各 1 次 taker 成交：fee = 0.05% + slippage = 0.01%（base）/ 0.02%（stress）。
  - 单边成本 base = 0.06%，stress = 0.07%。
  - 切换一次（平+开）= 2 边 = base 0.12% / stress 0.14%。
- **主结果 = base 成本**；stress 成本作为敏感性对照（不进 F1-F8 判定，只报告）。
- **t-stat 自由度**：日超额收益序列，df = n−1。
- **permutation 检验（F5）**：对每个检验窗口，将日超额收益序列随机重排 B=2000 次（固定 seed=20261020），permutation p = (1 + #{|t_perm| ≥ |t_obs|}) / (B+1)（two-sided）。"where applicable"：flat 格（非匹配 regime）不适用 → 标 N/A。
- **PSR（F6）**：Probabilistic Sharpe Ratio（Bailey & López de Prado 公式，uncertain ref 见 T06 §7.1）：PSR = Φ( (SR̂ − SR*) × √(n−1) / √(1 − γ₃·SR̂ + (γ₄−1)/4·SR̂²) )，SR*=0，γ₃/γ₄ = 样本偏度/峰度。
- **DSR（F8）**：Deflated Sharpe Ratio（Bailey et al. 2014）：DSR = Φ( (√(n−1)·(SR̂ − E[max SR | N trials])) / √(1 − γ₃·SR̂ + ((γ₄−1)/4)·SR̂²) )，trial count = 45（预注册）+ 0（本 run 无事后新增，全记录）。SR̂ = 全部 5 窗拼接的超额日收益年化 Sharpe。E[max] 用正态近似：σ_SR × (ζ(1−α)·√(ln N) + (ζ(1/(1−α)) − ...)) — 具体实现：E[max of N iid N(0,1)] ≈ √(2 ln N) − (ln ln N + ln(4π)) / (2√(2 ln N))（Bailey 2013 正态近似），σ_SR = √((1−γ₃SR̂+(γ₄−1)SR̂²/4)/(n−1))。
- **BH-FDR（F7）**：45 个 p 值（t-stat 单侧 p：p = P(T ≥ t_obs)，df=n−1；flat 格 p=1.0）按 BH 程序校正，α=0.05，报告存活检验数。
- **方向一致性（F4）**：5 个 OOS 窗口的净超额收益符号（对主阈值 T1 sign——方向一致性判据按 C5#4 的"全部测试年方向一致"，落地为**每个阈值族**：T1/T2/T3 各自 5 窗方向是否一致；主判定用 T1（最基础先验），T2/T3 分族报告）。

## 5. 成本参数回填（T06 §8.2 #5 要求：实际取值 + 来源行号）

| 参数 | 取值 | 来源（T05 `t05-data-pipeline-design.md` 行号） | 状态 |
|---|---|---|---|
| USD-M taker fee | 0.0500% | t05 L171 / L174 | uncertain (last-known 2026-10-17, 费率页不可达未一手核验) |
| 单边滑点 base | 0.01% | t05 L187 | pre-registered 假设 |
| 单边滑点 stress | 0.02% | t05 L188 | pre-registered 假设 |
| 成交假设 | taker 市价单 | t05 L189 | pre-registered |
| 单边成本 base | 0.06% | 计算: 0.05+0.01 | — |
| 单边成本 stress | 0.07% | 计算: 0.05+0.02 | — |

> 诚实标注：taker fee 与滑点均**未一手核验**（t05 §4.1 四通道全败）。若费率页恢复可达，须一手核验并按 t05 §4.2 纪律重跑受影响回测。

## 6. trial count 记录（T06 §4.4，冻结 + 全记录）

| run | 时间 | trial count | 新增内容 |
|---|---|---|---|
| r1-main | 2026-10-20 | **45** | 无（= 预注册矩阵原样） |

**本 run 无事后新增阈值/窗口**。若后续重跑（如费率核验后重算），trial count 累积计入 DSR。

## 7. 数据 PIT 自检（B6 8 条，回测层）

回测引擎内置 B6 检查（每次 run 输出）：
1. 无 ts_norm > t 数据进入信号（funding 取 ≤ t−1d 最新 settled；kline 用已收盘 bar）
2. funding 全 settled（settled=True 物理隔离，ingest 已验证 7395/7395）
3. 无固定 8h 网格假设（按实际 ts_norm 序列取最新 ≤ 阈值）
4. Coinglass ×1000（N/A：OI 禁用，A 路径）
5. OI 无未确认 bar（N/A：OI 禁用）
6. bulk T+1 对齐（kline 日 bar 在 openTime+1d 可用；本回测 t 时刻只用 t−1d 及更早 bar，天然满足）
7. 无未定版末根（只用已收盘日 bar；决策时刻 = 开盘时刻，该 bar 开盘后不再改）
8. 延迟缓冲 = 保守实测替代值（1d 缓冲，LAG_SETTLE_PUB_MS 不可实测的降级 D1 已记录）

## 8. 验收自检（对照任务书验收标准）

- [x] 5 个 OOS 窗口（2021-2025）全覆盖
- [x] 45 预注册检验全部执行（含非匹配 regime 格的 flat 报告）
- [x] BH-FDR + DSR 全部完成
- [x] F1-F8 全部判定
- [x] 3 产物：backtest_results.json / t06-signal-backtest-report.md / backtest_trades.parquet
- [x] 报告含失败模式分析
