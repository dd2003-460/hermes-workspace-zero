# F10-R3 / C — 策略拥挤与自我瓦解

# origin: ai (成璐 F10-R3 调研任务书 2026-11-01) | 执行: arena agent mode | 观测日: 2026-11-01
# 子问题: 策略变拥挤时收益如何衰减? 有没有预测"什么时候会拥挤"的前置指标? funding rate 作为拥挤度代理是否有效?
# 交叉验证: 每结论 ≥2 独立团队, 明细见 receipts.json

## 1. 直接回答 (≤3 行)

收益随拥挤**单调衰减**这件事有硬数据(发表后 -58%、样本外 -26%、样本外仅保留 ~50%), 是可测的;
但"**什么时候会变拥挤**"只有弱预测力, 所有文献给的是**条件概率**而不是时点。
可操作指标 3-4 个: 共动性 / carry-z / 容量上限 — 加密上只有 carry 有学术支撑, 且方向是"高 carry → 崩盘风险↑"而**不是**"立刻回归"。

## 2. 证据列表

### C1 · Lou & Polk (2022) Comomentum: Inferring Arbitrage Activity from Return Correlations — Review of Financial Studies
- 指标定义: winner/loser 组合内 **factor-adjusted 收益的两两相关**(日/周频), 记 CoMOM = (CoMOM_L + CoMOM_W)/2; 高 CoMOM = 套利者已挤入。
- 结论: 高 CoMOM → 动量**长期反转/崩盘**、波动上升、偏度更负; 对 short-run reversal(负反馈策略)**无此效应** → **只对正反馈策略成立**。([1])
- 对我们最有用: 这是唯一"用价格自身算拥挤度、不需持仓数据"的成熟方法 → 可直接移植到加密策略篮。

### C2 · 衰减曲线: McLean & Pontiff (2016, JF 71(1):5-32) + Falck, Rej & Thesmar (2022, QF 22(11))
- 数字: 97 个预测因子 样本外 **-26%**、发表后 **-58%**(差 32% 归因于发表后资本涌入); 发表异象样本外平均保留 **~50%**; 衰减与 in-sample 收益大小、低流动性、高特质风险**正相关**。([2][3])
- 对我们最有用: 给 F10 的"新空间"一个**折价因子 0.5** 与"越漂亮的历史回测衰减越快"的先验。

### C3 · Khandani & Lo (2011) What Happened to the Quants in August 2007? — J. Financial Markets 14(1):1-46
- 机制: 同构组合**协同去杠杆**(7 月已开始, 8/6 当周爆发, 8/10 反弹); 模拟做市策略在 8/6 当周显著为负、前后为正 → 是"强制平仓 + 做市风险资本撤离", 不是基本面。
- 对我们最有用: 拥挤的**实现形式是相关性上升 + 强制去杠杆**(断崖), 不是收益率缓慢下滑(斜坡) → 模型里必须有杠杆/保证金状态。([4])

### C4 · Stein (2009) 对 reflexivity 的形式化 (二手引述, 未直核原文)
- 核心: 每个套利者不确定"有多少同行在场" → 拥挤度是内生的、且**高拥挤时套利者行为会放大而非纠正**偏离。
- 状态: 本沙箱只拿到二手引述(EFMA 2024 论文转述), **未直核 Stein 原文**, conf 0.60。([5])
- 对我们最有用: 给"reflexivity"一个可检验形式 = 策略收益对自身拥挤度的弹性符号在拥挤区翻转。

### C5 · Schmeling, Schrimpf & Todorov (2023) Crypto carry — BIS Working Paper 1087
- 数字: 加密 carry 年化均值 **>10%**, 峰值达 **60%**(远高于股/债/汇/商品); 高 carry **预测未来崩盘**, 与崩盘保险价格同涨; carry 由"散户追涨 + 套利资本稀缺"驱动。([6])
- 对我们最有用: funding/basis 是**有学术背书**的加密拥挤度代理 — 但用途是"崩盘风险↑", 不是"方向做反"。

### C6 · 反例(必须记录): 公开独立复现 + 我们自己的 F10-R2
- 公开复现(6.1M settlements / 3 所 / 无幸存者偏差): funding **水平**能预测收益(IC +0.013, t=4.7)但**符号为正**(延续而非反转); 加 OI 条件化后, 日匹配下从 +34bps/day 塌到 **+7.0bps (t=0.35)**; ΔOI 本身基本就是短周期反转的另一种测法。([7])
- 与 F10-R2 一致: funding 极端 + OI 骤降后 24h 价格**继续原方向**(翻方向后胜率 83-87%)。
- 对我们最有用: **"OI 变化"作为拥挤度代理应直接弃用**; 这是两条独立证据线(外部复现 + 我们预注册回测)同时否定的唯一指标。

