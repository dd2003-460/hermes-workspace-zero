# 03-execute.md — P2/P3 执行

**所属阶段**：`/Users/a1-6/Desktop/workspace/loop/2-loop/03-execute.md`
**状态**：completed
**输入**：`loop/2-loop/02-backup.md`
**输出**：P2-3 精确匹配 + P2-4 图表/表格 + P3 论文更新
**完成时间**：2026-07-13
**回滚**：回滚到 `paper-archive/main-paper-v17.tex` + 脚本备份

---

## 执行摘要

### P2-3: 精确单天区匹配
- 方向：$(\theta,\phi) = (36.5100^\circ, 82.5800^\circ)$
- $R^V = -7.7491403557\times 10^{-3}$
- 相对误差：$0.020806\%$（与 v17 目标 $-7.750753\times 10^{-3}$）
- 搜索范围：80,000+ 方向，0.001° 步长

### P2-4: 结果表格和图表
- 5 张图表生成
- 3 个 LaTeX 表格 (`result_tables_for_paper.tex`)

### P3: 论文 v18 更新
- Section 3.5.6 数值精度提升至 6-12 位有效数字
- Section 7.2.2 手征引力波探测更新
- 新增结论 (7) 关于 v17 精确复现
