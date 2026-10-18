# origin: ai

# T05 数据管线设计 (Data Pipeline Design)

- **节点**: 03-r1-node-T05 (orthogonal_key: data-pipeline)
- **阶段**: 1-loop 03 任务分解 → 数据管线设计
- **宿主**: 2026-10-17 (本机单一视点, 选择性网络阻断环境)
- **depends_on**: T04 (t04-signal-spec.md, 已完成)
- **input_refs**: t04-signal-spec.md / data-history-depth.md / data-revision-latency.md / t02b-api-reachability-precheck.md
- **owner 声明**: 本节点是 DAG 中 **成本参数 (费率+滑点)** 的唯一 owner, 无其他节点负责。本节点同时承接 02.5 #2 延后项 (S2/S3 历史深度探针)。

---

## 0. 摘要 (速览)

1. **数据源**: S1=data.binance.vision (funding+klines, 本环境 **可达**)/ S2=Yahoo ^GSPC (本环境 **不可达 403**, 锚点改走新浪 hq.sinajs.cn 本环境可达)/ S3=腾讯 ifzq sh000300 (本环境 **可达**, 需 qfq, 单次 cap≈2000 bars)。
2. **OI 默认路径 = A (funding-only)**: t02b 已实证本环境 Bybit/Binance live API 全不可达 (rc=35 TLS reset / rc=28 timeout)。按 T04 §(a) 降级规则, 本环境 04 从 A 起步并记录降级事件。OI 源设计为 **可选插件, 默认关闭** (OI_ENABLED=false)。
3. **S2 锚点统一 = 3669.91** (02.5 交叉验证判定 = 新浪正确); Yahoo 原始值 3577.0 标注 "判定有差异, 未采用"。
4. **成本参数 = uncertain + 最后已知值 + 日期**: 费率页 (www.binance.com/en/fee/trade) 本环境不可达 (curl rc=28 timeout; web_fetch non-public IP)。记录最后已知公开值 (spot taker 0.1000% / futures taker 0.0500%), 获取日期 2026-10-17, **未一手核验**。
5. **修订风险 = MEDIUM (不写"低风险")**: "updates/ 清单全 spot" (实测 2026-10-17 = 2 文件, 均 spot) **≠** 已证明 futures 归档无修订。设计 SHA256 缓存 + 重拉应急 (SHA 变化 → flag + 记录 + 标记受影响回测需重跑)。
6. **PIT**: T04 §(b) B1-B6 逐条映射到管线实现字段 (§7)。
7. **可复现性**: 缓存布局 + SHA256 manifest + 04 复现步骤 (§8)。

---

## 1. 数据源矩阵 (S1 / S2 / S3)

> 单位纪律 (贯穿全部源): **统一归一到 UTC 毫秒 (int64)**。每源下表给出原生单位与归一规则; 任何量级陷阱在 §7.1 B1 单独列出。

### 1.1 S1 = data.binance.vision (主源, 加密永续)

| 维度 | 值 |
|------|-----|
| **endpoint (funding)** | `https://data.binance.vision/data/futures/um/monthly/fundingRate/{SYM}/{SYM}-fundingRate-{YYYY-MM}.zip` |
| **endpoint (klines)** | `https://data.binance.vision/data/futures/um/daily/klines/{SYM}/{INT}/{SYM}-{INT}-{YYYY-MM-DD}.zip` |
| **覆盖期 (funding)** | 2020-01 → 2026-09, 实存 206 个月度文件 (Lead 直探 + 本节点复验: 2020-01 存在 206 / 2019-12 缺失 404)。funding 仅月度 bulk, 无 daily。 |
| **覆盖期 (klines)** | 2020-01-01 → (逐日 zip; 本节点复验 2020-01-01 存在 206 / 2019-12-01 缺失 404) |
| **单位** | **futures 原生 UTC 毫秒 (ms)**。**⚠️ 量级陷阱**: README (binance-public-data, 2026-10-17 抓取) 明文 "The timestamp for **SPOT** Data from January 1st 2025 onwards will be in **microseconds**"。**futures 未被 README 明示改 µs** → 04 须逐文件核验 `fundingRateTimestamp`/kline openTime 量级 (13 位=ms / 16 位=µs), 不可假设。 |
| **修订风险** | **MEDIUM** (见 §6)。归档 mutable (README CHECKSUM 节 "Archived files may be updated at a later date")。updates/ 清单实测 (2026-10-17) = **2 文件, 均 spot** (kline_updates + aggregate_trade_updates), **无 futures fundingRate/OI 条目**。"全 spot" 不证明 futures 未修订。 |
| **本环境可达** | **可达 (REACHABLE)**。t02b: HTTP 200。本节点复验: 根 200; 具体文件 206 (存在) / 404 (缺失); 站点不暴露 S3 目录列举 (只认具体文件 URL), updates/ 候选目录均 404。 |

### 1.2 S2 = Yahoo ^GSPC (美股锚点)

