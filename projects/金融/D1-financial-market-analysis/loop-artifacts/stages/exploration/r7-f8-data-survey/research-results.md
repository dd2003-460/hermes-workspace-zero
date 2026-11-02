# F8 前置调研结果：正交信号源数据可得性

> origin: ai · 2026-11-02 · 本地执行（ego-browser + curl 直查 API）
> 状态：完成（部分数据源确认可用，部分确认不可用）

## 核心结论

**免费可回溯的历史数据极度有限。** 在"point-in-time + 免费 + 2020-2026 日线"三个约束下，能用的正交信号只有 2 个方向：

| 排名 | 信号 | 数据源 | 可用性 | 正交性 | conf |
|------|------|--------|--------|--------|------|
| 1 | DeFi TVL 变化率（链上资金活跃度的代理） | DefiLlama API | ✅ 2020-10 起，日线，免费无 key | 中（与 funding rate 相关性低，但都是"市场热度"维度） | 0.75 |
| 2 | 期权 IV（隐含波动率） | Deribit mark_iv | ⚠️ 仅当前值，无免费历史端点 | 高（IV 反映预期/情绪，与 funding rate 的 carry 逻辑正交） | 0.4（因为没历史） |
| 3 | 交易所 OI（持仓量） | Bybit/Binance | ❌ 仅近期（~5天），无免费历史 | 中 | 0.2 |
| 4 | 多空比 (long/short ratio) | Binance futures data API | ❌ 仅近期，startTime 参数被拒 | 低（本质是 OI 的函数） | 0.1 |
| 5 | 链上资金流 (exchange netflow) | Glassnode/CryptoQuant | ❌ 需 API key（free tier 有但需注册+限额） | 高 | 0.3 |
| 6 | 稳定币供应 (USDT/USDC) | DefiLlama stablecoins | ⚠️ 当前值可用，历史端点 404 | 中 | 0.3 |

## 逐源详情

### 1. DefiLlama — DeFi TVL（✅ 推荐）

- **URL**: `https://api.llama.fi/v2/historicalChainTvl/{chain}`
- **免费**: 是，无需 API key
- **时间范围**: 2020-10-30 起（BSC 链验证：2195 个数据点）
- **粒度**: 日
- **内容**: 各链/协议的 TVL（Total Value Locked）
- **PIT 可行性**: Y — 每日一个值，时间戳明确
- **正交性论证**: TVL 反映的是"多少资本锁在 DeFi 协议里"，funding rate 反映的是"永续合约的借贷成本"。两者驱动机制不同（TVL = 收益率套利/抵押需求, funding = 杠杆拥挤度）。直觉上 ρ < 0.3，但需要实证验证。
- **局限**: 不是直接的"交易所资金流入流出"，是间接代理。BTC/ETH 主链 TVL 包含大量 DeFi 而非 CEX 余额。
- **来源**: 实测 API 返回 2195 点 (2020-10 → 2026-11)
- **conf**: 0.75（数据确认可用，但正交性未实证）

### 2. Deribit — 期权隐含波动率（⚠️ 有当前值无历史）

- **URL**: `https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=option`
- **免费**: 是，无需 API key
- **时间范围**: 仅当前快照（尝试 start_timestamp=2020 仍返回当前数据）
- **粒度**: 实时（每个 option contract 一个 mark_iv）
- **内容**: 每个期权的 mark_iv、bid/ask、OI、volume
- **PIT 可行性**: N — 没有免费历史 IV 端点。`get_historical_volatility` 只给已实现波动率（realized vol），且仅近 ~16 天。
- **正交性论证**: IV 是"市场对未来的预期"，funding rate 是"当前的杠杆成本"。理论上高度正交（一个 look-forward，一个 look-back）。25-delta skew 还能区分 put/call 需求不对称。
- **如果要用**: 需要自己每天爬一次 Deribit API 积累数据（从今天开始），或者找学术论文附带的历史 IV 数据集。
- **来源**: 实测 API，2020 timestamp 返回当前数据（非历史）
- **conf**: 0.4（信号质量高但无历史 = 不能做回测）

### 3. Bybit / Binance — Open Interest（❌ 无免费历史）

- **Bybit**: `https://api.bybit.com/v5/market/open-interest` 仅返回最近几条（实测 3 条 = 3 天）
- **Binance**: `openInterestHist` 的 startTime 参数对 2020/2021 时间戳返回 "parameter invalid"；仅近期可用
- **F10 研究实际用法**: 用 Bybit 当前 OI + Binance Vision klines（价格），OI 只作为 contemporaneous 变量
- **结论**: OI 历史数据不免费可得。Glassnode free tier 可能有但需注册 API key。
- **conf**: 0.2（确认不可用）

