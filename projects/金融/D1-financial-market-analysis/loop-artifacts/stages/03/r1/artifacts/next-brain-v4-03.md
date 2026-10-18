# origin: ai
# 署名: 副脑 v4（sub-brain v4）— 分析由副脑 df5e1e83 在 context 耗尽前完成，Lead 于 2026-10-17 转录落盘并追加两条 Lead 实探验证（标 [Lead核验]）
# 阅读范围: 03-task_graph-review.md + t01/t02/t02b/t03/t04/t05/t06（t07 由 Lead grep 原文核对关键行后并入）

## P0（04 前必须解决，均不阻塞 03 CONFIRMED）

### P0-1 S3 指数错位: sh000300（T05 选定）vs sh000001（02.5 验证件） [conf 0.8]
- T05 §1.3: S3 = 腾讯 ifzq sh000300（沪深300，2005-04-08 起，API 可观测 2018-07-17→2026-10-16，单次 cap≈2000 bars，qfq）；T05 自身已注 000300 历史成分 point-in-time 风险
- 02.5 六节点 ±2% 锚点验证是在 sh000001（上证综指）上做的 → 02.5 验证证据不直接覆盖管线实际拉的指数；两者 universe 实质不同（全市场 vs 300 大中盘）
- 处置（04 前预注册）: (a) 定夺 S3 目标指数；(b) 若 sh000300，04 须在 sh000300 上重验六节点 ±2% 锚点，或显式降级锚点置信度范围；(c) 若 sh000001，T05 需补 ifzq 深度探针（未探）
- 判定: 非 03 CONFIRMED 阻塞项，但必须入确认文件"04 预注册项"

### P0-2 trial count 120 重复计数 regime-independent 基线，真值唯一 = 70 [conf 0.75]
- T07 §4.3 L216-223 原文 [Lead grep 核验]: 45 = 3 regime × 3 funding 阈值 × 5 窗口；基线 5 spec × 5 窗 × 3 regime = 75 cell；45+75=120；L221 自标"cell 计数是上限（保守）方向……若 04 采用更严格的只计搜索 spec 解释（buy-hold 等固定 spec 计 1 而非 15），计数会降到 45+5=50 起；本节点采用保守的 120"
- 副脑判定: 基线 5 条（B&H / momentum-12-1 / RSI-14 / MA(50,200) / funding 朴素分位）均 regime-independent（T07 §3 无任何 regime 条件）→ ×3 regime cell = 同一测试计 3 次 → 75 cell 实际唯一 = 25 → 真唯一 trial = 45+25 = 70
- 120 = over-deflation（有效性安全、power 损失）；T07 "避免 under-deflation" 措辞方向反了（under-deflation 来自少计）；T08v2 判 45 vs 120 "兼容"（03 预注册非 04 事后）但未点破重复计数
- 处置（04 前预注册）: 明确 trial 口径 — 推荐 70（唯一）与 120（保守上限）双报，DSR 取 max；或冻结 120 但诚实记录重复计数机制

### P0-3 S2 下限 2004-01-02 未入 artifact 链 [conf 0.85]
- on-disk T05 §5.1 只探了 Yahoo（403）+ 新浪实时 gb_$inx（空串=代码无效），从未探新浪 .INX 历史 K 线深度
- 5737 bars / first=2004-01-02 只存在于 T05v2 closing message + T06 L254（继承非实测）[Lead核验: T05v2 827782bf 死亡前探针]
- 若 04 预注册 S2 start=2002-10-09（确认文件风险登记措辞）→ 2002-2004 数据在本环境不存在 → 要么静默改 2004 起点（scope 变更）要么卡死
- 处置: (a) 把 S2 新浪 .INX 下限 2004-01-02（5737 bars, T05v2 实测）写入 03 artifact 或显式标"04-day-1 re-probe"；(b) 2002-10-09:776.8 锚点降级为"锚点仅（本环境不可回测）"；(c) S2 有效起点预注册 = 2004-01-02

## P1

### P1-1 成本接口缺口: T06 §5 期望 T05 提供 funding 结算成本归属，T05 §4 没有 [conf 0.9]
- T06 §5: "04 回测启动时从 T05 artifact §成本参数读取……taker/maker 费率、滑点模型、funding 结算成本归属、进出场点 funding 结算归属规则"
- T05 §4.2/§4.3 只有 taker/maker 费率 + 滑点（base 0.01%/side, stress 0.02%/side），无 funding payment 条目；§10 output_schema 无 cost_model/funding 归属字段
- 且交易标的（spot vs USDT-M perp）在所有 03 artifact 中未显式钉死 — 若 perp，持仓期每 8h 收/付 funding，该项成本/收益量级远大于 taker 费（funding 常态 ±0.01%/8h，挤兑期 >0.1%）
- 处置（04 前预注册）: (a) 钉死标的 = BTCUSDT USDT-M perpetual（T06 §5 "perp 策略成本是核心组成" 可推断，但未写明）；(b) 预注册 funding payment 归属规则: "entry→exit 间已结算 funding 按结算时间戳（settled 值, PIT 合规）记入 P&L，不按成交时点记账"；(c) 预注册成本敏感性网格: fee ∈ {0.04, 0.05, 0.06}% × slippage ∈ {0.01, 0.02}%/side，报告翻转 cell；verdict 在合理区间内翻转则结论报 "cost-fragile"