| 维度 | 值 |
|------|-----|
| **endpoint** | `https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=full&interval=1d` |
| **覆盖期** | **last-known** 回溯至 1950 (Yahoo 回填, ^GSPC 实际 1957-03-04 起算)。**本环境不可复核** (403, 见下); 起点值标 "last-known, not first-verified in this env"。 |
| **单位** | epoch **毫秒 (UTC)** (Yahoo chart API 标准); 锚点值本身为指数收盘价 (本地美东交易日)。 |
| **修订风险** | Yahoo 指数为历史回填序列, 存在静默重算可能; 但本节点锚点 **不依赖 Yahoo 原始值** — 见 §3, 锚点统一取 02.5 交叉验证判定值 (新浪 3669.91), Yahoo 仅作旁证。 |
| **本环境可达** | **不可达 (UNREACHABLE)**。query1 + query2 两 host 均 **HTTP 403** (size 3369, 返回 `<title>Yahoo</title>` 的 JS/consent HTML 壳, 非 JSON)。2 次尝试均 403。→ S2 锚点改走 **新浪 hq.sinajs.cn** (本环境 **可达**, HTTP 200, 需 Referer: `https://finance.sina.com.cn`, 返 GBK; `gb_ixic` 2026-10-17 返回 "纳斯达克,26140.0340,..."; `gb_$inx` 代码无效返空串)。 |

### 1.3 S3 = 腾讯 ifzq (A股, 沪深300 sh000300)

| 维度 | 值 |
|------|-----|
| **endpoint** | `https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh000300,day,,,N,qfq` |
| **覆盖期 (API-observable)** | **2018-07-17 → 2026-10-16** (count=2000 为最大可用, 2000 bars)。count=4000/8000 → param error (单次 **cap ≈ 2000 bars**)。完整指数历史 2005-04-08 起 (last-known, 来自 data-revision-latency.md, **非单次 API 可观测**)。 |
| **单位** | **day bar, date 字符串 "YYYY-MM-DD" (本地 CST, 非 ms)**, 日线指数。归一到 UTC ms 时按当日收盘时刻 (09:30 收盘, 即 01:30 UTC 前一交易日 / 或按交易日 00:00 标记, 04 统一), **S3 是日线, 天然不进入 8h funding 高频 PIT 路径**。 |
| **修订风险** | **MEDIUM**: ① 000300 "拟生效样本" 幸存者/前视 (data-revision-latency.md) — 须用 **生效日当时成分** (历史成分, 非当前成分), 否则前视; ② 腾讯 ifzq 为 **qfq (前复权)** 序列, 分红/样本调整会改历史 bar, 锚点值与原始值可能不一致。 |
| **本环境可达** | **可达 (REACHABLE)**。HTTP 200。**约束**: 指数 (sh000300) **必须带 `qfq`** 才返数据 (无 qfq → 空 data / param error); count 须 ≤ ~2000。 |

### 1.4 矩阵汇总

| 源 | venue | dataset | range | format | unit_rule | 本环境可达 |
|----|-------|---------|-------|--------|-----------|-----------|
| S1-a | data.binance.vision | fundingRate | 2020-01→2026-09 (206 monthly) | monthly zip | futures 原生 UTC ms; 2025+ µs 陷阱逐文件核验 | ✅ |
| S1-b | data.binance.vision | klines 1h | 2020-01-01→ (daily) | daily zip | futures 原生 UTC ms; 未定版末根禁用 | ✅ |
| S2 | Yahoo (query1/2) | ^GSPC 1d | last-known 1950→ (403 不可复核) | JSON (本环境 403 返 JS 壳) | epoch ms UTC; **锚点改走新浪 (可达)** | ❌ (新浪 ✅) |
| S3 | 腾讯 ifzq | sh000300 1d (沪深300) | API-observable 2018-07-17→2026-10-16 (cap ~2000/call) | JSON day bars (需 qfq) | date string 本地 CST 日线指数 (非 ms) | ✅ |

---

## 2. OI 默认路径 = A (funding-only)

### 2.1 为什么本环境默认 A

- **t02b 实证** (t02b-api-reachability-precheck.md, 本机单一视点): `api.bybit.com /market/time` 3/3 全失败 **rc=35** (TLS 握手 reset by peer); `api.binance.com /ping` **rc=35** (TLS error); `fapi.binance.com /ping` **rc=28** (10s timeout); `data.binance.vision` **200 OK**。规律: **live API 域全不可达, 归档 CDN 可达**。
- **T04 §(a) 降级规则 A**: "A = 放弃 OI 仅 funding, 仅当 Bybit API 于 04 执行环境不可达 (reproducibility break) 时启用 + 记录降级事件"。t02b 已满足该触发条件 (Bybit live API 本环境不可达) → **本环境 04 从 A 起步, 并记录降级事件** (degradation_event: t02b rc=35/rc=28, 2026-10-17)。
- 事实约束: `openInterest` 归档 404 (data.binance.vision 无 OI bulk) → **OI 无 bulk 路径, 只能 live API** → 本环境 A 是唯一可复现的 OI 路径。
- T04 Lead 批注 (2026-10-17 15:58) 确认: 04 本环境默认走 A; B 转条件路径 (需无阻断网络/代理); C 三条件不变。

### 2.2 OI 源 = 可选插件 (默认关闭)

管线实现上 OI 模块为 **插件接口**, 通过配置切换:

```
OI_ENABLED  = false   # 默认 (A 路径): 信号仅用 funding
OI_SOURCE   = "none"  # ∈ {none, bybit, coinglass}; OI_ENABLED=false 时强制 none
OI_DELAY_BUFFER_MS = <04 实测>   # B3 延迟缓冲, 04 实测前为参数占位
```

