# F10-R3 / D — 信息不对称下的被迫流动预测

# origin: ai (成璐 F10-R3 调研任务书 2026-11-01) | 执行: arena agent mode | 观测日: 2026-11-01
# 子问题: 哪些"被迫交易"(margin call / ETF 调仓 / options gamma / 爆仓)可提前预测? 精度到什么程度?
# 交叉验证: 每结论 ≥2 独立团队 (本域 ≥3 独立团队线), 明细见 receipts.json

## 1. 直接回答 (≤3 行)

只有**日历型**(funding 结算/期权到期/指数调仓/链上清算价)能给出**事前确定时点**, 但幅度小、容量小、可交易性差;
**级联/被迫抛售型**在**高流动性大盘标的**上不可事前抢跑获利 — 3 条独立团队证据线(2026 加密永续级联 Part I/II + Perez 2021 链上清算 + Coval-Stafford 2007 / Shive-Yun 2013 JFE 机构 fire sales 实证)一致支持该边界;
真正可用的是"**暴露量核算**"(强平价密度 × 名义量)与"**同步确认**"(OI+funding+taker 方差), 不是事前点位预测。

## 2. 分类表 (类型 / 预测窗口 / 数据源 / 历史精度 / 可交易性) 与新增独立证据

| # | 类型 | 代表事件 | 预测窗口 | 数据源 | 历史精度(效应量, 非命中率) | 可交易性 |
|---|---|---|---|---|---|---|
| 1 | 日历-结算 | 永续 funding 8h 结算、交割结算价 | 提前已知, 精确到分钟 | Binance/Bybit funding API; data.binance.vision fundingRate(2020-) | 时点 **100% 机械**(方向/幅度无信息) | 高(时点确定)但空间已被套平: F9 p95 spread 0.056%→0.01% (conf 0.9) |
| 2 | 日历-行权价钉住 | 期权 OI 密集行权价的 pinning | T-3d → T 收盘 | Deribit/CME OI by strike + gamma | Ni-Pearson-Poteshman (2005): 到期日收益平均被改变 **≥16.5bps**, 合计 ~$9bn(美股) | 中(小容量); 加密无同行评审证据 (conf 0.2) |
| 3 | 日历-调仓 | 杠杆 ETF 日终再平衡、指数季度调仓 | 收盘前 30 分钟 | 发行方持仓/指数公告 | Cheng & Madhavan: 指数日变动 1% 时, 收盘再平衡可占该指数收盘成交量 **16.8%** (二手引用) | 低 — 加密无等价物, 且该效应被独立研究质疑 (conf 0.3) |
| 4 | 实时监测-级联 | BTC 永续爆仓级联 | 分钟-小时, 且是**同步**非事前 | 5m OI / funding / taker 买卖失衡; 逐笔强平流**已停供** | 7 次级联**无一变量事件不变**; 价格 CSD 仅 5/7, 2 次关税冲击完全无预警; 唯一稳健项 = taker 订单流**方差压缩**(300 onset placebo, Fisher p≈5e-6) | 中 — 只能同步跟(=F10 已发现的动量延续) (conf 0.6) |
| 5 | 结构暴露-链上清算 | Compound/Aave 抵押率公开 → 清算价可算 | 清算价事前可算; 触发时刻不可知 | 链上事件 + 预言机价格 | Perez et al. (2021): 3% 价格下跌使 **>$10M** 可清算; 2020 年 **>70%** 可清算头寸被**立即**清算(同/次区块) | 低(机器人/MEV 竞争), 但"可清算量 vs 价格"曲线是最该抄的工具 (conf 0.7) |
| 6 | 结构-分支比诊断 | λ = k·ρ (Galton-Watson 型) | 事后 in-flight, **不能事前** | 公开成交日志 + 报价冲击价 | 2025-10-10 事件 **88%** 强制卖出落在 onset 后 30 分钟内, **63%** 被场所 backstop 吸走; λ≈0.1-0.2 深度亚临界; 其两个可证伪预测在 power≥0.96 下失败 | 否 — 仅诊断, 不可交易 (conf 0.6) |
| 7 | 不可预测 | 黑天鹅/突发新闻(关税) | — | — | 7 次级联里有 **2 次**属此类, 赛前零信号 | 否 (conf 0.8) |
| 8 | 结构暴露-机构赎回抛售 | 基金极端流出触发被迫减仓 (Fire Sales) | T-1 季/月 → T 季 (2-4 周) | 13F 季度持仓 + 基金月度净申赎流 | Coval & Stafford (2007, JFE): 赎回最重十分位基金次季被迫减仓 **20.1%**, 重叠股当季 CAAR **-7.9%**(t=-3.45); Shive & Yun (2013, JFE): 对冲基金抢跑获年化 **+0.9%** alpha; Dyakov & Verbeek (2013, JBF): 实时抢跑月均 **+0.5%**, 但**大盘股在检测前已修复** | 中(仅小盘低流动性标的有效; 大盘股不可抢跑, 窗口从 1 个月缩至 2 周) (conf 0.8) |

