# origin: ai

# T02 — OI（持仓量）数据源三选项终决

**任务**: 03阶段 T02 节点 — 对 OI 数据源做 A/B/C 三选项终决
**事实依据**:
- `loop-artifacts/stages/02/r1/research/funding-rate-oi-timing.md`（funding/OI 发布时点与更新频率）
- `loop-artifacts/stages/02/r1/research/data-revision-latency.md`（数据修订与迟报机制）
- Lead 直探实证: openInterest 归档 **404（真不存在）**；fundingRate 月度 **2020-01 → 2026-09 实存 206 文件**
**评估维度**: 信号贡献（regime识别/择时）、PIT风险、成本（用户默认画像：免费/白嫖优先，仅边际收益明确且成本极低≤几美元/月才付费）、可复现性

---

## 1. 三选项对比表

| 维度 | A 放弃OI（仅funding） | B 免费OI（Binance 30d + Bybit至上线日） | C Coinglass 付费 $29/mo |
|---|---|---|---|
| **信号贡献** | 失去OI这一独立regime指标（OI=总持仓/杠杆累积-去化，与funding的"拥挤度"正交互补）；funding单信号可识别部分regime但盲区较大 | funding+OI双信号，regime识别/择时信息最完整（OI增/降配合价格方向→新增多/空、去杠杆判定） | 跨所聚合OI（含OI Weight/Vol Weight/Long-Short Ratio/Liquidation），信号维度最丰富 |
| **PIT风险** | 最低——无OI bar时间戳语义/延迟缓冲问题；仅funding settled规则（Bybit官方原文确认） | 中——OI bar时间戳=bar起点（领域知识未核验）；需`bar_start+duration(+延迟缓冲)≤t`规则；Bybit官方承认极端行情延迟警示；data.binance.vision归档mutable（修订风险MEDIUM） | 中高——单位=秒需×1000归一（02§3单位陷阱）；修订行为公开无记录（未解决）；单请求≤90天需分页拼接；跨所聚合口径/延迟变更无公开说明 |
| **成本** | 0 | 0（Bybit免费至上线日 + Binance免费30d交叉验证） | $29/mo（**超出"≤几美元/月"默认画像阈值**，须条件触发才破例） |
| **可复现性** | 最高——fundingRate月度206个bulk文件实存（2020-01→2026-09），bulk下载可复现 | 中——Bybit OI须live API取数（openInterest归档404→无bulk路径）；依赖04环境Bybit API可达+分页深度+速率限制；Binance 30d仅近期交叉验证 | 低——依赖付费订阅持续有效+条款可能变更；修订不可审计（公开无记录）；需API key |
| **对齐用户默认画像** | 对齐（免费/简单可靠） | **最对齐**（免费+增加信号价值+零成本可逆） | 不对齐（$29>几美元，须边际收益明确才破例） |

---

## 2. 推荐选项 + 理由

### 推荐：**B（免费OI：Bybit至上线日为主深度源 + Binance 30d为近期交叉验证）**

作为 04 回测的**默认OI路径**。A 为降级后备，C 为条件触发分支（见§3）。

**理由**：
1. **信号价值非冗余**：OI（总持仓/杠杆累积-去化）与 funding（拥挤度/情绪）是正交信息。研究问题明确含"funding rate/OI 等时间戳信号"，OI 在范围内。A（永久放弃且未经测试）= 过早放弃潜在信号，违背 P1（实际问题优先、能产生可验证结果优先）。
2. **零成本 + 可逆**：B 不花钱，仅工程成本。若 04 证明 OI 无增量价值，直接剔除（无沉没成本）。这是"免费试错"的最优结构——用 0 代价换取一次真实的信号价值检验机会。
3. **满足≥5年硬约束**：Bybit 免费 OI 历史至 symbol 上线日（**官方原文** "The upper limit time you can query is the launch time of the symbol"，BTCUSDT 永续 2019-09 上线→覆盖 5 年+）。这是 02 研究唯一经文档书面确认的免费 5 年 OI 源。Binance 仅 30 天（SDK 原文 "Only the data of the latest 30 days is available"）直接出局作主源，仅作近期交叉验证。
4. **PIT 风险可控且已文档化**：OI 的 PIT 规则（`bar_start+duration+延迟缓冲≤t`）、Bybit 延迟警示、单位归一（Bybit/Binance 均 ms，**无单位陷阱**——陷阱仅 Coinglass）在 02 研究中均已明确导出，回测框架可参数化"可用时刻=标称时间+延迟缓冲"。
5. **C 不默认的理由**：$29/mo 超出用户默认画像"≤几美元/月"阈值；Coinglass 修订行为公开无记录（PIT 可审计性弱）；依赖付费订阅（可复现性差）。02 研究已将其"降级为备选，不作为 S1 默认数据源"。故 C 只能是条件触发项，不能默认。
6. **A 不默认的理由**：A 牺牲了零成本可获得的潜在信号价值。仅在 Bybit API 于 04 执行环境不可达（reproducibility break）时作为降级路径启用（见§4 第6条），并记录降级事件。