- `signal_at(t_ms)` (T04 B5): `f = latest_settled_funding(FUNDING[S], t_ms)` 恒执行; `oi = latest_oi(OI[S], t_ms, delay_buffer)` **仅当 OI_ENABLED** 且 OI_SOURCE 对应实现存在。
- OI 关闭时, 回测 = funding-only (S_base); 开启 B/C 后 = S_oi。ΔS = S_oi − S_base 用于 C 条件①的价值门槛。
- **降级事件记录**: 若 04 执行时 live API 代码路径失败 (rc=35/28), 必须显式降级 A 并写 `degradation_event` log (时间 + rc + 影响), 不得静默。

### 2.3 B 路径 (Bybit 免费 OI) 启用路径与触发条件

- **定位**: T02 决策 B 原为 "Bybit 免费 OI 至上线日为主深度源 + Binance 30d 近期交叉验证"。本环境 (t02b) 下 **降级为条件路径**, 不默认启用。
- **启用路径**: 需 **无阻断网络 / 代理** (live API 可达环境)。04 前 curl 预检 (t02b 已做, 结果 = 本环境不可达 → 本环境 B **不启用**)。
- **触发条件 (全部满足才启用)**:
  1. Bybit `api.bybit.com` live 可达 (04 执行环境 curl 预检 rc=0);
  2. Bybit OI 历史深度可分页到 symbol 上线日 (满足 PIT, 非仅近期);
  3. 速率限制可承受全回测窗拉取 (不触发封禁);
  4. OI bar 时间戳语义 (bar 起点) 经 04 实测确认 (T04 §(f) 局限: 该语义为领域知识未核验)。
- **04 行为**: 本环境 B 不启用 → OI 保持 none (A); B 代码路径存在但失败时显式降级 A + 记录。

### 2.4 C 路径 (Coinglass 付费) 启用路径与触发条件

- **定位**: T02 决策 C = Coinglass 付费源 ($29/mo, HOBBYIST)。触发逻辑 = **T04 §(a) C 三条件表** (预注册阈值, 04 前锁定, 不得事后下调):

| 条件 | 判据 | 退化路径 |
|------|------|----------|
| **① 价值门槛** | ΔS = S_oi − S_base ≥ **+0.20** 且 95% bootstrap CI (≥3 折) 下界 > 0 | 样本不足 → 改用 OOI 特征 walk-forward OOS **IC ≥ +0.05** 且 **符号跨折稳定 ≥3 折同号** |
| **② 免费源瓶颈** | 有效 OI bar 覆盖率 < **95%** **或** Bybit 延迟警示触发率 > **5%** 回测 bar | — |
| **③ 成本** | Coinglass 月费 ≤ **$30/mo** (涨 > **$50** 不启用) | — |

- **触发逻辑** (T04 §(a) 原文): **① + ② 同时成立 → C**; 仅 ① → 保持免费 B; ① 不成立 **或** ③ 不成立 → **不付费**。
- **本环境默认**: C 不启用 (默认 A; 且付费源本身需网络可达, 本环境 live API 不可达)。C 的启用决策 **推迟到 04 回测出 ΔS/覆盖率后** 按三条件判定, 阈值 04 前锁定。

---

## 3. S2 锚点取值规则 (P0 修正点)

### 3.1 2022-10-13 双值判定

- Yahoo ^GSPC 2022-10-13 **原始值 = 3577.0**; 新浪对应 **3669.91**; 两者差 **2.6%**。
- **02.5 交叉验证判定 = 新浪 3669.91 正确**。
- 本节点 (Yahoo 403 不可达) **无法本环境复核 3577.0**, 锚点依赖 02.5 记录; 新浪 hq.sinajs.cn 本环境可达 → 锚点源在本环境可复核。
- **标注**: `3577.0` = **"Yahoo 原始值, 判定有差异, 未采用"**。

### 3.2 三熊底锚点表 (统一采用 3669.91 系)

| 熊底日 | 采用锚点 (close) | 来源/判定 |
|--------|----------------|-----------|
| 2002-10-09 | **776.8** | 02.5 交叉验证判定值 |
| 2008-03-10 | **1273.4** | 02.5 交叉验证判定值 |
| 2022-10-13 | **3669.91** | 02.5 判定 = 新浪正确 (Yahoo 原始 3577.0 未采用) |

### 3.3 取值规则 (管线落地)

1. **锚点值一律取 02.5 交叉验证判定值** (本例 = 新浪系), 不以任一单源原始值为准。
2. **单源原始值仅作旁证并显式标注**: 凡与判定值不一致的原始值 (如 Yahoo 3577.0), 标注 "原始值, 判定有差异, 未采用", 不进入回测。
3. **多源冲突时** (Yahoo vs 新浪): 以 02.5 判定为准; 若 02.5 未覆盖该日, 标 "未交叉验证, uncertain" 并触发补充验证, 不默认取任一源。
4. **本环境约束**: Yahoo 403 → 锚点可复核源 = 新浪 (hq.sinajs.cn, 需 Referer); 04 若新浪亦不可达, 锚点标 "last-known (02.5 记录), 本环境不可复核"。
5. 锚点值在管线中以 **常量表** 形式硬编码 (三熊底固定日 + 判定值), 不运行时拉取 → 避免运行时时点漂移。

---

## 4. 成本参数 (本节点唯一 owner)

> 声明: DAG 无其他节点负责成本参数。本节为本节点独有产出。

### 4.1 费率页一手核验结果 (本环境不可达)

