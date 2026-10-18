# origin: ai

# T04 — 信号架构定稿 Spec（03 阶段 join 节点）

**任务**：合成 T01/T02/T03 产物为信号架构定稿 spec。
**输入**（input_refs，仅用此三件 + 02 stability-criteria.md，不新增外部事实）：
- T01 `loop-artifacts/stages/03/r1/artifacts/t01-arxiv-260827734-verify.md`（arXiv:2608.27734 直验，verdict=exists，confidence=0.95）
- T02 `loop-artifacts/stages/03/r1/artifacts/t02-oi-source-decision.md`（OI 源决策 B，confidence=0.70，条件触发 C 预注册）
- T03 `loop-artifacts/stages/03/r1/artifacts/t03-negative-search-protocol.md`（缺口声明，gap_confidence=0.75，arXiv 范围内）
- 02 候选集 `loop-artifacts/stages/02/r1/research/stability-criteria.md`（regime/窗口/阈值候选）

**输出 schema 自检**：confidence=0.72（合成置信度，取三输入 0.95/0.70/0.75 的保守合成——受限于 T02 的 Bybit 可达性与 T03 的付费库未覆盖）；pit_rule=见 §(b) 伪代码 `available_at`；regime_locked=true（§(c) 已锁定）；sections=6 节齐全 (a)–(f)。

---

## (a) 信号清单

**主信号：funding rate（确认，唯一默认主信号）**

- 定位：加密货币永续合约 funding rate 作为**主择时/市场状态信号**（拥挤度/情绪维度）。
- 数据基础：Binance data.binance.vision fundingRate 月度 bulk 文件 2020-01 → 2026-09 实存 **206 个**（Lead 直探实证），bulk 可复现。
- 确认依据：02 研究锚定 + T03 负检索确认"公开检索未找到以 funding rate 为主择时信号的已发表回测"（arXiv 范围内，gap_confidence=0.75）→ funding 主信号地位既有数据支撑又有新颖性空间。

**辅信号：OI（持仓量）——T02 决策 B 全文引用**

> **T02 推荐（原文核心）**：推荐 **B（免费OI：Bybit至上线日为主深度源 + Binance 30d为近期交叉验证）** 作为 04 回测的**默认OI路径**。A 为降级后备，C 为条件触发分支。
>
> **分支逻辑（原文）**：
> - 默认 → **B**
> - Bybit API 04 环境不可达 → 降级 **A**（仅 funding），记录降级事件
> - 04 回测证明 OI 增量价值>阈值 **且** 免费 OI 源是约束瓶颈 → 触发 **C**（付费补齐数据质量/覆盖）

**A 降级规则（全文引用）**：A = 放弃 OI（仅 funding）。仅在 **Bybit API 于 04 执行环境不可达（reproducibility break）时**作为降级路径启用，并**记录降级事件**。事实基础：openInterest 归档 404（真不存在）→ OI 无 bulk 路径，只能 live API 取数；若 API 不可达，OI 信号整体剔除，funding 单信号继续（funding 有 206 个 bulk 月度文件可复现）。

**C 条件触发规则（全文引用，预注册阈值，非事后拟合）**：C = Coinglass 付费 $29/mo，**仅当 04 回测满足以下全部条件**时才付费启用，任一不满足则保持免费路径：

| 门槛 | 判据 | 预注册值 |
|---|---|---|
| ① 价值门槛 | walk-forward OOS 上 ΔS = S_oi − S_base（funding-rate-only 基准 vs 加 OI）的绝对值 ≥ 阈值，且 ΔS 的 95% bootstrap CI（≥3 个 walk-forward 折）下界 > 0 | **ΔS ≥ +0.20**（退化判据：样本不足时改用 OOI 特征 walk-forward OOS IC ≥ +0.05 且符号跨折稳定 ≥3 折同号） |
| ② 免费源瓶颈门槛 | 免费 OI 有效 bar 覆盖率 < 阈值，或 Bybit 延迟警示触发率 > 阈值 | **有效 OI bar 覆盖率 < 95%**，或 Bybit 延迟警示触发率 > **5%** 的回测 bar |
| ③ 成本门槛 | Coinglass 实际月费 ≤ 上限 | **≤ $30/mo**（若涨价 > $50 不启用） |

