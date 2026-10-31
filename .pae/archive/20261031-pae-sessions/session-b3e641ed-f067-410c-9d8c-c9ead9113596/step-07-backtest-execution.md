# Step 07 — 无未来回测执行（防过拟合 + 失败如实）

## 目标
对 step 06 裁决为「进入回测」的全部 idea，执行符合 `market-alpha/backtest-sop.md` 的四层护栏的无未来回测：数据只用发布戳 < T 期起点的、阈值/窗口/成本预注册冻结、多重检验 BH-FDR + DSR deflation、失败判据 Mesfin 五条 + PSR。产出回测报告与预注册文件。本步是用户「通过无未来回测验证有效性，注意不要过拟合」的直接落点。

## 涉及文件
- 只读对象：
  - `market-alpha/backtest-sop.md`、`market-alpha/preregistration-template.md`（step 02 产出，护栏与模板）
  - `market-alpha/loop-artifacts/stages/06/06review.md`（step 06 产出，进入回测的 idea 清单）
  - `projects/金融/D1-financial-market-analysis/loop-artifacts/stages/04/r1/t06-signal-backtest-report.md`（负结果报告先例：失败也按同一格式交付，含 DSR z / pooled Sharpe）
  - 各 idea 对应的 arena 数据与信号产出（step 05 验收通过的，路径在 05-tracking.md 台账内）
- 产出：
  - 每个 idea 一份 `market-alpha/loop-artifacts/stages/07/preregistration-<idea-id>.md`（按模板冻结，回测代码运行前落盘）
  - 每个 idea 一份 `market-alpha/loop-artifacts/stages/07/backtest-<idea-id>.md`（回测报告：OOS 窗口结果 / BH-FDR 后显著性 / DSR / MDD 跨窗口一致性 / 失败判据逐条对照）
  - `market-alpha/loop-artifacts/stages/07/07-backtest-summary.md`（汇总表：idea × 判据通过数 × 最终结论 {有效 / 无效 / 部分有效}）

## 做法
1. **预注册冻结（先写后跑，硬序）**：对每个 idea 填 `preregistration-template.md` 全字段（阈值先验圆整值、互不重叠年度 OOS 窗口 + 至少一段强制危机/熊市窗、费率 + 滑点、方向映射、trial count 起始 = 0），commit + push 后再允许运行回测代码。冻结后任何「跑不过就换阈值」= 违规，新增一律计入 trial count 并触发 DSR 加严。
2. **无未来数据执行**：数据管道按 backtest-sop 防前视节执行——每个数据点核对发布戳 < 当前 T 期起点；成分股/样本用生效日当时值；未定版末根 bar 剔除；量级陷阱逐条过。管道脚本 + 数据 manifest（SHA 锁定）入仓，保证 bit-level 可复现。
3. **回测与多重检验**：按预注册窗口跑 walk-forward OOS；全部检验 p 值进 BH-FDR（α=0.05）；绩效按 DSR trial-count deflation 重算（trial count = 预注册检验数 + 事后新增搜索次数，全记录）；失败判据（Mesfin 五条 + PSR）逐条对照并写入报告。
4. **失败如实**：无效/不显著的 idea 与有效的一视同仁出报告（参照 D1 负结果报告先例格式：结论 + 关键数值 + 失败判据命中项），禁止只报通过项。部分有效（仅部分 regime/窗口显著）标注适用边界。
5. 全程 commit + push；回测代码 + 数据 manifest + 报告同仓，可复现定义 = 给定 manifest + 预注册 + 信号规则重跑结果 bit-level 一致。

## 验收标准（可机器检查）
1. 进入回测的每个 idea 有 preregistration + backtest 两份文件，且 preregistration 的 commit 时间早于 backtest 报告的 commit 时间（`git log` 可验时序）。
2. 每份 preregistration 的 5 个字段（阈值 / OOS 窗口 / 成本 / 方向映射 / trial count）无空值，且标注「先验圆整值，非样本内拟合」。
3. 每份 backtest 报告含 4 项关键数值：BH-FDR 后显著检验数 / DSR deflate 后值 / MDD 跨窗口一致性 / 失败判据通过条数（Mesfin+PSR 逐条列出）。
4. `07-backtest-summary.md` 行数 = 回测 idea 数，每行结论 ∈ {有效, 无效, 部分有效}；「无效」行对应报告存在且含关键数值（无空报告）。
5. 数据 manifest 文件存在且含 SHA 清单；回测脚本入仓（`git -C market-alpha ls-files` 可查）。