**分支逻辑**：
- 默认 → **B**
- Bybit API 04 环境不可达 → 降级 **A**（仅 funding），记录降级事件
- 04 回测证明 OI 增量价值>阈值 **且** 免费 OI 源是约束瓶颈 → 触发 **C**（付费补齐数据质量/覆盖）

---

## 3. 触发条件（Coinglass 付费启用 — 条件分支）

C 作为**条件分支触发项**，**仅当 04 回测满足以下全部条件**时才付费启用（$29/mo）。任一不满足则保持免费路径（B 或降级 A）。

**触发阈值（预注册，非事后拟合）**：

| 门槛 | 判据 | 建议值 |
|---|---|---|
| **① 价值门槛**（OI 是否值得付费） | walk-forward OOS 上，funding-rate-only 基准 OOS Sharpe = S_base；加入 OI 后 = S_oi。要求 ΔS = S_oi − S_base 的**绝对值** ≥ 阈值，且 ΔS 的 95% bootstrap CI（≥3 个 walk-forward 折）下界 > 0 | **ΔS ≥ +0.20** |
| **② 免费源瓶颈门槛**（免费 OI 是否是约束） | 免费 OI（Bybit 至上线日 + Binance 30d 交叉验证）的有效覆盖率 < 阈值，或免费 OI 的 PIT 延迟缓冲导致信号可用率显著退化 | **有效 OI bar 覆盖率 < 95%**，或 Bybit 延迟警示触发率 > **5%** 的回测 bar |
| **③ 成本门槛**（维持"成本极低"约束） | Coinglass 实际月费 ≤ 上限（核验条款未涨价） | **≤ $30/mo**（$29 满足；若涨价 > $50 不启用） |

**逻辑**：
- 仅 ① 成立（OI 有价值）但免费 OI 已足够（② 不成立）→ **保持免费 B，不付费**（价值已被免费源捕获，无理由花钱）。
- ① + ② 同时成立（OI 有价值 且 免费源是瓶颈）→ **触发 C**，付费补齐数据质量/覆盖。
- ① 不成立（OI 无增量价值）→ **不付费**，保持 B 或降级 A。
- ③ 不成立（涨价超上限）→ **不付费**。

**为何阈值取 +0.20（Sharpe 绝对增量）**：在成本调整、PIT 合规、滚动走步 OOS 的加密择时研究中，单 regime 周期内的 OOS Sharpe 增量噪声较大；< +0.15 的增量通常不跨折稳健。+0.20 且 CI 下界 > 0 是"边际收益明确"的保守预注册门槛，与用户"边际收益明确才付费"的要求对齐。该值在 04 前锁定，04 不得事后下调以通过门槛。

**为何用 OOS Sharpe 增量为主判据**：Sharpe 同时纳入收益/波动/风险，walk-forward OOS 已控过拟合，辅以 CI 下界 > 0 防单折偶然。**退化判据**：若 04 环境样本不足以稳定估计 Sharpe，则改用 OOI 特征的 walk-forward OOS **IC ≥ +0.05 且符号跨折稳定（≥3 折同号）** 作为价值门槛 ① 的替代。

---

## 4. PIT 风险落地（数据管道硬性要求）

从 02 研究直接导出，04 执行须内置：