**触发逻辑（原文）**：仅①成立但②不成立 → 保持免费 B 不付费；①+②同时成立 → 触发 C；①不成立 → 不付费；③不成立 → 不付费。阈值 04 前锁定，04 不得事后下调以通过门槛。

**信号角色汇总**：funding rate = 主信号（默认在场）；OI = 辅信号（默认在场，免费可逆，04 检验增量价值后去留）；无第三个信号。

---

## (b) PIT 时间戳严格规则（全文最关键 — 伪代码级）

> **副脑判定：PIT 前视偏差是审稿人第一攻击点。** T01 已核验的 arXiv:2608.27734 给出核心证据："a deliberately leaky oracle posting a Sharpe ratio of 35 survives Deflated Sharpe and probability-of-backtest-overfitting testing completely"（故意泄漏的 oracle Sharpe=35 能完整通过 DSR 与 PBO 检验）——**统计门槛（第二层）防不住未来信息泄漏，结构性 point-in-time（第一层）是前提，不是可选项**。本节把第一层写成可执行伪代码。

### B0. 总原则（五条硬规则）

1. **UTC 毫秒归一**：所有时间戳在管道入口归一为 **UTC 毫秒整数**。Binance = Bybit = 原生毫秒（直接用）；**Coinglass = 秒 → ×1000**（02 §3 单位陷阱，仅 Coinglass 有）。归一是管道第一步，任何数据源进入回测前必过。
2. **funding 只用已结算值**：t 时刻仅用 `fundingRateTimestamp ≤ t` 的 **settled**（已结算）记录。settled 与 predicted（基于 mark price 实时推算的当期值）**分字段，不可混用**（Bybit 官方原文确认语义）。
3. **8h 间隔逐 symbol 可变**：funding 结算名义上 8h 一次，但**逐 symbol 的实际 `fundingRateTimestamp` 可变**（不同 symbol 上线时间/结算时刻不同）→ **禁止硬编码 `t − 8h` 网格假设**，只用该 symbol 自身的实际时间戳序列。
4. **数据可用 lag 与决策时刻对齐**：数据"存在"（有 timestamp）≠ 数据"可用"（决策时刻能拿到）。可用时刻 = 标称时间戳 + 发布 lag + 延迟缓冲，**不得假设 timestamp = 可用时刻**。所有 lag/缓冲参数化，04 实测校准。
5. **OI bar 起点语义**：OI bar 时间戳 = **bar 起点**（领域知识，02 未核验，04 须实测响应时间补证）→ t 时刻可用集 = {bar : `bar_start + bar_duration (+ 延迟缓冲) ≤ t`}。**保守策略 = 只用到上一根已确认 bar**。

### B1. 时间戳归一（管道第一步）

```python
def normalize_ts(ts_ms_or_s, source) -> int:
    """归一为 UTC 毫秒。source ∈ {Binance, Bybit, Coinglass}"""
    if source == "Coinglass":
        return int(ts_ms_or_s) * 1000        # 秒 → 毫秒（×1000）
    elif source in ("Binance", "Bybit"):
        return int(ts_ms_or_s)               # 原生毫秒
    else:
        raise ValueError(f"unknown source {source}")
```

### B2. funding 可用性谓词（主信号核心规则）

```python
# funding_records: 该 symbol 的已结算 funding 记录列表，每条:
#   { rate: float, ts_norm: int(UTC ms), settled: bool }
# 已按 ts_norm 升序。预测值 predicted 根本不在本表内（分字段，物理隔离）。

def latest_settled_funding(funding_records, t_ms) -> float | None:
    """t 时刻可用的最近一条已结算 funding。
    硬规则:
      R1: 只取 settled（本表只含 settled，predicted 物理隔离）
      R2: ts_norm <= t_ms（已结算值，未结算的当期值不可见）
      R3: 不假设 8h 网格 —— 只信该 symbol 自身的 ts_norm 序列
    """
    avail = [r for r in funding_records
             if r.settled and r.ts_norm <= t_ms]
    return avail[-1].rate if avail else None   # 取最近一条；无则 None（不填充、不外推）
```