### D8 · 第 3 条独立团队证据: 已发表机构被迫抛售预测实证 — Shive & Yun (2013-01, JFE 107(1):220-237) + Coval & Stafford (2007-11, JFE 86(2):479-512) + Dyakov & Verbeek (2013-12, JBF 37(12):4931-4942)
- 团队/出处: **Shive & Yun 团队** (Notre Dame/MSU, *JFE* 2013-01, DOI:10.1016/j.jfineco.2012.08.012)、**Coval & Stafford 团队** (Harvard, *JFE* 2007-11, DOI:10.1016/j.jfineco.2006.09.007 / NBER w11357, 2005-05) 与 **Dyakov & Verbeek 团队** (Erasmus, *JBF* 2013-12, DOI:10.1016/j.jbankfin.2013.08.013)。([7][8][9])
- 核心机制与实证精度: 由历史业绩-申赎关系 + 公开持仓可事前预测下季度被迫抛售(flow-induced forced selling); Coval-Stafford 测得被迫抛售股两季度超额下跌 **-7.9% (t=-3.45)** 并在 12-24 个月反转, 多空预期流组合月收益 **0.65%–1.07% (t=2.51–3.59)**; Shive-Yun 证实对冲基金针对下季 1% 成交量被迫流在当季提前交易 **0.29%–0.45%** 成交量、每 +1σ 抢跑度带来 **+0.9%** 年化四因子 alpha(季报强制披露期更强)。
- 可交易性边界(对 F10 最关键): Dyakov-Verbeek 样本外实时检验(1990-2010)显示 **+0.5%/月** 抢跑 alpha **仅存在于 NYSE 均值以下小盘股** — **高流动性大盘股虽有抛压但价格在实时策略可检测前已修复**, 且抛压持续期从 1990s 的 ~1 个月压缩至 2000s 的 **~2 周**。
- 对我们最有用: 已发表同行评审实证直接验证了"**公开持仓暴露可算, 但高流动性标的被迫流抢跑窗口极短且随套利竞争加速坍缩**", 解释了为何 BTC/ETH 永续(全市场最高流动性)不能做慢速反转抢跑、只能做清算热力图暴露核算与同步动量确认。

> 表中"历史精度"给的是**效应量与时点确定性**, 不是命中率: 除第 4 行有 placebo 检验外, 文献里几乎不存在"预警命中率"口径 — 这本身是 D 子领域最大空白。

## 3. 对 F10 模型设计的启示 (≤5 行)

