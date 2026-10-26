# Step 06: 变压器子模块 arena 任务书（方法论+模型+tex+PDF 全外包）

## 目标
撰写变压器板块估值子模块的 arena 任务书，把方法论整理、估值模型实现、tex 报告手册、PDF 编译全部外包给 arena 在仓库内走 1-loop 完成。

## 涉及文件
- `market-alpha/tasks/T2-transformer-valuation.md`（任务书，≤50 行)
- 推送后 arena 将产出：
  - `transformer-sector-valuation/docs/methodology.md` + `docs/assumptions.md`
  - `transformer-sector-valuation/src/`（config/valuation/decomposition/global_compare/main）
  - `transformer-sector-valuation/outputs/round-1/`
  - `transformer-sector-valuation/reports/report.tex` + `report.pdf` + `figures/`

## 做法
任务书内容（顶部强制段 + 任务本体）：
```
【执行前必读】（同 T1 强制段 4 条）

【任务 T2：A股变压器板块估值与全球对比模型】
数据源：transformer-sector-valuation/data/yuanbao-session-raw.md + report-attachment.md（已移植的元宝会话：1.5万字深度报告 + 正交分解/贡献因子框架讨论，数据截止 2026-10-26）
要求：
1. 从 data/ 整理方法论（docs/methodology.md）：覆盖标的（≥10 家 A 股）+ 海外对标组（GEV/ETN/VRT/Hitachi 等）/估值方法（PE-PS 分位+目标价）/贡献因子对数分解框架（盈利预期修正 vs 估值倍数压缩，如思源 -56.1% 案例）/五个核心判断；假设逐条列 assumptions.md（目标PE/EPS 预测/铜价硅钢路径等，来源+置信度）
2. 用 Python 实现（src/）：config 结构化财报行情数据 + 估值分位/目标价计算 + 贡献因子对数分解复算 + A股vs美股全球对比表；产出 outputs/round-1/valuation.json + summary.md；仅标准库+numpy/pandas
3. 复算校验：思源电气分解（估值压缩占比 81-85%）、金盘目标价区间 55-100 元、板块 PE 30.72/47.2% 分位须与源数据一致
4. 写 LaTeX 报告手册（reports/report.tex）编译 PDF：摘要（五核心判断）/问题定义与标的×维度矩阵/数据来源/方法论（含对数分解公式推导）/全球对比/个股结果（目标价表+分解案例）/假设与敏感性/数据缺口与后续轮次；≥3 张图；中文 xelatex+ctex
5. 报告标注 round-1 + 数据快照日期 2026-10-26，预留修订记录节
验收：main.py 跑通产出 round-1；思源分解复算与原文一致；目标价表 ≥8 家；report.pdf 零 error、>150KB
```
1. 写任务书 → commit + push → 验证（断点 B）

## 验收标准
- [ ] T2 任务书含强制段 + 任务 5 步 + 验收标准
- [ ] 任务书已 commit + push（断点 B 过）
- [ ] 任务书 ≤50 行