### B3. OI bar 可用性谓词

```python
# oi_bars: 该 symbol 的 OI K 线，每条:
#   { bar_start: int(UTC ms, 起点), duration_ms: int, oi_value: float }
# 硬规则（B0.5）:
#   bar 时间戳 = bar 起点（领域知识，04 实测补证）
#   可用集 = { bar : bar_start + duration (+ 延迟缓冲) <= t }
#   保守策略 = 只用到上一根已确认 bar

def latest_oi(oi_bars, t_ms, delay_buffer_ms) -> float | None:
    """t 时刻可用的最近一根已确认 OI bar。
    delay_buffer_ms: 延迟缓冲参数（04 实测 Bybit 响应延迟分布后定值；
                     Bybit 官方承认极端行情有延迟警示 → 极端段用更保守缓冲）
    """
    avail = [b for b in oi_bars
             if b.bar_start + b.duration_ms + delay_buffer_ms <= t_ms]
    return avail[-1].oi_value if avail else None
```

### B4. 数据可用 lag 与决策时刻对齐（发布 lag 规则）

```python
# 关键: "下载到的文件/响应" 的可用时刻 = 标称时间戳 + 发布 lag，而非标称时间戳本身。
# 三种已识别的 lag（全部来自 02 研究，04 实测校准）:

LAG_RULES = {
  # (1) funding settled: 结算时刻 T 的值，在 T + LAG_SETTLE_PUB 后才可见
  #     （结算后交易所才发布；LAG_SETTLE_PUB = 04 实测的结算→发布延迟上界）
  "funding_settled":  lambda ts_norm, t_ms: ts_norm + LAG_SETTLE_PUB_MS <= t_ms,

  # (2) data.binance.vision bulk 文件: T+1 迟报
  #     日线文件次日发布("the next day")、月线文件当月第一周一发布
  #     → bulk 文件的可用时刻按 T+1 对齐时间戳（确切 UTC 时刻 04 补证）
  "bulk_daily":       lambda ts_norm, t_ms: ts_norm + 1_day + LAG_T1_MS <= t_ms,
  "bulk_monthly":     lambda ts_norm, t_ms: ts_norm + LAG_FIRST_MONDAY_MS <= t_ms,

  # (3) 实时未定版末根 K 线: 末根是进行中（未定版），收盘才冻结
  #     → 回测信号生成 禁用未定版末根（只用已收盘 bar）
  "kline_unconfirmed": lambda b: b.confirmed,   # 未定版 bar 直接排除
}

def data_available(source_kind, ts_norm, t_ms) -> bool:
    """统一判定: 标称时间戳为 ts_norm 的数据在决策时刻 t_ms 是否可用。"""
    return LAG_RULES[source_kind](ts_norm, t_ms)
```

### B5. 决策时刻信号生成（组装）

```python
def signal_at(t_ms) -> Signal:
    """t_ms = 决策时刻（UTC ms）。t_ms 由已收盘 bar 的收盘时刻 + 执行 lag 确定，
    不得指向未定版 bar 的内部时刻。"""
    f = latest_settled_funding(FUNDING[S], t_ms - LAG_SETTLE_PUB_MS)
    #    等价: ts_norm <= t_ms - LAG_SETTLE_PUB_MS 的最近 settled
    oi = latest_oi(OI[S], t_ms, delay_buffer_ms) if OI_ENABLED else None
    regime = regime_label(t_ms)          # §(c) 预注册 regime，日历锁定
    return Signal(funding=f, oi=oi, regime=regime, t_ms=t_ms)
```

### B6. PIT 违规检查清单（04 实现时逐条自检，任一违反即回测无效）

| # | 检查 | 对应规则 |
|---|---|---|
| 1 | 是否存在任何 `ts_norm > t_ms` 的数据进入 `signal_at(t_ms)`？ | B2/B3 |
| 2 | funding 是否混入了 predicted 当期值？（应物理隔离） | B0.2 |
| 3 | 是否假设了 8h 固定网格（`t − 8h`）而非实际 `fundingRateTimestamp`？ | B0.3 |
| 4 | Coinglass 时间戳是否已 ×1000 归一？（若启用 C 分支） | B0.1 |
| 5 | OI 是否使用了 `bar_start + duration > t_ms − buffer` 的未确认 bar？ | B3 |
| 6 | bulk 文件是否按 T+1 对齐（日线次日/月线当月第一周一）？ | B4 |
| 7 | 信号是否生成于未定版末根 K 线？ | B4(3) |
| 8 | 延迟缓冲参数是否为 04 实测值（而非假设 timestamp=可用时刻）？ | B0.4 |

