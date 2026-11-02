# F8 前置调研：链上资金流 + 期权 skew 数据可得性

> origin: ai · 2026-11-02 · 本地执行（arena dispatch blocked）
> 目的：F7 三市场组合 FAIL（信息冗余 ρ=-0.30~-0.39），F10 agent-game-model 全 FAIL。
> 下一步需要**正交信号源**才能构造有效组合。本调研回答：哪些免费/开放数据源能拿到
> 链上资金流和期权 skew，质量如何，能否 point-in-time 对齐。

## 背景（为什么做这个）

F4-F7 的核心教训：资金费率单信号在三市场（BTC/ETH/SOL）全部不显著，且与基差信号高度冗余。
F10 的 agent-game-model（预测新兴套利空间）也全 FAIL。
→ 结论：现有信号池（funding rate + basis）信息量不够，需要引入**不同维度的信号**。

候选正交方向（按直觉排序）：
1. **链上资金流**（exchange inflow/outflow, whale movement）— 反映真实供需
2. **期权 skew**（25-delta put-call skew）— 反映市场情绪/对冲需求
3. **持仓结构**（OI by exchange, long/short ratio）— 反映杠杆分布
4. **稳定币供应**（USDT/USDC mint/redeem）— 反映增量资金

## 调研问题

### Q1: 链上资金流 — 免费数据源有哪些？粒度如何？

搜索方向：
- Glassnode free tier / CryptoQuant free / Dune Analytics public dashboards
- Blockchain.com API (BTC), Etherscan API (ETH)
- 交易所公开 API (Binance/OKX/Coinbase 的 withdrawal/deposit 统计)
- DefiLlama (TVL changes as proxy)

关键约束：
- point-in-time：数据必须有时间戳，不能是"当前值"快照
- 免费额度够不够 2020-2026 日线回溯
- 延迟：链上确认 vs 交易所报告的时间差

### Q2: 期权 skew — 加密市场有可用的历史数据吗？

搜索方向：
- Deribit 公开 API（25-delta skew, PCR, IV term structure）
- CME Bitcoin Options（如果有公开历史）
- OKX Options API
- 学术论文中用过的加密期权数据集

关键约束：
- Deribit 是最主要的加密期权所，但历史数据从什么时候开始？
- 免费 API 能拿多久的历史？
- skew 的计算需要多个 strike 的 IV，API 是否直接提供还是自己算？

### Q3: 持仓结构 / 多空比 — 哪些数据可用？

搜索方向：
- Binance/OKX 公开的 long/short ratio（用户级别 vs 仓位级别）
- Open Interest by exchange（聚合 vs 单所）
- Funding rate 本身已经是 OI 的函数，有没有额外信息？

### Q4: 稳定币供应作为增量资金代理

搜索方向：
- USDT total supply (Tether 官方透明页 + 链上追踪)
- USDC supply (Circle 官方)
- 稳定币在交易所的余额变化（vs DeFi 锁仓）

## 产出要求

对每个数据源回答：
| 字段 | 内容 |
|------|------|
| 数据源名称 + URL | |
| 免费/付费 | |
| 时间范围（最早到最晚） | |
| 粒度（日/小时/分钟） | |
| 是否需要 API key | |
| 免费额度限制 | |
| point-in-time 可行性（Y/N + 理由） | |
| 与 funding rate 的正交性直觉（高/中/低 + 一句话理由） | |
| conf (0-1) | |

最终给一个推荐：如果只能选 1-2 个信号加入 F8 组合实验，选哪个、为什么。

## 验收标准

1. ≥4 个数据源有明确可用性判定（不是"可能可以"）
2. 每个判定有来源 URL
3. 正交性判断有逻辑支撑（不是拍脑袋）
4. 最终推荐 ≤2 个信号 + 理由
5. 找不到数据的明确说"未找到免费源"，不编造