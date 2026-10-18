# origin: ai (Lead 内联预检, 2026-10-17 17:08)

## Lead 内联预检记录（供 T07/T05v2 完成后交叉核对，不作为节点输入）

### P1: 6 个 B 层 arXiv ID 直验（export.arxiv.org/abs 逐页, 17:07-17:08）
| ID | HTTP | 标题 | 判定 |
|---|---|---|---|
| 2601.10812 | 200 | Optimal Liquidation of Perpetual Contracts | B→A 可升级 |
| 2605.05089 | 200 | Dynamic Collateral Control for Permissionless Spot Perpetual Basis Trading | B→A 可升级 |
| 2602.11708 | 200 | Systematic Trend-Following with Adaptive Portfolio Construction: Enhancing Ri… | B→A 可升级 |
| 1905.05023 | 200 | Avoiding Backtesting Overfitting by Covariance-Penalties: an empirical invest… | B→A 可升级 |
| 2209.13623 | 200 | Publication Bias in Asset Pricing Research | B→A 可升级 |
| 2309.06711 | 200 | Epps Effect and the Signature of Short-Term Momentum Traders | B→A 可升级 |

**交叉核对规则**: T07 返回后，若其分层表与上表矛盾（如仍标 13A/6B 且未说明原因），flag 到 T08 gap 列表。

### P2: Yahoo ^GSPC range=max → "Edge: Too Many Requests"（限流, 17:06）
**环境事实**: 本环境 Yahoo chart API 存在限流。T05v2 的深度探针若同现限流，fallback = 新浪 .INX（02 实证起点 2004-01-02）。

### P3: 腾讯 ifzq kline 接口 "bad params"（17:08, 未带正确参数格式）
02 阶段 6 节点验证券时用的是另一参数格式（见 data-history-depth.md）；T05v2 按 02 实证格式重探。

## Lead 内联副脑 v4（槽位满，独立实例待补派; 红线1以内联代劳）
1. [T05 竞态] T05v1 疑似僵尸 60min+，T05v2 排队。v1 若在 v2 运行中复活并写盘 → v2 prompt 已内置协同协议（先盘后写，存在则只补核验）→ 可接受。
2. [T07 交叉点] 6 个 B 层 ID 实测全 200 → T07 完成后分层预期应为 19A（或说明性降级）。T07 应独立得出此结论；若未得出 = 幻觉/不一致 flag。
3. [S2 风险 — 重要] Yahoo 限流 + 新浪起点 2004-01-02 → 若两源深度探针对 S2 都失败或起点>2002，则 **S2 的 2002-10-09 熊底锚点在回测中不可用**（数据不存在），S2 窗口实际下限=2004-01-02（或更晚），2002 锚点降级为"历史参考点"而非回测窗口锚。T08 一致性检查必须包含此项：核对 T05 深度探针实值 vs T06 §1 S2 窗口假设。
4. [机制] 僵尸槽位（T05v1/副脑v3）阻塞独立副脑与 T05v2 派发 → 等待任一完成通知释放槽位，届时优先补 T05v2，副脑 v4 独立实例随后。

## §T05 审读结论 (Lead, 17:44) — 审读=PASS
- 8 项 spec 全部盘上核验: S1可达+起点2020-01 / S2锚点3669.91统一(02.5判定)+新浪可达 / S3 ifzq qfq+cap2000+起点2018-07-17 / 成本uncertain不编造(last-known 0.1000%/0.0500%+滑点0.01%/0.02%) / OI=A插件默认关 / SHA256缓存+重拉应急 / PIT B1-B6逐条映射。
- 执行身份: 649a24df(原v1)76min完成=慢非死; v2(827782bf)按协同协议将走只读核验+追加, 无覆盖冲突。
### Flags
- **F1→04 B1**: binance-public-data README 明文 SPOT 2025-01+ 时间戳=µs → 04 须逐文件量级核验(13位=ms/16位=µs, µs÷1000); FUTURES 2025+ 未明示=未知。
- **F2→T08 gap 列表**: updates/ 清单 T05 实测=2 文件 vs 02.5 #6 记录=3 文件(均spot, 方向一致, 计数矛盾待裁)。
- **F3→T08+03-task_graph-review 风险登记**: S2 本环境执行阻塞=Yahoo 403 且新浪 hq.sinajs.cn 是报价 API 非历史 K 线 API → 04 必须预注册 S2 诚实 fallback(本环境不可执行即如实报告, 不静默丢弃); S2 2002-10-09 起设计在无阻断环境仍有效。
### 教训
- 本环境子代理实际耗时 55-76min 远超 25min 预算属常态; "零磁盘活动"≠死(T03v1/T05v1 均为慢); v1/v2 竞态由协同协议(v2 只读核验+追加)无损化解。