| 尝试 | 命令/通道 | 结果 |
|------|-----------|------|
| curl (spot) | `curl -s -A "$UA" -L "https://www.binance.com/en/fee/trade" --max-time 30` | **HTTP 000, rc=28 (TIMEOUT)** — 与 t02b Binance live 域阻断一致 |
| curl (futures) | `curl -s -A "$UA" -L "https://www.binance.com/en/fee/futuresFee" --max-time 30` | **TIMEOUT rc=28** |
| web_fetch | `https://www.binance.com/en/fee/trade` | **失败: "hostname resolves to a non-public IP address"** |
| web_search | Binance fee rates 查询 | **失败: 无 DEEPSEEK_API_KEY** |

→ **费率页本环境不可达 (4 通道全败)**。按任务规则: 记 **uncertain + 最后已知值 + 日期**。

### 4.2 spot / futures taker 费率 (uncertain + last-known + 日期)

> 以下值 = **最后已知公开值 (Binance 公开费率表), 获取日期 2026-10-17, 本环境费率页不可达故未一手核验 → 标 uncertain**。04 执行时若费率页可达, 须一手核验并刷新本表。

| 市场 | 等级 | maker | taker | 状态 |
|------|------|-------|-------|------|
| Spot | VIP0 | 0.1000% | **0.1000%** | uncertain (last-known 2026-10-17, 未一手核验) |
| USD-M Futures | VIP0 | 0.0200% | **0.0500%** | uncertain (last-known 2026-10-17, 未一手核验) |
| BNB 折扣 | — | 25% off (spot) | 25% off | uncertain (last-known, 本项目假设不持有 BNB → 不折) |

- **采用基准** (回测默认, 无 VIP/无 BNB): spot taker **0.1000%** / USD-M futures taker **0.0500%** / maker 0.0200%。
- **04 复现纪律**: 成本参数 = 预注册 (pre-04 锁定), 不得事后下调以"美化"净收益; 若 04 费率页可达且一手核验值 ≠ 本表, 记录差异并 **以一手核验值为准 + 标记受影响回测需重跑** (与 §6 修订应急同机制)。

### 4.3 滑点假设 (来源 + 获取日期)

> 滑点 **无公开权威值** (取决于市场微观结构), 故为 **预注册建模假设** (非事后拟合), 获取日期 2026-10-17。

| 参数 | 采用值 | 来源/说明 | 状态 |
|------|--------|-----------|------|
| 单边滑点 (base) | **0.01% / side** | 本节点预注册假设 (小账户, BTCUSDT 1h 典型价差 ~1 tick, 量级 1e-4~1e-3); 获取日期 2026-10-17 | pre-registered, 非拟合 |
| 单边滑点 (stress) | **0.02% / side** | 压力情形 (低流动性/快速市); 获取日期 2026-10-17 | pre-registered |
| 成交假设 | 市价单 (taker) | 回测默认 taker 成交 (含 taker 费 + 滑点); 获取日期 2026-10-17 | pre-registered |

- **04 校准**: 若 04 能拉取到 1s/1h 盘口或 tick 数据, 可用实际点差校准滑点; 否则保持预注册值。**校准须记录原值→新值 + 标记受影响回测重跑**。

---

## 5. S2 / S3 历史深度探针 (02.5 #2 延后项, 本节点承接)

> 记录实际值 + 探针命令原样。host 2026-10-17。

### 5.1 S2 ^GSPC 历史深度探针

**命令原样**:
```
curl -s -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36" -L \
  "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=full&interval=1d" --max-time 30
# 复现 host 2: 把 query1 换 query2.finance.yahoo.com
```
**实际结果**:
- query1: **HTTP 403** (size 3369, 返回 `<title>Yahoo</title>` 的 JS/consent HTML 壳, **非 JSON**)
- query2: **HTTP 403** (同 query1)
- **结论**: 本环境 ^GSPC **实际起点不可复核 (unreachable)**。起点值 = **last-known 1950** (Yahoo 回填惯例), 标 "not first-verified in this env"。S2 锚点改走 **新浪 hq.sinajs.cn** (本环境 200 可达, 见 §1.2/§3)。

### 5.2 S3 ifzq (sh000300 沪深300) 历史深度探针

**命令原样** (count 递增找单次 cap):
```
# 最大可用 count (单次 cap 探测)
curl -s -A "$UA" "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh000300,day,,,2000,qfq" --max-time 30
# cap 上界验证 (超限 → param error)
curl -s -A "$UA" "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh000300,day,,,4000,qfq" --max-time 30
curl -s -A "$UA" "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh000300,day,,,8000,qfq" --max-time 30
```
**实际结果**:
| count | 结果 | 最早 bar | 最新 bar |
|-------|------|----------|----------|
| 800 | 200, bars=800 | 2023-06-28 | 2026-10-16 |
| 1000 | 200, bars=1000 | 2022-08-26 | 2026-10-16 |
| **2000** | **200, bars=2000 (MAX WORKING)** | **2018-07-17** | **2026-10-16** |
| 4000 | **param error** (`{"code":0,"msg":"param error","data":[]}`) | — | — |
| 8000 | **param error** | — | — |

- **结论**: ifzq 单次 **cap ≈ 2000 bars**; **API-observable 最早 bar = 2018-07-17** (count=2000)。完整指数历史 2005-04-08 起为 last-known (data-revision-latency.md), **非单次可观测** — 04 若需 2018 前须分段拉取 (多次 count=2000 + 时间窗) 或换源。
- **约束**: 指数 **必须带 `qfq`**; 无 qfq → 空 data / param error。

---

## 6. 修订风险应急设计 (MEDIUM, 不写"低风险")

