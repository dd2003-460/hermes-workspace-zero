# 阶段02 资料搜集 — 研究索引

**状态**: 已完成（7/7 全部落盘 + field-apply，`remaining.complete=true`，待写 advance 推进 02.5）
**更新**: 2026-10-17 03:40

## 因素 → 工件映射

| # | 因素（阶段01 research_required） | 工件 | 状态 | disposition |
|---|---|---|---|---|
| 1 | 数据历史深度与退市标的覆盖（幸存者偏差） | research/data-history-depth.md | ✅ 完成 | research_required (0.55, 4条URL) |
| 2 | 可得数据跨度能否覆盖牛市 | research/bull-coverage.md | ✅ 完成 | confirmed (0.78, 2条URL) |
| 3 | 熊市与震荡市状态覆盖 | research/bear-range-coverage.md | ✅ 完成 | research_required (0.7, 2条URL—S1/S2 主代理一手实证，S3 A股未证) |
| 4 | 稳定性判据：窗口划分与通过阈值 | research/stability-criteria.md | ✅ 完成 | confirmed (0.8, 17条arXiv) |
| 5 | 资金费率/OI 发布时点与更新频率 | research/funding-rate-oi-timing.md | ✅ 完成 | confirmed (0.75, 7条URL；含 observed_at=2026-10-16T17:10Z) |
| 6 | 数据修订与迟报机制 | research/data-revision-latency.md | ✅ 完成（01:47 落盘） | confirmed（修订风险=中；futures 归档是否被修订=核心待证） |
| 7 | 公开基准与已知失败模式 | research/public-benchmarks.md | ✅ 完成（03:09 落盘，03:35 field-apply） | confirmed (0.68, 19条arXiv—13条abs页fetch验证+6条列表级；主代理独立抽查 4/19 全过) |

## 交叉询问回执

- web-llm-cross-check.md — `ralph prompt-first web-llm` 真实回执。3 个 provider（perplexity/chatgpt/gemini）全部 error：Chromium profile 被其他实例占用（ProcessSingleton 锁）。按 02 规则记录失败后继续公开网页搜集，不重试。

## 暂定结论汇总（供03，不写最终推荐）

1. **S1 主数据源**: Binance 官方逐日文件（data.binance.vision）+ Coinglass（含 Delisted Pairs，规避幸存者偏差）；免费可支撑 5 年 OOS。
2. **A4 可行窗口**: S1 锚定 **2020-01 起**（2020-01→2025-01+：2020-21牛+2022熊+2023震荡+24-25牛）→ A4 仍满足。主代理 2026-10-17 HTTP 一手实证：data.binance.vision 免费批量文件（逐日K线+monthly fundingRate）最早 2020-01（2019 各月 404）；2019.9 为产品上线先验，免费批量不可得。
3. **S2/S3**: 免费退市覆盖未证实（AV 免费档仅100根；Baostock/AkShare 未验证）→ 落实前保持 S1 单场景。
3.5. **S1 市场节点实证（2026-10-17 主代理直探）**: 2020-03-12崩盘底/2021-11-10牛顶/2022-01-10熊顶/2022-11-21熊底 均 206（免费逐日K线实际存在）；2018-12-15 熊底 404（早于起点，符合预期）→ #3 熊市覆盖在 S1 分支已从领域结论升级为一手实证。
4. **证据缺口**: #3 S3 A股分支未证（S1/S2 已一手实证，见 3.5）；#1 Coinglass 可回看年限未取证（Binance 起始日期已实证，见#2）；#5 Binance API 字段语义/OKX OI 深度/Coinglass 定价档位（交易所 API 与 Binance 文档站本环境不可达，需可直连环境实测）；#4 DSR/PBO 原始定义（Bailey/López de Prado）未核验；#6 A股指数 PIT 与美股财报重述 URL 未核验；#7 期刊经典文献 11 项（Bailey 2013/2014、Harvey-Liu-Zhu 2016 t>3.0、White 2000、Hamilton 1989 等）ssrn 沙箱不可达未核验，待 02.5 补。
5. **OI 历史可得性（主代理 2026-10-17 一手实证 + #5 子代理官方SDK渠道，已关闭）**: ① data.binance.vision 无 OI 历史文件（多路径探测全 404）；② **Binance 免费 OI 历史仅 30 天**（binance-futures-connector 4.2.0 原文 "Only the data of the latest 30 days is available."）→ 此前"保留期未验证"现已 SDK 渠道证实；③ **5 年免费 OI 源仅 Bybit**（官方文档：可查询上限为 symbol 上线时间）——跨交易所替代（BTCUSDT 各所 OI 高相关，但为 Bybit 数据非 Binance，需 03 决策）；④ **Coinglass 无免费档**（HOBBYIST $29/mo 起）且单请求 ≤90 天。
   **PIT 语义（#5 confirmed）**: t 时刻可用集 = 已结算费率（fundingRateTimestamp≤t，Bybit 原文 latest=last settled）+ bar_end≤t 的 OI bar（Bybit 警示极端行情延迟，回测须加缓冲）；单位陷阱：Binance/Bybit/OKX 毫秒 vs Coinglass 秒 → 归一 UTC ms 为管道必做项。
   **设计含义（更新）**: funding rate 仍为主信号（免费、2020-01 起 5 年+、含牛熊震荡）；OI 三条路：(a) 放弃 5 年 OI，(b) **Bybit 免费 OI 至其上线日（新选项，跨所代理）**，(c) 付费 Coinglass $29/mo（超默认成本门槛，需人类拍板，见 03 决策点）。
6.5. **稳定性判据（#4 完成，disposition=confirmed, 17条arXiv）**: ① 窗口划分公开实践主流 = 3–5 个互不重叠**年度** OOS 窗口 + expanding walk-forward（月级窗口文献零出现；理论守恒律 α+β≤1+Λ 约束窗口数）；② **无普适通过阈值**——最严格显式集合 = 每窗口 OOS 净收益 T≥2.0 + ≥30 笔 + 扣费净正 + 全测试年方向一致 + permutation p<0.001（arXiv:2605.04004 五条原文）；MDD 跨窗口一致性无公开标准值（03 设计项）；③ 统计门槛防不住未来信息泄漏：**结构性 point-in-time 是前提**（arXiv:2608.27734：Sharpe 35 泄漏 oracle 完整通过 DSR+PBO）；DSR/PBO 需按试验数 deflate，标签重叠用 CPCV/purged k-fold+embargo；④ 校准警告：MinervaScore 真实数据无前瞻力（ρ=0.013），绝对收益门槛会误杀真信号（arXiv:2610.07701）。→ 03 直接可用的窗口/阈值设计输入。
7. **数据修订风险（#6 完成，disposition=confirmed）**: data.binance.vision 免费逐日文件**官方承认可被历史修订**（binance-public-data README CHECKSUM 节：2022-04-21 aggTrades、2022-08-08 klines 两例，可审计）+ 日线 T+1 迟报 + API 末根 K 线未定版 → 严格 point-in-time 快照不可免费直接获得；但已记录修订均针对 spot，S1 futures funding/OI 样本影响大概率可忽略（未 100% 排除）→ **修订风险暂定=中**。决定"中→低"的关键待证: futures 归档文件是否在 2022-08 后或针对 futures 修订过。