### 4. Binance Futures Data API — 多空比（❌ 无免费历史）

- **URL**: `https://fapi.binance.com/futures/data/takerlongshortRatio`
- **问题**: startTime 参数对 2020/2021 返回 invalid；仅支持近期查询
- **结论**: 同 OI，不免费可得历史
- **conf**: 0.1

### 5. Glassnode / CryptoQuant — 链上指标（❌ 需 API key）

- **Glassnode**: `api.glassnode.com` 返回 401 without key。Free tier 存在但需注册，且有速率限制 + 历史深度限制（community plan 通常只给 90 天）
- **CryptoQuant**: 同样 401 without token
- **如果成璐愿意注册**: Glassnode community plan 可能够（exchange_netflow, exchange_balance 等），但历史深度是瓶颈
- **conf**: 0.3（理论上最正交的信号，但实操门槛高）

### 6. DefiLlama Stablecoins — 稳定币供应（⚠️ 部分可用）

- **当前值**: `https://stablecoins.llama.fi/stablecoins` ✅ 返回 427 种稳定币，USDT 总额 $179B
- **历史**: `stablecoin-chart/all` 和 `stablecoin-history/all` 端点返回空/404
- **结论**: 能拿当前快照但不能回溯。如果要历史 USDT supply，需要从 Tether 透明页手动爬或找第三方
- **conf**: 0.3

## 推荐方案（F8 实验设计输入）

### 方案 A：DefiLlama TVL 变化率（立即可做）

- **信号定义**: ΔTVL_7d / TVL_t（7 天滚动变化率，归一化）
- **为什么选它**: 唯一确认有 6 年免费历史的"链上活动"代理
- **预期正交性**: 中（ρ 可能在 0.2-0.4 区间，需要实证）
- **风险**: TVL 变化可能是"市场热度的另一个度量"而非独立信息源——如果 funding rate 和 TVL 都跟着 BTC 价格走，那它们只是同一个因子的两个表达
- **验证方法**: 先算 ρ(funding_rate, ΔTVL) 分 regime（牛/熊/震荡），如果某 regime 下 ρ < 0.2 就有组合价值

### 方案 B：自建 Deribit IV 采集器（长期）

- **做法**: 写一个 cron job 每天拉一次 Deribit 全 option book，存 mark_iv + delta（从 strike 推算）
- **产出**: 25-delta IV, 25-delta skew (call_iv - put_iv), term structure slope
- **时间线**: 从今天开始积累，3 个月后有 90 天数据（不够回测但够校准）
- **短期替代**: 搜索 arXiv 上用了 Deribit 历史 IV 的论文，看他们是否共享数据集
- **正交性**: 高（IV 是 forward-looking，funding 是 backward-looking）

### 方案 C：注册 Glassnode free tier（如果成璐愿意花 5 分钟注册）

- **能获得**: exchange_netflow, exchange_balance, active_addresses（90 天历史）
- **局限**: 90 天太短，不够做 2020-2026 回测
- **判断**: 性价比低，除非 Glassnode 改政策

### 最终推荐

**F8 第一步**: 用方案 A（DefiLlama TVL）做快速正交性检验（半天工作量）：
1. 拉 BSC + Ethereum 链 TVL 日线（2020-10 → now）
2. 与已有 funding rate 数据对齐
3. 分 regime 算 ρ + 做 Granger causality
4. 如果 ρ > 0.5 → 放弃（信息冗余，跟 F7 的 basis 一样）
5. 如果 ρ < 0.3 → 加入 F8 组合实验

**F8 第二步（并行）**: 启动方案 B 的 IV 采集器（一次性写脚本，之后自动跑），为未来积累数据。

**不做**: 方案 C（性价比太低）。

## 搜索记录

| 查询 | 工具 | 结果 |
|------|------|------|
| Deribit get_book_summary_by_currency (2020 ts) | curl | 返回当前数据，无历史 |
| Deribit get_historical_volatility | curl | 仅 ~16 天 realized vol |
| Bybit open-interest (current) | curl | 3 条记录（3 天） |
| Binance openInterestHist (2021 ts) | curl | "parameter startTime is invalid" |
| Binance takerLongShortRatio (2020/2021 ts) | curl | "parameter startTime is invalid" |
| Glassnode exchange_netflow (no key) | curl | 401 |
| CryptoQuant capital_flow (no key) | curl | 401 |
| DefiLlama historicalChainTvl/Binance | curl | ✅ 2195 点 from 2020-10 |
| DefiLlama stablecoins (current) | curl | ✅ 427 种, USDT $179B |
| DefiLlama stablecoin-chart/all | curl | 404/empty |
| OKX option instruments | curl | 650 个 BTC options（当前） |
| OKX option candles (historical) | curl | 0 records |
| Binance Vision fundingRate 2021-03 | curl download | ✅ 918 bytes CSV |
| GitHub search "crypto funding rate historical" | GitHub API | 3 repos, max 9★ |