### 6.1 关键认识: "updates/ 全 spot" ≠ 已证明 futures 无修订

- data.binance.vision 归档 **mutable** (非严格 PIT)。来源 = binance-public-data README CHECKSUM 节: *"Archived files may be updated at a later date as a result of recently discovered issues"* + 完整 updates 清单。
- **本节点实测 (2026-10-17)**: README updates 清单 = **2 文件**, **均 spot**:
  | 日期 | 文件 | 说明 |
  |------|------|------|
  | 2022-08-08 | `updates/2022-08-08_kline_updates.zip` | "Fixed inconsistent data" |
  | 2022-04-21 | `updates/2022-04-21_aggregate_trade_updates.zip` | "Align to Spot aggregate trade data change" |
- **注意**: 任务 prompt 曾提 "3 文件全 spot", 但 README 实测 = **2 文件** (本节点据实记录 2, 差异如实标注)。
- **逻辑**: 两例均 spot (kline + aggregate_trade), **无任何 futures fundingRate/OI 条目** → 支持 "目前已知修订全 spot" 的弱结论, 但 **不证明 futures 归档将来/过去未被修订**。→ **修订风险 = MEDIUM**, 且必须配应急机制 (§6.2-6.3), **不得写 "低风险"**。

### 6.2 SHA256 缓存机制

- **下载即留痕**: 每下载一个 zip, **同时下载其同目录 `.CHECKSUM` 文件** (Binance 为每个 zip 提供 sibling `FILE.zip.CHECKSUM`, 内含 sha256)。
- **校验命令** (跨平台):
  ```
  # Linux
  sha256sum -c FILE.zip.CHECKSUM
  # MacOS (本机)
  shasum -a 256 -c FILE.zip.CHECKSUM
  ```
- **cache manifest** (JSON, 记录方式见 §8.2): 每文件一条 `{file_path, sha256, downloaded_at, source_url, checksum_file}`。

### 6.3 重拉应急流程 (SHA 变化 → flag + 记录 + 标记受影响回测)

```
04 执行时 (怀疑修订 / 定期复核 / 数据质疑):
1. 对目标文件重新下载 (fresh copy, 不覆盖原缓存)。
2. 重算 fresh copy 的 sha256。
3. 对比:
   - SHA 相同 → 归档未变, 用原缓存, 记录 "no-revision @ <date>"。
   - SHA 不同 → **REVISION EVENT**:
       a. flag: 写入 revision_event log (文件 / 旧SHA / 新SHA / 检测日期 / source_url)。
       b. 记录: 哪些文件的 SHA 变了 (清单)。
       c. 标记受影响回测: 凡使用该文件且落在修订时间窗内的回测 → 标 "needs_rerun"。
       d. 不静默覆盖: 原缓存保留 (可回溯), fresh 另存 + 标注。
4. 受影响回测重跑 (用 fresh 数据), 结果对比旧结果, 记录差异。
```
- **纪律**: 修订事件 **永不静默**; 任何 SHA 变化都触发 flag + 受影响回测标记; 重跑结果与旧结果差异超预注册阈值 → 触发结论复核。

---

## 7. PIT 落地映射 (T04 §(b) B1-B6 → 管线实现字段)

> 每条 T04 B 规则映射到管线具体实现字段/函数/参数。04 实现须逐条自检 (B6 清单)。

### 7.1 B1 `normalize_ts(ts, source) → int64` (UTC 毫秒归一)

| 源 | 原生单位 | 归一规则 | 管线字段 |
|----|----------|----------|----------|
| Binance futures (fundingRate/klines) | ms | `int(ts)` (原生直接用) | `ts_norm` |
| Bybit (OI, 条件路径) | ms | `int(ts)` | `ts_norm` |
| Coinglass (OI, 条件路径) | **秒** | `int(ts) * 1000` | `ts_norm` |
| **Binance SPOT 2025-01-01+** | **µs** (README 明文) | `int(ts) // 1000` (**反向陷阱!**) | `ts_norm` |
| **Binance FUTURES 2025+** | **README 未明示** (可能 µs) | **04 逐文件量级核验**: 13 位=ms 直用 / 16 位=µs ÷1000 | `ts_norm` |
| 腾讯 ifzq (S3, 日线) | date string (CST) | 按交易日 00:00 或收盘 UTC → ms (04 统一口径) | `ts_norm` (日线, 不进 8h 高频路径) |

- **⚠️ 量级陷阱表** (04 必须核验, 任一错 = 前视/时间轴错乱): Coinglass 秒→×1000 (漏乘 = 时间戳退到 1970); SPOT/FUTURES 2025+ µs→÷1000 (漏除 = 时间戳推到未来 → **前视**)。

### 7.2 B2 `latest_settled_funding(funding_records, t_ms)`

- **实现**: 过滤 `settled == True` (settled 与 predicted **分字段物理隔离**, predicted 永不进此函数) → `ts_norm <= t_ms` → 取 `ts_norm` 最大的一条 → 无则 `None`。
- **关键**: **不假设 8h 固定网格** (8h 间隔逐 symbol 可变); 取 "≤ t_ms 的最近一条 settled"。
- **管线字段**: `FUNDING[S] = list of {ts_norm, rate, settled(bool)}`; `settled` 为独立布尔字段 (Binance fundingRate bulk 含 settled 时间戳与 rate; predicted 值物理隔离到 `FUNDING_PRED[S]`, 本管线不使用)。