1. **把 D 从"预测"降级为"暴露量核算"**: 用公开强平价/抵押率/持仓分布算"距下一档清算的价格距离 × 该档名义量" = **清算热力图**, 这是唯一可事前算出的量(第 5、8 行共同支持)。
2. **日历型只当时点过滤器**: 在结算/到期窗口内禁止新开方向仓, 或只做流动性提供(第 1 行空间已被套平, 别当 alpha)。
3. **级联不做方向反转下注**: 把"taker 订单流方差压缩"当**风险闸门**(降杠杆), 不当反转入场信号 — 大盘高流动性标的抢跑窗口已被压缩(第 8 行), 与 F10 动量延续一致。
4. **"温度"里加杠杆密度**: 强平价位密度 = 气体模型的**局部压强**, 比 OI 总量更接近物理量(见 C 第 4 条指标)。
5. **放弃预测黑天鹅**, 改做压力测试: 3%/5%/10% 冲击下的可清算量曲线(第 5 行方法), 这是 F10 可交付且可验证的 D 类产物。

## 4. 未解决 / 矛盾点 (诚实标注)

- **矛盾①(conf 0.50)**: Ni et al. (2005) 的钉住效应显著(≥16.5bps, $9bn) vs 独立研究 "Do Leveraged ETFs Increase Volatility" 认为 ETF 再平衡与波动的关系是 spurious。另: 16.8% 为二手转述, **未直核 Cheng & Madhavan 原文表格**。
- **矛盾②(conf 0.45)**: 2607.27070 说存在稳健前兆(taker 方差压缩), 2608.03616 说 severity 无法被任何标量前态量分级、"两个可证伪预测均失败"。二者逻辑上可并存(有总体级前兆 / 无单事件级预警), 但对外表述极易被误读成"级联可预测" — 本文件取后者为操作口径。
- **独立性说明(3/3 门禁通过)**: ① 2026 加密永续级联两篇预印本为同一作者 Part I/II(合并算 **第 1 线**); ② Perez et al. (2021, FC 链上清算) + Ni et al. (2005, JFE 日历钉住) 算 **第 2 线**; ③ 新增已发表同行评审机构 forced selling 实证 **Shive & Yun (2013, JFE) + Coval & Stafford (2007, JFE) + Dyakov & Verbeek (2013, JBF)** 算 **第 3 条独立团队证据线**(3/3 满足门禁)。
- **数据可得性(conf 0.70)**: Binance `liquidationSnapshot` 已全线停供 → D 类最关键的微观数据**不可复现**, 我们只能用 OI/funding 代理(这是 2607.27070 自己指出的结构限制)。
- **完全空白(未验证)**: 加密期权 pinning、加密 ETF 调仓、**代币解锁(unlock/vesting)** 三类均**未找到**同行评审的精度研究; 代币解锁目前只有实践者数据源(未验证, 不入表)。

---
URLs (观测 2026-11-01):
[1] https://arxiv.org/abs/2607.27070 · https://arxiv.org/abs/2608.03616
[2] https://doi.org/10.1016/j.jfineco.2004.08.005 (Ni, Pearson & Poteshman 2005, JFE 78(1):49-87)
[3] https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1539120 (Cheng & Madhavan, JOIM 2009)
[4] https://static.perez.sh/research/2020/defi-liquidations/defi-liquidations.pdf (Perez, Werner, Xu & Livshits, FC 2021)
[5] https://www.researchgate.net/publication/228727907_Do_Leveraged_ETFs_Increase_Volatility
[6] https://www.bis.org/publications/working-paper-1087-crypto-carry (流动性/杠杆背景, 见 C)
[7] https://ideas.repec.org/a/eee/jfinec/v107y2013i1p220-237.html · https://broad.msu.edu/profile/yunhayon/ (Shive & Yun 2013-01, JFE 107(1):220-237, DOI:10.1016/j.jfineco.2012.08.012)
[8] https://www.nber.org/papers/w11357 · https://www.sciencedirect.com/journal/journal-of-financial-economics/vol/86/issue/2 (Coval & Stafford 2007-11, JFE 86(2):479-512, DOI:10.1016/j.jfineco.2006.09.007)
[9] https://ideas.repec.org/a/eee/jbfina/v37y2013i12p4931-4942.html (Dyakov & Verbeek 2013-12, JBF 37(12):4931-4942, DOI:10.1016/j.jbankfin.2013.08.013)
