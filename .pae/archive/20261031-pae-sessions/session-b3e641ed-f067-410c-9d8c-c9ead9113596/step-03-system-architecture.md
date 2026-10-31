# Step 03 — market-alpha 系统架构与 SOP 定义（含博弈策略设计）

## 目标
把「气体动理论资金流 + 产业链供需预测 + 不同背景下的资金博弈策略 + 无未来回测」整合为 market-alpha 的系统 SOP 架构：定义 3 个新子模块的边界、数据契约、博弈策略框架，并更新 `tasks/decomposition.md` 分解树。这是 arena 派活前的「01 目标分解」产出，也是用户「整合成系统 SOP」要求的核心落点。

## 涉及文件
- 只读对象（输入素材）：
  - `projects/AI-计算科学/D1-academic-AI/papers/D23-kinetic-theory-market-modeling.md`（5 命题 + 4 实验协议 D23-A/B/C/D）
  - `projects/金融/quant-capital-flow/tasks/state.md`（toy model v5-v15 十五连败教训：3 策略+1 核框架不够，F/M 恒胜 S 是结构问题）
  - `market-alpha/transformer-sector-valuation/data/yuanbao-session-raw.md`（生产链供需→盈利分布→拥挤度→资金流→价格 的因果链 + 「12 个月尺度 meme 层主导、长周期生产链主导」的期限结论 + 资金流守恒假设）
  - `market-alpha/gpu-price-prediction/data/arena-session-raw.md`（分群体供需动态：个人/企业供需、供给情景推演）
  - `market-alpha/backtest-sop.md`（step 02 产出，回测护栏引用）
- 产出：
  - `market-alpha/SOP.md`（系统 SOP：子模块接入 → 数据契约 → 预注册 → 无未来回测 → 博弈策略 → 胜率记录 全流程）
  - `market-alpha/tasks/decomposition.md` 更新（分解树：3 新子模块 × 原子任务 × 依赖 × 正交性核对）
  - 三个子模块 README 骨架（`kinetic-capital-flow/README.md`、`supply-chain-forecast/README.md`、`regime-game-strategies/README.md`，只写定位+数据契约+验收口径，不写实现）

## 做法
1. **子模块划分（正交性核对）**：
   - M1 `kinetic-capital-flow`：气体动理论研究资金流动。输入 = D23 的 5 命题 4 协议 + quant-capital-flow stage02 已核 17 数据源（北向/两融/ETF 申赎/大宗/主力/机构持仓 13F 等，源清单在 `projects/金融/quant-capital-flow/tasks/stage02/source-*.md`）+ toy model 教训（不重蹈 3 策略+1 核覆辙，策略层先做实证归因）。正交性：只管「资金流的统计物理刻画 + 可证伪命题」，不管产业链基本面。
   - M2 `supply-chain-forecast`：产业链供需预测。输入 = transformer 子模块已验证的因果链（供需平衡表→价格→量价→利润率→盈利分布）+ gpu 子模块的分群体供需情景方法 + 产业链事件信号（招标/核准/出口/产能，yuanbao 会话已确认是合法 edge）。正交性：只管「产业侧供需→板块基本面」，资金流层交 M1，策略层交 M3。
   - M3 `regime-game-strategies`：各自资金在不同背景下博弈策略。输入 = regime 日历锁定（D1 t04）× 策略类型（趋势 M / 跟风 F / 聪明钱 S，沿用 toy model 命名）× 「信息不完备参与者博弈」框架（yuanbao：内行信息差 vs 大资金速度）。正交性：只管「给定信号，不同 regime 下选什么策略、仓位如何」，信号生产交 M1/M2。
   - 空缺清单（decomposition 必填）：M1 与 M2 的接口（供需→资金流的传导系数）暂无数据支撑 → 标 candidate，不阻塞；M3 的「聪明钱策略」缺持仓数据（D1 缺口清单已记：北向/两融/机构季度变动）→ 依赖 stage02 数据管道。
2. **数据契约**：每个子模块的 README 骨架里写死：数据源清单（引用 quant-capital-flow stage02 的 source-*.md 编号）、发布戳纪律（复用 quant-capital-flow README 红线 1 原文：预测 T 期只能用发布戳 < T 起点的）、单位换算陷阱表（引用 t05 量级陷阱表）。
3. **SOP.md 主文档**：按 goal-template 六阶段写 market-alpha 级流程（子模块接入模板 / 预注册冻结流程 / 回测验收口径 = 引 backtest-sop.md / 胜率记录规则 / arena 派活流程 = 引 sop/arena-loop-pipeline.md），不复制内容，只指路径。
4. 全部产出 git commit（不 push，随 step 04 统一 push）。

## 验收标准（可机器检查）
1. `market-alpha/SOP.md` 存在，含 ≥6 节（子模块接入 / 数据契约 / 预注册 / 无未来回测 / 博弈策略 / 胜率记录），每节有指向具体文件的相对路径引用（grep 可验）。
2. 3 个新子模块 README 骨架存在，每个含 4 段（定位 / 数据源与发布戳纪律 / 验收口径 / 正交边界）。
3. `tasks/decomposition.md` 含分解树：3 子模块 × 每模块 ≥3 个原子任务 × 依赖关系 × 空缺清单（≥2 条，标注 candidate/不阻塞）。
4. 正交性核对表存在：每对子模块（M1-M2 / M1-M3 / M2-M3）一行「共同职责 = 无，接口 = X」。
5. 与 goal-template 流程对齐声明：SOP.md 顶部注明走 arena 外包链路（`sop/arena-loop-pipeline.md`）。