### 7.3 B3 `latest_oi(oi_bars, t_ms, delay_buffer_ms)`

- **实现**: 过滤 `bar_start + duration_ms + delay_buffer_ms <= t_ms` → 取最大 `bar_start` 一根 → 无则 `None`。
- **保守原则**: **只用到上一根已确认 bar** (当前未确认 bar 禁用, 见 B4 kline_unconfirmed)。
- **管线字段**: `OI[S] = list of {bar_start, duration_ms, oi_value}`; `bar_start` = bar 起点 (T04 §(f) 局限: 该语义为领域知识, 04 须实测确认)。
- **delay_buffer_ms**: 参数化, 04 实测 (live API 推送延迟); 本环境 OI 关闭 (A 路径) → 该字段占位, B/C 启用时 04 实测填充。

### 7.4 B4 `LAG_RULES` (发布 lag 参数化, 04 实测)

| 规则 | 判据 (可用时刻) | lag 参数 | 来源/04 动作 |
|------|----------------|----------|--------------|
| `funding_settled` | `ts_norm + LAG_SETTLE_PUB_MS <= t_ms` | `LAG_SETTLE_PUB_MS` | funding 结算后发布 lag; **04 实测** (结算时刻 vs 数据可获取时刻差) |
| `bulk_daily` | `ts_norm + 1_day + LAG_T1_MS <= t_ms` | `LAG_T1_MS` | bulk 日线 **T+1** (README: "new daily data becoming available the next day"); **04 实测 T+1 确切 UTC 边界** |
| `bulk_monthly` | `ts_norm + LAG_FIRST_MONDAY_MS <= t_ms` | `LAG_FIRST_MONDAY_MS` | bulk 月线 **当月第一周一** (README: "new monthly data at the first monday of the month"); **04 实测** |
| `kline_unconfirmed` | `b.confirmed == True` 才入集 | — | 实时末根未定版 (进行中, 收盘冻结) → **未定版末根禁用** (回测误用 = 前视) |

- **纪律**: 所有 lag **参数化** (非硬编码); 可用时刻 = 标称 ts + 发布 lag + 延迟缓冲; **不得假设 ts = 可用时刻** (T04 B0-4)。

### 7.5 B5 `signal_at(t_ms)` (信号组装)

```
def signal_at(t_ms):
    f = latest_settled_funding(FUNDING[S], t_ms)          # 恒执行 (A 路径主信号)
    oi = latest_oi(OI[S], t_ms, OI_DELAY_BUFFER_MS) if OI_ENABLED else None   # 条件
    regime = regime_label(t_ms)                            # T04 §(c) 预注册日历
    return {"funding": f, "oi": oi, "regime": regime}
```
- funding 恒为默认信号; oi 仅 OI_ENABLED; regime 用 T04 §(c) 锁定日历 (bull 2020-2021 / bear 2022 / range 2023 / bull 2024-2025)。

### 7.6 B6 PIT 违规检查清单 (04 逐条自检, 任一违反 = 回测无效)

| # | 检查项 | 管线对应 |
|---|--------|----------|
| 1 | 是否有 `ts_norm > t_ms` 进入 `signal_at` | B1 归一 + B2/B3 的 `<=` 过滤 |
| 2 | 是否混入 predicted funding | B2 settled 物理隔离 |
| 3 | 是否假设 8h 固定网格 | B2 "取最近 settled" 不假设网格 |
| 4 | Coinglass 是否漏 ×1000 | B1 Coinglass 秒→ms |
| 5 | OI 是否用了未确认 bar | B3 上一根已确认 + B4 kline_unconfirmed |
| 6 | bulk 是否 T+1 对齐 | B4 bulk_daily/bulk_monthly lag |
| 7 | 是否用了未定版末根 | B4 kline_unconfirmed 禁用 |
| 8 | 延迟缓冲是否 04 实测值 | B4 LAG_* + B3 delay_buffer 参数化 |

- **04 实现要求**: 回测启动前跑 B6 8 条自检 (自动化 assert), 任一失败 → 拒绝启动 + 报错定位。

---

## 8. 缓存布局与可复现性

### 8.1 缓存目录布局 (文件清单规则)

```
cache/
├── S1_binance_vision/
│   ├── funding/um/BTCUSDT/
│   │   ├── BTCUSDT-fundingRate-2020-01.zip
│   │   ├── BTCUSDT-fundingRate-2020-01.zip.CHECKSUM
│   │   ├── BTCUSDT-fundingRate-2020-02.zip
│   │   ├── ... (2020-01 → 2026-09, 206 文件)
│   └── klines/um/BTCUSDT/1h/
│       ├── BTCUSDT-1h-2020-01-01.zip
│       ├── BTCUSDT-1h-2020-01-01.zip.CHECKSUM
│       └── ... (逐日)
├── S2_yahoo_anchor/          # 锚点常量表 (不运行时拉取, 见 §3)
│   └── gspc_anchor.json      # {2002-10-09:776.8, 2008-03-10:1273.4, 2022-10-13:3669.91}
├── S3_ifzq/
│   ├── sh000300/
│   │   ├── day_2018_07_17_2026_10_16.json   # count=2000 单窗 (API cap)
│   │   └── (分段拉取: 每段 ≤2000 bars + 时间窗)
├── OI_plugin/                # 默认空 (A 路径); B/C 启用时填充
│   └── {bybit|coinglass}/...
├── manifest.json             # SHA256 manifest (§8.2)
└── revision_events.log       # 修订事件 (§6.3)
```