1. **时间戳归一 = UTC 毫秒**：Bybit = Binance = ms（原生）；Coinglass = 秒 → **×1000**。必做管道步骤（02§3 单位陷阱）。
2. **funding PIT 规则**：t 时刻仅用 `fundingRateTimestamp ≤ t` 的**已结算**记录（Bybit 官方原文确认语义）。settled 与 predicted（基于 mark price 实时推算的当期值）**分字段**，不可混用。
3. **OI bar PIT 规则**：t 时刻可用集 = {bar : `bar_start + bar_duration (+ 延迟缓冲) ≤ t`}。bar 时间戳 = bar 起点（领域知识，02 未核验，建议 04 实测响应时间补证）。保守策略 = "只用到上一根已确认 bar"。**延迟缓冲参数化**（"可用时刻 = 标称时间 + 延迟缓冲"），不得假设 timestamp = 可用时刻。
4. **Bybit 极端行情延迟警示**（官方原文）：回测框架须内置延迟缓冲参数，极端行情段用更保守缓冲。
5. **data.binance.vision 归档 mutable（修订风险 MEDIUM）**：fundingRate 月度文件（2020-01→2026-09，206 个实存）下载到的 = 截至下载时点的文件，非当时点原始文件。缓释：修订罕见/离散/CHECKSUM 清单可审计，已记录修订集中 2022 年且主针对 spot；futures funding/OI 修订未确认。对 2020-01 起窗口，2022 spot 修订对 futures funding/OI 样本影响大概率可忽略（未 100% 排除）→ 记录为 **MEDIUM 残余风险**，04 须核对 futures 是否在 updates 清单。
6. **openInterest 归档 404（无 bulk 路径）**：Lead 直探证实 data.binance.vision 无 OI bulk 文件 → OI **只能 live API 取数**（Bybit 至上线日）。**可复现性依赖**：04 执行环境须 Bybit API 可达 + 分页深度充足 + 速率限制可承受。若 04 环境 Bybit API 不可达 → **降级 A**（仅 funding，funding 有 206 个 bulk 月度文件可复现），并记录降级事件。
7. **T+1 迟报**：data.binance.vision 日线文件次日发布、月线文件当月第一周一发布 → bulk 文件的可用时刻须按 T+1 对齐时间戳（"the next day" 的确切 UTC 时刻未明确，04 补证）。
8. **实时未定版末根 K 线**：从 API 拉取的"最近 klines"末根是进行中（未定版）K 线，收盘才冻结 → 回测信号生成**禁用未定版末根**。

---

## 5. Confidence

**confidence = 0.70**

- **支撑（为何 ≥ 0.7）**：决策"免费 OI 默认 + 免费可逆 + C 条件触发"是低成本、可逆、对齐用户默认画像（免费优先）的结构；事实基础扎实（Bybit OI 至上线日 = 官方原文；Binance 30 天 = SDK 原文；fundingRate 206 个 bulk 文件实存；openInterest 404 实探）；PIT 规则已从 02 研究完整导出。
- **压低（为何 < 0.85）**：① OI 真实增量价值 04 前未知（本决策不假设其高，仅"免费试错"）；② Bybit API 在 04 执行环境的可达性未实证（02 全程沙箱网络阻断，无一次真实 API 响应）→ 可复现性依赖是最大残余风险；③ Coinglass 定价档位未解决（但仅影响条件分支 C，不阻塞默认路径）；④ OI bar 时间戳语义 = 领域知识未核验（建议 04 实测补证）。

---

## 6. 未解决 / 04 阶段需补证

1. Bybit API 04 执行环境实测可达性 + 分页深度（是否真到上线日）+ 速率限制。
2. OI bar 响应时间实测（"标称时间戳 vs 实际可得时间"延迟分布 → 支撑延迟缓冲参数）。
3. data.binance.vision updates 清单是否覆盖 futures（fundingRate/OI）文件 → 决定修订风险可否从 MEDIUM 降 LOW。
4. Coinglass 定价/plan 门控核验（浏览器渲染 pricing 页）→ 条件分支 C 门槛 ③ 的实际值。
5. OI 信号的真实增量价值（04 回测核心输出，决定触发 C 与否）。
