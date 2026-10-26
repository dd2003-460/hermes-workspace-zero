# Step 05: GPU 子模块 arena 任务书（方法论+模型+tex+PDF 全外包）

## 目标
撰写 GPU 价格预测子模块的 arena 任务书，把方法论整理、模型实现、tex 报告、PDF 编译全部外包给 arena 在仓库内走 1-loop 完成。本地不做这些执行工作。

## 涉及文件
- `market-alpha/tasks/T1-gpu-price-model.md`（任务书，≤50 行）
- 推送后 arena 将产出：
  - `gpu-price-prediction/docs/methodology.md` + `docs/assumptions.md`
  - `gpu-price-prediction/src/`（config/tco/model/backtest/main）
  - `gpu-price-prediction/outputs/round-1/`
  - `gpu-price-prediction/reports/report.tex` + `report.pdf` + `figures/`

## 做法
任务书内容（顶部强制段 + 任务本体）：
```
【执行前必读】
1. 本任务必须走 1-loop：先读 sop/arena-loop-pipeline.md + loop/prompt-first/00-common-review.md + 01..04.5。
2. 每阶段产出落盘 loop-artifacts/stages/<N>/，阶段判定 pass 才进下一阶段。
3. 完成后 commit + push（含全部 loop-artifacts/）。
4. 通道故障 → 报告 Lead，不得静默跳过 loop。

【任务 T1：GPU PRO 系列专业卡价格预测模型】
数据源：gpu-price-prediction/data/arena-session-raw.md（已移植的 arena 会话，含 TCO 计算与价格平衡讨论）
要求：
1. 从 data/ 会话整理完整方法论（docs/methodology.md）：预测目标/卡型口径/TCO 公式与参数/价格预测方法/轮次机制，假设逐条列 assumptions.md（来源+置信度）
2. 用 Python 实现模型（src/）：TCO 计算 + 价格预测 + 历史轮次回测胜率；轮次用 outputs/round-N/ 区分；仅标准库+numpy/pandas
3. 跑通 round-1 预测（outputs/round-1/predictions.json + summary.md）
4. 写 LaTeX 技术报告（reports/report.tex）并编译 PDF：摘要/问题定义/数据/方法（TCO 公式推导）/假设表/结果（round-1+回测）/局限与后续轮次；含 ≥2 张 matplotlib 图；中文用 xelatex+ctex（环境缺失则装 tectonic 或改英文）
5. 报告标注 round-1 版本，预留修订记录节
验收：predictions.json 结构完整；TCO 对 ≥3 卡型可复算；report.pdf 编译成功零 error、>100KB
```
1. 写任务书 → commit + push → `git log -1 -- tasks/T1-gpu-price-model.md` 验证（断点 B）

## 验收标准
- [ ] T1 任务书含强制段 4 条 + 任务 5 步 + 验收标准
- [ ] 任务书已 commit + push（断点 B 过）
- [ ] 任务书 ≤50 行