**文件清单规则**:
1. 命名 = 源原生文件名 (Binance) / 源标识+时间窗 (S3 分段); 不重命名 (保留原始 SHA 可对照)。
2. 每 zip 旁 **强制** 有 `.CHECKSUM` sibling (Binance 提供); S3 (JSON) 无官方 CHECKSUM → 04 自算 sha256 入 manifest。
3. 每文件 = 不可变 (immutable-on-disk): 重拉走 fresh 临时路径, 校验后才替换 + 记 revision event (§6.3)。

### 8.2 SHA256 记录方式 (manifest.json)

```json
{
  "manifest_version": 1,
  "generated_at": "2026-10-17T..Z (04 首次构建)",
  "files": [
    {
      "file_path": "S1_binance_vision/funding/um/BTCUSDT/BTCUSDT-fundingRate-2020-01.zip",
      "source_url": "https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2020-01.zip",
      "sha256": "<64-hex>",
      "checksum_file": "S1_binance_vision/funding/um/BTCUSDT/BTCUSDT-fundingRate-2020-01.zip.CHECKSUM",
      "checksum_verified": true,
      "downloaded_at": "2026-10-17T..Z",
      "unit": "futures UTC ms (2025+ µs 待 04 核验)",
      "revision_flag": false
    }
  ]
}
```
- 校验: `shasum -a 256 -c FILE.zip.CHECKSUM` (MacOS) / `sha256sum -c` (Linux); 结果回写 `checksum_verified`。
- S3 等无官方 CHECKSUM 的源: 04 自算 sha256, `checksum_file` 置 null, `checksum_verified` 记自算值。

### 8.3 04 执行复现步骤 (端到端)

```
0. 读 manifest.json + 本设计文档 (t05) + T04 (t04) + t02b 可达性基线。
1. [可达性预检] curl data.binance.vision (200?) ; live API (预期 rc=35/28 → 确认 A 路径)。
2. [下载/校验] 对 manifest 每文件:
   - 本地存在 + SHA 匹配 → 用缓存。
   - 缺失或 SHA 不匹配 → 重拉 (fresh) + 重算 SHA + 对比:
       相同 → 用 fresh; 不同 → REVISION EVENT (§6.3: flag+记录+标记受影响回测重跑)。
3. [ts 归一] B1: 每源 → UTC ms int64 (逐文件量级核验 µs 陷阱)。
4. [构建表] FUNDING[S] (settled 物理隔离) / OI[S] (A 路径为空) / 锚点常量表 / regime 日历。
5. [成本参数] §4 费率 (last-known/uncertain, 04 若费率页可达则一手核验+刷新) + 滑点 (预注册)。
6. [PIT 自检] B6 8 条 assert, 全过才启动回测。
7. [回测] signal_at (B5) + regime (T04 §c) + 成本 (§4) → 45 检验 (T04 §d)。
8. [复现留痕] 记录: 每文件 SHA + 下载日期 + 修订事件 + 成本参数版本 + OI 路径 (A/B/C) + 降级事件 → 任何时点可复现同一结果。
```
- **可复现性定义**: 给定 manifest (SHA 锁定) + 本设计 (lag/成本/规则锁定) + T04 (信号/regime/多重检验锁定) → 04 任一环境重跑, 结果 bit-level 一致 (除非触发 revision event / 成本刷新, 均留痕)。

---

## 9. 探针实测附录 (全部 curl 原样记录, host 2026-10-17)

> 本环境 = 选择性网络阻断 (t02b: api.bybit.com/api.binance.com rc=35 TLS reset; fapi.binance.com rc=28 timeout; data.binance.vision 200 OK)。下列为本节点自测, 不可达者如实记 "unreachable + 尝试记录"。

| 组 | 命令原样 | 结果 | 判定 |
|----|----------|------|------|
| S1 根 | `curl -s -A "$UA" -w "HTTP=%{http_code} size=%{size_download}" "https://data.binance.vision/" --max-time 30` | HTTP 200, size 2712 (custom "Binance Data Collection" HTML) | 可达 |
| S1 funding 起 | `curl -s -A "$UA" -r 0-0 -o /dev/null -w "%{http_code}" "https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2020-01.zip" --max-time 30` | **206** (存在) | 2020-01 起点确认 |
| S1 funding 前 | `... BTCUSDT-fundingRate-2019-12.zip ...` | **404** (缺失) | 2019-12 不存在 → 起点=2020-01 |
| S1 kline 起 | `... klines/BTCUSDT/1h/BTCUSDT-1h-2020-01-01.zip ...` | **206** (存在) | 2020-01-01 起点确认 |
| S1 kline 前 | `... BTCUSDT-1h-2019-12-01.zip ...` | **404** | 2019-12-01 不存在 |
| S1 updates 候选 | `curl ... "https://data.binance.vision/updates/" ...` (data/spot/daily/updates, data/spot/monthly/updates, data/updates 均试) | 全 **404** (站点不暴露目录列举) | updates 清单改从 README 取 (§6.1) |
| S2 Yahoo q1 | `curl -s -A "$UA" -L -w "HTTP=%{http_code}" "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=full&interval=1d" --max-time 30` | **403** (size 3369, JS/consent 壳非 JSON) | **unreachable** |
| S2 Yahoo q2 | `... query2.finance.yahoo.com ...` | **403** | **unreachable** |
| S2 新浪锚点 | `curl -s -A "$UA" -H "Referer: https://finance.sina.com.cn" "https://hq.sinajs.cn/list=gb_ixic" --max-time 30` | **200** (GBK: "纳斯达克,26140.0340,-2.14,2026-10-17 05:30:00,...") | **可达** (锚点源) |
| S2 新浪标普 | `... hq.sinajs.cn/list=gb_$inx ...` | **200 但空串** (代码无效) | 标普代码未命中, 锚点仍走 §3 常量表 |
| S3 ifzq 起 | `curl -s -A "$UA" "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh000300,day,,,2000,qfq" --max-time 30` | **200**, bars=2000, first=**2018-07-17**, last=2026-10-16 | **可达**, 起点 2018-07-17 (API-observable) |
| S3 ifzq cap | `... count=4000,qfq` / `count=8000,qfq` | **param error** (`{"code":0,"msg":"param error","data":[]}`) | 单次 cap ≈ 2000 |
| S3 ifzq 无qfq | `... count=320 (无qfq)` / `count=640 (无qfq)` | 空 data / param error | 指数须 qfq |
| S4 费率页 | `curl -s -A "$UA" -L "https://www.binance.com/en/fee/trade" --max-time 30` | **HTTP 000, rc=28 (TIMEOUT)** | **unreachable** (§4) |
| S4 费率页 fut | `... /en/fee/futuresFee ...` | **TIMEOUT rc=28** | **unreachable** |
| S4 web_fetch | `web_fetch https://www.binance.com/en/fee/trade` | **"non-public IP address"** | **unreachable** |