---

## (c) regime 定义与转移规则（backtest 前锁定，禁止样本内拟合）

**regime 划分来源**：02 stability-criteria.md「对阶段03的建议输入」暂定结论 #1 —— 对 2020–2025（6 年）样本，明确列出 regime 周期：**2020-21 牛 / 2022 熊 / 2023 震荡 / 2024-25 牛**。该划分在 02 阶段已锚定，非本节点新造。

**预注册 regime 标签（锁定值，日历边界，04 前不得修改）**：

| regime | 区间（UTC 日历） | 依据（02 候选集） |
|---|---|---|
| **bull** | 2020-01-01 → 2021-12-31 | 02 #1 "2020-21 牛" |
| **bear** | 2022-01-01 → 2022-12-31 | 02 #1 "2022 熊"（**必须落入 OOS 段**，方向一致性判据 C4 天然要求） |
| **range** | 2023-01-01 → 2023-12-31 | 02 #1 "2023 震荡" |
| **bull** | 2024-01-01 → 2025-12-31 | 02 #1 "2024-25 牛" |

**regime 转移规则**：
- `regime_label(t_ms)` = 覆盖 t_ms 的唯一日历区间的标签（边界硬切换，无过渡带）。
- **禁止自适应再估计**：regime 边界是预注册日历常数，**不得**用回测样本内的价格/波动率数据重新估计 regime 边界或标签（= 样本内拟合，被禁止）。
- **稳健性对照（预注册，非默认）**：04 可跑一个定量对照定义（如 90 日滚动价格收益符号 + 幅度阈值）作 regime 稳健性检验，但其阈值必须在 04 启动前写死、用先验圆整值，且该对照结果不进入主结论、仅报告敏感性。若对照 regime 下结论翻转，如实报告。
- **T01 验证结果如何进入**：T01 核验 arXiv:2608.27734（exists，0.95）→ 确认验证栈分层：第一层结构性 point-in-time（§(b)）→ 第二层 DSR/PBO/PSR 按 trial count deflate（§(d)）。regime 条件化本身不增加泄漏风险，但每个 regime 内的 OOS 窗口仍须独立做第二层统计校正。

**窗口候选（02 锁定，供 §(d) 矩阵用）**：02 #1 主流为 **3–5 个互不重叠的年度 OOS 窗口 + expanding window**（Mesfin 3 测试年 / Wysocki 4 窗口+1 OOT / GT-Score 15 年 9 splits）。本 spec 取 **5 个年度 OOS 窗口**（2021/2022/2023/2024/2025，2020 作首窗扩展训练段），2022 熊市强制入 OOS。月级窗口 02 已判"零出现且加重 deflation"→ 不采用。

**锁定声明**：以上 regime 区间、窗口数、对照规则在 04 回测启动前全部锁定。**regime_locked = true。**

---

## (d) 多重检验修正计划

**测试矩阵规模（预注册，04 前锁定）**：

| 维度 | 取值 | 数 | 来源 |
|---|---|---|---|
| regime | bull / bear / range | 3 | §(c) |
| funding 阈值 | 3 个先验候选（符号阈值 / 低分位 / 高分位，具体值 04 前写死为先验圆整值，**不得**从样本内挑选） | 3 | 02 C5 "阈值最终值属阶段03设计决策" |
| OOS 窗口 | 5 个年度窗口（§(c) 窗口候选） | 5 | 02 #1 |

**总测试数 = 3 × 3 × 5 = 45 个 OOS 检验**（每检验 = 某 regime 某阈值某窗口上"funding 信号 OOS 净收益显著为正"的假设检验）。

**修正方法选择：BH-FDR（Benjamini-Hochberg）为主 + DSR trial-count deflation 为第二层，弃 Bonferroni。**

