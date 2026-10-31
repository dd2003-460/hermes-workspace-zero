# Step 02 — 统一无未来回测框架（防过拟合护栏）

## 目标
把 D1-financial-market-analysis 已验证的三层防过拟合护栏提炼成 market-alpha 的共享回测 SOP，供后续所有子模块复用，保证"无未来回测 + 不过拟合"是系统级护栏而非单项目纪律。

## 涉及文件
- 只读对象：
  - `projects/金融/D1-financial-market-analysis/loop-artifacts/stages/03/r1/artifacts/t04-signal-spec.md`（PIT 时间戳规则 / regime 锁定 / 多重检验计划）
  - `projects/金融/D1-financial-market-analysis/loop-artifacts/stages/03/r1/artifacts/t05-data-pipeline-design.md`（量级陷阱表 / 未定版末根禁用 / 成本参数预注册）
  - `projects/金融/D1-financial-market-analysis/loop-artifacts/stages/03/r1/artifacts/t06-backtest-design.md`（walk-forward / Mesfin 五条 + PSR / BH-FDR + DSR deflation）
  - `projects/金融/D1-financial-market-analysis/loop-artifacts/stages/04/r1/t06-preregistration-04r1.md`（预注册模板实例）
- 产出：
  - `market-alpha/backtest-sop.md`
  - `market-alpha/preregistration-template.md`

## 做法
1. 从 t04/t05/t06 提炼四层护栏，逐层写明规则 + 反例：
   - 防前视：所有数据点必须「发布戳 < T 期起点」；量级陷阱（秒→ms、µs→ns 换算）；未定版末根 bar 禁用；成分股用生效日当时成分。
   - 预注册：回测启动前冻结阈值（先验圆整值，禁止样本内挑选）、OOS 窗口、成本参数（费率 + 滑点）、方向映射；事后新增计入 trial count 并 DSR 加严。
   - 多重检验修正：BH-FDR（α=0.05，正相关检验家族适用）+ DSR trial-count deflation（arXiv:2608.27734）。
   - 失败判据：Mesfin 五条 + PSR + MDD 跨窗口一致性；regime 日历锁定禁止样本内再估计。
2. 把 t06-preregistration-04r1.md 抽成字段化模板：`preregistration-template.md`（阈值 / 窗口 / 成本 / 方向映射 / trial count 起始值）。
3. 交叉对照 t04/t05/t06 原文，确认每条护栏都有出处文件 + 行号，不发明新判据、不丢判据。

## 验收标准（可机器检查）
1. `market-alpha/backtest-sop.md` 存在，含 4 个章节（防前视 / 预注册 / 多重检验 / 失败判据）。
2. 每个判据条目都标了来源（`t04-signal-spec.md` / `t05` / `t06` / `preregistration` 之一）。
3. 预注册模板字段 ≥5 项（阈值、OOS 窗口、成本、方向映射、trial count）。
4. 原文关键判据抽查 3 处（BH-FDR α=0.05、未定版末根禁用、DSR deflation）在 SOP 中均出现（grep 可验）。
5. git commit 落 market-alpha。