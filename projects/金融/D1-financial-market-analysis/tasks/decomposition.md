# D1-financial-market-analysis — 任务分解与状态

> origin: ai · 2026-11-03 · 权威任务记录（CLAUDE.md 规定 md 工件为权威，非 JSON 草稿）

## 当前焦点：F8 正交信号源（已收口）

### 结论（负面结果，本身有价值）
**在「免费 + point-in-time + 2020-2026 日线」约束下，crypto 日频信号高度冗余，不存在可验证的正交日频信号源。**

已穷尽方向（详见 `loop-artifacts/stages/exploration/r7-f8-data-survey/research-results.md`）：
| 方向 | 判定 | 关键证据 |
|------|------|----------|
| DeFi TVL 变化率 | ❌ 冗余 | ρ(FR,ΔTVL)=0.43 超阈值；偏相关 0.22 仅因共享极慢结构性周期 |
| 期权 IV/skew | ⚠️ 无免费历史 | Deribit 仅当前值，get_historical_volatility 只给 ~16 天 realized vol |
| OI 历史 | ❌ 无免费历史 | Bybit/Binance startTime 对 2020/2021 返回 invalid |
| 多空比 | ❌ 无免费历史 | Binance takerLongShortRatio 同 OI |
| 链上资金流 | ❌ 需付费 key | Glassnode/CryptoQuant 401，free tier 90 天深度不够回测 |
| 稳定币供应 | ❌ 无免费历史 | DefiLlama stablecoin-chart/all 404 |
| 跨交易所 FR spread | ❌ 无免费历史 | Bybit funding/history 仅 ~200 条(≈2月) |

### 核心教训
F4-F8 反复撞同一堵墙：现有免费信号池（funding rate + basis + TVL）都是「市场热度」的不同度量，不是独立信息通道。真正的正交信息需要**付费数据**或**自建积累**。

### 唯一可行路径（待启动）
1. **Deribit IV 采集器**（方案 B）— 从今天开始每日积累 mark_iv + delta → 25-delta IV/skew/term structure。forward-looking vs funding 的 backward-looking，理论上最正交。3 个月后可初步验证。
2. 或接受 F8 负面结果作为正式结论（已完成，见上表）。

## 任务表

| ID | 任务 | 状态 | 备注 |
|----|------|------|------|
| F8-1 | 正交信号源数据可得性调研 | ✅ done (2026-11-02) | research-results.md 完整落盘 |
| F8-2 | TVL 正交性检验 | ✅ done (2026-11-02) | FAIL，ρ=0.43 |
| F8-3 | Deribit IV 采集器 | ⏳ ready | 一次性脚本+cron，今日启动 |
| F8-4 | F8 组合实验设计 | blocked | 等 F8-3 积累 ≥90 天 IV 数据 |

## 阻塞项
- F8-4 需成璐决策：是否接受「免费数据下 crypto 日频信号高度冗余」作为 F8 正式结论（负面结果可发表），还是投入时间等 IV 采集器积累。