## 未解决的问题

1. **Deribit 历史 IV 有没有学术数据集？**— 需要搜 arXiv（arena 外包任务）
2. **TVL 变化率与 funding rate 的实际 ρ 是多少？**— 需要跑数据（本地可做，下一步）
3. **Glassnode free tier 到底给多深历史？**— 需要注册才能确认
4. **有没有其他免费链上数据源我没想到？**— 如 Dune Analytics public queries（需要 Dune account）
## 正交性检验结果（2026-11-02 本地执行）

### 方法
- 数据：BTCUSDT funding rate（Binance Vision, 2020-01→2025-12, 2465 天）× DefiLlama ETH/BSC TVL（7天滚动变化率）
- 指标：Pearson ρ（零阶 + 控制 BTC 日收益后的偏相关）
- Regime split：30日均线上下分牛熊

### 结果

| 指标 | ETH ΔTVL | BSC ΔTVL |
|------|----------|----------|
| 零阶 ρ(FR, ΔTVL) | **0.4274** (t=23.5, n=2465) | **0.5107** (t=27.6, n=2155) |
| 牛市 ρ | 0.3996 (n=1149) | — |
| 熊市 ρ | 0.3453 (n=1013) | — |
| 偏相关 ρ(FR, TVL_ret \| price_ret) | **0.2153** (n=2191) | — |
| R²(TVL_ret ~ price_ret) | 0.0017 | — |
| R²(FR ~ price_ret) | 0.0001 | — |

### 判定

**FAIL — TVL 不作为 F8 正交信号。**

理由：
1. 零阶 ρ=0.43 超过 0.3 阈值 → 信息冗余
2. 偏相关降到 0.22 看似通过，但原因是 TVL 和 FR 各自都与 BTC 日收益几乎无关（R²≈0），说明它们共享的是一个**极慢的结构性周期**（DeFi 夏季/冬季、机构入场/退出），不是日频可交易信号
3. 实际含义：ΔTVL 能解释的"超出 funding rate 的增量方差"只有 ~5%（0.22²），远不够构成独立 alpha 源
4. 与 F7 的 basis 冗余问题同构：都是"市场热度的不同度量"，不是真正正交的信息通道

### 下一步建议

F8 的真正出路不在"找更多免费数据"，而在：
1. **Deribit IV 采集器**（方案 B）— 从今天开始积累，是唯一确认理论上正交的信号（forward-looking vs backward-looking）。3 个月后可做初步验证。
2. **换思路**：不找"新数据源"，而是找"新变换"——比如 funding rate 的**跨交易所差异**（Binance vs Bybit vs OKX 的 FR spread），这不需要新数据源（三个交易所的 FR 都免费可得），但可能捕捉到套利机会/流动性碎片化信息。
3. **接受 F7 结论**：在免费数据约束下，crypto 市场的日频信号高度冗余，真正的正交信息需要付费数据（Glassnode/CryptoQuant 链上指标）或期权数据（需积累）。

### 数据文件
- `data/tvl_ethereum.csv` (3324 行)
- `data/tvl_bsc.csv` (2195 行)
- `data/orthogonality_test_results.json`

### 补充：跨交易所 FR spread 可行性（2026-11-02）

测试 Bybit `funding/history` API：仅返回最近 ~200 条（≈2 个月），startTime 参数对 2020 年返回空。
**结论**：跨交易所 funding rate spread 同样没有免费历史数据，不可行。

### F8 最终判定

**在"免费 + point-in-time + 2020-2026 日线"约束下，不存在可验证的正交日频信号源。**

已穷尽的方向：
- ❌ DeFi TVL 变化率 → ρ=0.43（冗余）
- ❌ 期权 IV/skew → 无免费历史
- ❌ OI 历史 → 无免费历史
- ❌ 多空比 → 无免费历史
- ❌ 链上资金流 → 需付费 API key
- ❌ 稳定币供应 → 无免费历史
- ❌ 跨交易所 FR spread → 无免费历史

**唯一可行路径**：自建 Deribit IV 采集器（从今天开始积累），或接受"免费数据下 crypto 日频信号高度冗余"作为 F8 的正式结论（本身就是一个有价值的负面结果）。