**理由**：
1. **Bonferroni 过度保守会系统性误杀**：45 个检验 Bonferroni α = 0.05/45 ≈ 0.0011，在加密择时的噪声水平下几乎不可能通过 → 对应 arXiv:2610.07701（02 C7 已引）的警告："admission gates 把采用率压到 1–7%"，"criteria computed on absolute rather than excess returns silently reject every candidate, including true signals"。Bonferroni 在正相关的 45 个同源检验（同一 funding 信号的不同阈值/窗口，高度共享信息）下损失过多真阳性。
2. **BH-FDR 适配正相关家族**：本 45 检验高度正相关（同一底层信号，相邻阈值/相邻窗口信息重叠），BH 在正相关（PRDS）下仍控制 FDR，且不假设独立，比 Bonferroni 的"全独立"假设更贴合实际。
3. **与 02 验证栈分层一致**（02 #3，T01 已强化）：第一层结构性 PIT（§(b)）防泄漏 → **第二层 = 本节的 FDR + DSR deflation** 防多重检验/过拟合。DSR/PBO 的 trial-count deflation（arXiv:2608.27734，T01 核验 exists）作为**叠加的第二层防线**：所有报告绩效按试验次数（= 45 个 OOS 检验的 trial count + 04 中任何额外的阈值/窗口搜索次数，全记录）deflate。
4. **预注册 vs 暴力搜索**（T01 核验的 arXiv:2608.27734 核心论点）："pre-registered hypotheses earn lower evidential bars than brute search"——本 spec 的 45 检验全部预注册（阈值/窗口/regime 先验锁定），故用 FDR 而非更严的 CSCV；**但 04 中任何事后新增的阈值/窗口都计入 trial count 并触发 DSR 加严**，禁止"跑一个不过就换一个"。

**通过判据（02 C5 最严格显式集合，预注册）**：每 OOS 窗口 OOS 净收益 T ≥ 2.0 + 每窗口 ≥ 30 笔 + 扣费后净正 + **全部测试年方向一致**（C4）+ permutation p < 0.001（where applicable）。PSR > 0.95 作"正 Sharpe 概率"门槛参考（02 C5，arXiv:2608.24786）。阈值基于**超额收益**（非绝对收益，避免 02 C7 的误杀）。

**锁定声明**：45 检验家族结构、BH-FDR α=0.05、DSR 叠加、trial-count 全记录规则，04 前锁定，04 不得事后扩大家族或下调 α。

---

## (e) 贡献定位（严格引用 T03 口径 + T01 核验引用）

**贡献声明（限定口径）**：
本项目的贡献**不是**"发现 funding rate 有效"（funding rate 作为拥挤度/情绪指标是从业者常识，不构成新发现）。贡献是：

1. **严格条件下的形式化验证**：把"funding rate 作为主择时/市场状态信号"放进**结构性 point-in-time（§(b) 伪代码级）+ 预注册 regime 条件化（§(c)）+ 预注册多重检验修正（§(d)）**的完整验证栈里，给出可复现的、防泄漏防过拟合的 OOS 证据。
2. **regime 条件化**：bull/bear/range 下 funding 信号是否稳定（方向一致性 C4），这是 02 候选集指向、T03 缺口声明支持的空白。

**新颖性声明（严格口径，必须随论文披露）**：
> "公开检索未找到以加密货币永续合约 funding rate 为主择时/市场状态信号并给出回测的已发表工作" —— 此声明的置信度为 **gap_confidence = 0.75（T03 §4 原文口径）**，其**度量的是该缺口陈述成立的置信度（而非"本次检索确实没找到"——后者 ≈0.9+）**，且**限定为 arXiv 公开预印本范围内**。
>
> **必须披露的局限（T03 §3 直接引用）**：检索仅覆盖 arXiv 公开预印本；**SSRN 不可达（curl 000）、Google Scholar 无公开 API、付费金融期刊（JFE/JBF/JFM 等）付费墙不可搜** → 一篇以 funding rate 为主择时信号的回测完全可能只发表于付费金融期刊而非 arXiv，缺口可能被推翻。论文中必须把新颖性限定为"公开可检索预印本范围内"并披露此局限。