### P1-2 2026 数据（至 2026-09/10）vs 窗口止 2025-12: 须预注册 holdout [conf 0.8]
- 数据实际可得: S1 funding 至 2026-09、S3 ifzq 至 2026-10-16；分析窗口止 2025-12-31（T06 §1.1）；regime 日历止 2025-12-31（regime_locked，2026 无标签）
- 风险: 04 "顺手看看" 2026 数据 = informal peek，未计入 trial count 的软测试
- 处置（04 前预注册，建议现在冻结）: 2026-01→2026-09/10 段 = 预声明 quarantine holdout — 04 全程不碰、不用于任何决策、最终报告仅以 "post-protocol 段" 标签披露；或直接从 active dataset 排除

### P1-3 2020 单一 regime 训练基段 + 3 先验阈值定义模糊 [conf 0.75]
- T06 §4.3: 阈值 = "先验整值（如 sign flip、10/90 分位）——不采用样本内精确分位点" — 但"10 分位"需要一个分布来算: 先验常数（固定数字）vs expanding 训练窗分位（PIT 合规，但 2021 窗只有 2020 牛市 1 年数据，regime 无代表性、噪声大）
- 两种读法并存 = 04 的未预注册自由度
- 处置: (a) 04 前预注册 3 阈值实例化方法（推荐: sign=常数 0；low/high 分位 = expanding 训练窗分位点取整，逐窗重算）；(b) 预注册 2021 warmup 窗处置（保留报告，C4 方向一致性违反时与 regime 失败分开 flag）；(c) 记录硬数据约束: 本环境无 2020 前 funding（2019-12 404 + live API 阻断）

## P2

1. T06 Lead 批注 #3（L254）误引: 引"T06 §1.1 S2 窗口起点 2002-10-09"，但 T06 §1.1 是 S1 加密段，T06 正文不含 2002-10-09 字样（该值在确认文件风险登记 + T05 §3.2 锚点表）— 无害，但人类 reviewer 核对会找不到
2. T05 §3.2 锚点表含 2002-10-09:776.8 未标"本环境不可回测"（见 P0-3）
3. 45 矩阵 cell 语义未写明 [0.8]: (regime, threshold, window) — 若读法2（regime 过滤归属窗口）只有 15 个测试（bull 3 窗 + bear 1 + range 1 = 5 窗 × 3 阈值），不是 45；artifact 一致写 45 → 意图读法1（regime cell = 规则的 regime 条件，window = 评估期，跨 regime cell 是刻意 OOD 测试）— 必须写明，否则 trial count 语义漂移（15 vs 45）
4. T02 正文"推荐 B 为 04 默认"在 t02b 后未就地更正（更正只在 T04 Lead 批注/T05 §2/确认文件）— 单文件读者拿 stale guidance；建议 T02 加 t02b cross-ref
5. "206 文件" = HTTP 206 状态码误读 [0.9, 已坐实]: 2020-01→2026-09 = 81 个月，"206 文件"算术不可能；[Lead核验 2026-10-17] 81 个月逐一 curl -r 0-0 = 81/81 全 HTTP 206（全部存在，无缺口）→ 真实文件数 = 81；t02/t04/t05/t06/确认文件"206 文件"措辞均需修正为"81 文件（81/81 验证存在）"
6. T03 v2 的 Q6 换了查询词（"timing signal" 替代 "trading strategy"）但一致性列称"与 v1 一致" — 实为新查询，表格误导（不影响结论）
7. 2020-21 "bull" 标签含 2020-03 崩盘（-50%），regime 粒度粗；regime_locked=true 不可改，90 日滚动敏感性检查部分覆盖，记入 limitation
8. T06 §8 L212 基线行写于 17:22 早于 T07 落盘 19:14，"pending disk write" 是时间事实；T08v2 已判 drift 非 conflict，04 以 T07 终版为准

## 总结判定
- **03 CONFIRMED 不阻塞**: P0×3 / P1×3 全部是"04 必预注册项"，不改变 03 任务图结构
- 确认文件须新增"04 预注册项"节: P0-1 指数 / P0-2 trial 口径 / P0-3 S2 下限 / P1-1 标的+成本归属 / P1-2 holdout / P1-3 阈值实例化
- 确认文件"数据基础"S1 行"206 文件"须改为"81 文件（81/81 验证存在，2026-10-17 实探）"