### 2.1 可操作拥挤度指标表 (≥3 个, 含数据可得性)

| # | 指标 | 定义 | 数据源 | 可得性 | 证据强度 |
|---|---|---|---|---|---|
| 1 | **共动性 CoMOM** | 策略篮(动量/反转/carry/事件)内 factor-adjusted 收益 20-60d 滚动两两相关 | Binance 1d/1h klines(data.binance.vision, 免费) | 高, 今天可实现 | 股票强(0.8)/加密未验证(0.4) |
| 2 | **Carry / funding z-score** | 结算 funding 累计年化 + 逐合约滚动 z | data.binance.vision fundingRate(2020-, 免费) / Bybit / OKX | 高, 免费 | BIS 强(0.8), 方向=崩盘风险非反转 |
| 3 | **容量上限 AUM\*** | 由 √Q 冲击容忍度 + alpha 半衰期 + 二次成本反解最优规模 | klines volume(免费) + L2 depth(部分付费) | 中 | 理论成熟(0.6), 参数需本地校准 |
| 4 | **杠杆密度** | 强平价附近的 OI 密度(由 OI+funding+抵押率反推) | OI 免费; 逐笔强平流(Binance liquidationSnapshot)**已停供** | 低-中 | 0.5(见 D) |
| 5 | ~~OI 变化~~ | ΔOI 3d | Bybit 1d OI(2022-, 免费) | 高 | **反证 0.7 — 弃用** |

## 3. 对 F10 模型设计的启示 (≤5 行)

1. **拥挤度只做风险调节器, 不做方向信号**: carry-z 高 → 降杠杆/加宽止损/缩短持有, 而不是反向开仓 — 这正是 F10-R2 反转失败的教训。
2. **移植 CoMOM 到加密策略篮**: 先定义 3-5 个篮, 再用 20-60d 滚动相关; 移植前必须先验证方向(conf 0.4, 是假设不是结论)。
3. **每个"新空间"必须报 AUM\* 容量上限**, 报不出的不可交易 — 这是把"α 是否还存在"变成可证伪问题的最便宜办法。
4. **折价因子 0.5**: 任何历史回测的 OOS 预期先乘 0.5(C2), 越漂亮的样本内越要乘得更狠。
5. **自我瓦解是断崖不是斜坡**: 模型必须含杠杆/保证金状态 — 我们现在只有 OI 与 funding, **缺杠杆分布**, 这是 C 子领域指出的最大模型缺口。

## 4. 未解决 / 矛盾点 (诚实标注)

- **矛盾①(conf 0.45)**: C5(BIS) 高 carry 预测**崩盘**(反转方向) vs C6 复现 funding 水平系数为**正**(延续) vs F10-R2 反转失败。差异可能来自期限(dated futures basis 周-月 vs funding 8h)与样本期, 未验证 → 在解决前, carry 只能当风险闸门。
- **矛盾②(conf 0.50)**: C4 说高拥挤时套利者放大偏离; C1 说高 CoMOM 后是长期**反转**。两者对"高拥挤之后是什么"不一致。
- **移植风险(conf 0.40)**: CoMOM 只在美股验证; 加密"策略篮"没有权威定义, 相关性在加密本底就高(同涨同跌) → 需做 beta 中性化, 否则测的是 BTC beta 不是拥挤。
- **"OI 水平" vs "OI 变化"(conf 0.60)**: 被否定的是 ΔOI; OI **水平**/杠杆密度**未被检验**, 不能一并弃用。
- **方法论(conf 0.50)**: 所有 "crowding → crash" 结论都是条件概率, 文献里**没有任何命中率数字**; 把它们当"预警准确率"是误读。
- **独立性**: C1/C2/C3/C5 为四条独立团队证据 → "拥挤可测、收益单调衰减" conf 0.85; "能预测何时拥挤" 仅 C1(+弱 C4), conf 0.35。

---
URLs (观测 2026-11-01):
[1] https://www.aqr.com/-/media/AQR/Documents/AQR-Insight-Award/2014/Comomentum.pdf
[2] https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12365
[3] https://dspace.mit.edu/entities/publication/e48d406c-5c40-4607-9924-72484366411b
[4] https://www.nber.org/papers/w14465
[5] http://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2024-Lisbon/papers/CoCrowding.pdf
[6] https://www.bis.org/publications/working-paper-1087-crypto-carry
[7] https://github.com/OctopusTakopi/funding-rate-alpha