**最接近邻接工作（T03 + T01，均非 funding 主择时回测）**：
- **arXiv:2608.25348**（T03 Q3 命中）*Point-in-Time Audit Before Alpha: … Negative Matched-Budget Study on BTC Perpetual Futures* —— **数据设定最接近本项目**（Binance BTCUSDT USD-M 永续，含 trade/mark/index/funding/OI 流，PIT 审计），但它是**数据可用性审计 + 自适应 agent 负结果研究**（"all evaluated runs had positive IC but negative net Sharpe"），**不是以 funding rate 为主择时信号的策略回测** → 是 PIT 审计方法学的最近邻，非信号贡献的竞品。
- **arXiv:2608.27734**（T01 直验，verdict=exists，confidence=0.95，Gençay，q-fin.ST，2026-08-27）*What survives honest evaluation? Leakage-safe, search-aware assessment of LLM-driven trading strategy discovery* —— **验证方法学的承重引用源**（leakage-safe 结构性 PIT + trial-count deflation），本 spec §(b)/(d) 的方法论依据，**不是** funding 择时策略本身。

**定位一句话**：本项目 = "在已验证的 leakage-safe 验证栈（2608.27734）+ PIT 审计实践（2608.25348）之上，首次以 funding rate 为主信号做预注册、regime 条件化的严格 OOS 验证"，新颖性限定于 arXiv 公开预印本范围（gap_confidence 0.75，披露 SSRN/付费库未覆盖）。

---

## (f) 局限性（继承 T03 §3 + T02 可达性）

**继承 T03 §3 局限（原文 5 条）**：
1. **仅覆盖 arXiv 公开预印本**。本沙箱 web_search 无 API key、SSRN 不可达（curl 000）、Google Scholar 无 API、付费金融期刊（JFE / Journal of Banking & Finance / Journal of Futures Markets 等）不可搜。**一篇以 funding rate 为主择时信号的回测完全可能只发表于付费金融期刊而非 arXiv。**
2. **arXiv 术语歧义**："funding rate" 在宏观金融中 = Federal Funds Rate（2506.22763、2604.08825、2604.01431 均为 Fed 利率），在加密中 = 永续 funding rate。同名词污染使纯文本检索难以精确区分；加密 funding 择时论文可能用 "perp carry" / "funding carry" / "basis signal" 等未覆盖术语。
3. **检索词有限（6 组）**：穷举所有可能措辞不可能；存在未覆盖的同义/邻接表述。
4. **arXiv 限流**：export API 间歇 429、HTML 连续请求偶发 "Rate exceeded."，需 15–25s 间隔；未做分页深翻页（max_results=10 / 首页），极冷门深排结果可能漏检。
5. **未检索非 arXiv 学术平台**：SSRN（金融论文主阵地）、RePEc、NBER、工作论文系列均不可达。

**T02 继承局限（Bybit API 可达性未实证 — 0.70 压因）**：
6. **Bybit API 在 04 执行环境的可达性未实证**（T02 §5 压低 confidence 的最大残余风险）：02 全程沙箱网络阻断，**无一次真实 API 响应** → OI 数据（默认路径 B）的整条 live API 取数链（分页深度是否真到 symbol 上线日 + 速率限制是否可承受）在 04 前未验证。**→ 04 前必须先做 curl 预检**（Bybit OI API 可达性 + 分页深度 + 一次真实响应时间），不可达则按 §(a) 规则降级 A（仅 funding）并记录降级事件。
7. **OI bar 时间戳语义 = 领域知识未核验**（T02 §5）："bar 时间戳 = bar 起点"是 02 未核验的领域知识，04 须实测响应时间补证（支撑 §(b) B3 延迟缓冲参数）。
8. **data.binance.vision 归档 mutable（修订风险 MEDIUM）**（T02 §4.5）：bulk 文件下载到的是截至下载时点的文件，非当时点原始文件；futures funding/OI 是否在 updates 修订清单未确认 → 对 2020-01 起窗口影响大概率可忽略（未 100% 排除），记录为 MEDIUM 残余风险，04 须核对。
9. **单交易所幸存者偏差**（T04 objective (f)）：S1 以 Binance 为主 venue（funding 206 bulk 文件）+ Bybit 为 OI 主深度源，**单交易所/双交易所数据边界** → 结论的跨所泛化性未验证；funding rate 的跨所分布差异（不同所 funding 水平/波动不同）未建模，列为局限。
10. **OI 真实增量价值 04 前未知**（T02 §5）：本 spec 不假设 OI 高价值，仅"免费试错"，04 回测为核心输出（决定触发 C 与否，§(a) C 规则）。