**rc 语义**: 35 = TLS 连接错误 (reset), 28 = 超时, 0 = 成功。

---

## 10. output_schema 映射 (供任务 JSON 回填)

```json
{
  "cache_strategy": "SHA256 manifest (cache/manifest.json) + 每 zip 旁 .CHECKSUM sibling (shasum -a 256 -c); 下载即留痕 (file_path/sha256/downloaded_at/source_url); 重拉走 fresh 临时路径, SHA 变化 → revision_event (flag+记录+标记受影响回测重跑), 永不静默; 文件 immutable-on-disk。",
  "pit_rules": [
    "B1 normalize_ts: 全源 → UTC ms int64; Binance/Bybit 原生 ms, Coinglass 秒×1000, Binance SPOT 2025+ µs÷1000 (反向陷阱), FUTURES 2025+ 04 逐文件量级核验",
    "B2 latest_settled_funding: settled-only (与 predicted 物理隔离), ts_norm<=t_ms 取最近, 不假设 8h 网格",
    "B3 latest_oi: bar_start+duration_ms+delay_buffer<=t, 保守只用上一根已确认 bar (仅 OI_ENABLED)",
    "B4 LAG_RULES 参数化 04 实测: funding_settled(+LAG_SETTLE_PUB_MS) / bulk_daily(T+1+LAG_T1_MS) / bulk_monthly(当月第一周一 LAG_FIRST_MONDAY_MS) / kline_unconfirmed(末根禁用); 不得假设 ts=可用时刻",
    "B6 8 条 PIT 自检 assert, 任一违反回测无效 (04 启动前跑)"
  ],
  "sources": [
    {"venue": "data.binance.vision", "dataset": "fundingRate", "range": "2020-01→2026-09 (206 monthly)", "format": "monthly zip", "unit_rule": "futures 原生 UTC ms; 2025+ µs 陷阱 04 逐文件核验; 可达"},
    {"venue": "data.binance.vision", "dataset": "klines 1h", "range": "2020-01-01→ (daily)", "format": "daily zip", "unit_rule": "futures 原生 UTC ms; 未定版末根禁用; 可达"},
    {"venue": "Yahoo (query1/query2)", "dataset": "^GSPC 1d", "range": "last-known 1950→ (本环境 403 不可复核)", "format": "JSON (403 返 JS 壳)", "unit_rule": "epoch ms UTC; 锚点改走新浪 hq.sinajs.cn (可达); 锚点统一 3669.91 (02.5 判定), Yahoo 3577.0 未采用"},
    {"venue": "腾讯 ifzq", "dataset": "sh000300 1d (沪深300)", "range": "API-observable 2018-07-17→2026-10-16 (cap ~2000/call)", "format": "JSON day bars (需 qfq)", "unit_rule": "date string 本地 CST 日线指数 (非 ms); 000300 须用生效日当时成分 (幸存者/前视)"}
  ]
}
```

---

## 附: 本节点 owner 交接 (给 04 执行节点)

- **成本参数** (本节点独有 owner): 费率 last-known (spot taker 0.1000% / futures taker 0.0500% / maker 0.0200%, **uncertain**, 2026-10-17 未一手核验) + 滑点预注册 (base 0.01% / stress 0.02% / side, taker 成交)。04 若费率页可达 → 一手核验 + 刷新 + 标记受影响回测重跑。
- **S2/S3 历史深度** (02.5 #2 承接): S2 本环境 403 不可复核 (last-known 1950, 锚点走新浪); S3 ifzq 单次 cap ≈2000 bars, API-observable 起点 2018-07-17 (04 需 2018 前须分段拉取)。
- **OI 路径**: 本环境默认 A (funding-only), B 条件 (需无阻断网络), C 按 T04 §(a) 三条件 (04 回测后判定, 阈值锁定)。
- **修订应急**: MEDIUM, SHA256 缓存 + 重拉 flag 机制 (不写"低风险")。
