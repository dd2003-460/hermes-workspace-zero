# Step 01 — 资产盘点与融合决策

## 目标
建 goal（按 goal-template 五字段），并盘点 workspace 全部金融研究资产，产出融合决策：哪些仓库的资产并入 market-alpha、以什么形式（复制/引用/合并），落盘为 `market-alpha/tasks/fusion/00-asset-inventory.md`。

## 涉及文件
- 只读盘点对象：
  - `market-alpha/`（README/INDEX/loop-artifacts/tasks/gpu-price-prediction/transformer-sector-valuation）
  - `projects/金融/quant-capital-flow/`（tasks/stage02 17 个已核数据源 source-01~17、tasks/stage03/toy-model、tasks/state.md、memory/）
  - `projects/金融/D1-financial-market-analysis/`（loop-artifacts/stages 预注册+回测模板、TASKS.md 负结果）
  - `projects/AI-计算科学/D1-academic-AI/papers/D23-kinetic-theory-market-modeling.md`（5 命题+4 协议）
- 新建：`market-alpha/tasks/fusion/00-asset-inventory.md`
- 参考：`agents/goal-template.md`（§1 五字段）、`market-alpha/README.md`（子模块惯例）

## 做法
1. 按 goal-template 执行：create_goal（【目标】【阶段】【SOP 索引】→ arena-loop-pipeline 链路【验收标准】→ 可机器检查项）→ get_goal 验证落库。
2. 逐仓库盘点，每仓记录：现状、完成度、可复用资产（具体文件路径）、融合建议（复制进 market-alpha / 保留原位引用 / 合并改造）。
   - quant-capital-flow：stage02 17 个数据源核验文档（G4 矩阵）→ 复制为 market-alpha 数据契约底稿；toy-model 十五连败教训（3 策略+1 核框架不够，是结构不是参数问题）→ 作为设计反例引用，不复制代码。
   - D1-financial-market-analysis：预注册模板、t06-backtest-design（BH-FDR/DSR/PSR/Mesfin 五条/walk-forward）、负结果报告格式 → 复制到 market-alpha 作为回测 SOP 底稿。
   - D23 论文：5 命题+4 实验协议 → 作为 kinetic 模块理论底稿引用。
   - market-alpha 既有两模块：transformer 的产业链因果链分析（供需→信息→meme→资金流→股价）、gpu 的分群体供需动态 → 作为 supply-chain 模块方法学底稿。
3. 融合决策：主系统 = market-alpha 仓（git 远端可 push，loop 骨架齐），新增 3 个子模块：`kinetic-capital-flow/`（气体动理论资金流）、`supply-chain-forecast/`（产业链供需预测）、`regime-game-strategies/`（不同背景资金博弈策略）；原 quant-capital-flow 与 D1 仓保留原位，标注为"资产已融合，进入维护模式"，不删除任何探索过程（AGENTS.md 红线 0）。
4. 写 00-asset-inventory.md：资产表（路径+状态+融合方式+去向）+ 决策理由 + 子模块规划表（目录结构按 market-alpha 惯例：data/ src/ docs/ reports/ outputs/ + README）。
5. market-alpha 仓 commit（本地；不 push，push 在 step-06/07 随 arena 流程做）。

## 验收标准
- [ ] goal 已创建且 get_goal 回读确认（objective 含完整链路规则）。
- [ ] `market-alpha/tasks/fusion/00-asset-inventory.md` 存在，资产表 ≥6 行，每行含 4 列（来源路径/现状/融合方式/去向），无空列。
- [ ] 3 个新子模块的目录规划（含各自 README 骨架）写进 inventory。
- [ ] 融合决策显式声明：不删除任何原仓文件（grep 文档确认"保留原位"字样）。
- [ ] market-alpha 仓 `git log -1` 出现本步 commit。