---

## 合成置信度

**confidence = 0.72**（03 阶段 join 合成置信度）
- 支撑：T01 承重引用核验成立（0.95，强化 02.5 的 0.85）；T02 PIT 规则完整导出且免费可逆结构对齐用户画像；T03 双通道负检索一致无反例；§(b) PIT 规则达伪代码级、可执行可审计。
- 压低：T02 Bybit API 可达性未实证（0.70 压因，04 前须 curl 预检）；T03 付费库/SSRN 未覆盖（0.75 口径，新颖性需限定披露）；OI 增量价值 04 前未知。
- 合成取保守值：三输入 0.95/0.70/0.75 中，结构完整性不受 0.95 限制、受 0.70（可达性）与 0.75（新颖性口径）共同限制 → 0.72。

## 输出 schema 自检

- **confidence**: 0.72 ✓
- **pit_rule**: 见 §(b) `latest_settled_funding` / `latest_oi` / `data_available` 伪代码 —— "t 时刻仅用 settled 且 ts_norm ≤ t − 发布lag 的 funding；OI 用 bar_start+duration+delay_buffer ≤ t 的已确认 bar；Coinglass ×1000 归一；禁用未定版末根" ✓
- **regime_locked**: true（§(c) 日历锁定，04 前不得修改）✓
- **sections**: 6 节齐全 (a) 信号清单 / (b) PIT 时间戳严格规则（伪代码级）/ (c) regime 定义与转移规则 / (d) 多重检验修正计划 / (e) 贡献定位 / (f) 局限性 ✓

*生成: T04 synthesis-worker | 合成自 T01/T02/T03 三 artifacts + 02 stability-criteria.md | 主机日期 2026-10-17*

---

## §Lead 批注（2026-10-17 15:58，T04 完成后补录）

1. **(a)/(f) OI 有效默认更新**：Lead 于 15:42 完成 Bybit/Binance API 可达性预检（`t02b-api-reachability-precheck.md`）：本环境 live 交易所 API 全部不可达（TLS reset/timeout），仅 data.binance.vision 归档 CDN 可达。按 §(a) 降级规则，**04 在本环境直接从 A（funding-only）起步并记录降级事件**；B 为条件路径（需无阻断网络/代理时启用）；C 三触发条件不变。§(f) 第6条的"04 前 curl 预检"要求已由 t02b 满足（结果：不可达）。
2. **(e) T01 验证层级更新**：Lead 内联 PDF 正文级补验（t01 artifact §Lead 内联补验节）：C10 原话 + 453-stock universe + trial-count deflation 全部 PDF 正文确认 → T01 验证层级 = **PDF 正文级**；残余仅剩 provenance（arXiv 单库两镜像，无第三方独立索引），记入 T08 gap 列表。

# origin: ai (Lead 批注, 2026-10-17)

## §Lead 内联核验（arXiv:2610.07701，2026-10-17 16:24）

§(d) 引用的 arXiv:2610.07701 此前全项目未核验。Lead 直验（export.arxiv.org API）：
- 文献存在：*On the Boundary of Admission Gates: An Injected-Truth Study of Falsification-First Selection in Quantitative Strategy Research*（arXiv:2610.07701v1）
- 摘要级核验：§(d) 两处引文与摘要逐字吻合——(1) "cut adoption to 1--7%"（对应本文"admission gates 把采用率压到 1–7%"）(2) "criteria computed on absolute rather than excess returns silently reject every candidate, including true signals"（对应本文"criteria computed on absolute rather than excess returns silently reject every candidate, including true signals"）
- 验证层级：摘要级（与 T01 初判同层级；PDF 正文级未做，04 前可选补）
- 结论：§(d) BH-FDR 论证的文献支撑成立，无幻觉引用。
（# origin: ai — Lead 内联核验）
