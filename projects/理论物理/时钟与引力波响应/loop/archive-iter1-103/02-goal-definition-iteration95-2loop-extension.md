# 1-loop/02 目标澄清 — Iteration 95: 2-loop Extension

> 创建时间: 2026-07-12
> 输入: gap-analysis.json (iter36), task-decomposition-v2

## 目标: 提升理论完整性置信度从 0.85 到 0.90+

### 子目标 1: 非共面 Γ^V 超越小臂近似
- **输入**: 当前代码 `scripts/01-olc-orf-solver.py` (含空间相位因子)
- **输出**: 非共面构型 sky-averaged Γ^V(θ) 解析表达式
- **验证**: 对 LISA-Taiji 构型 (夹角 θ=0, 30, 60, 90°), 解析 vs 数值相对误差 < 5%

### 子目标 2: 一般网络 Helicity flip 反对称性
- **输入**: 当前代码 + Iter80 验证框架
- **输出**: 3 个不等边网络构型的 χ→-χ 反对称性验证
- **验证**: |Γ^V(χ) + Γ^V(-χ)| / |Γ^V(χ)| < 1e-6 (数值误差范围内)

### 子目标 3: Nishizawa 2009 交叉验证
- **输入**: Nishizawa PRD 79, 082002 公式 (Eq. 23-25)
- **输出**: 2 个标准构型下的数值对比表
- **验证**: 两种方法数值差异 < 1%

## 产出文件

- `loop/2-loop/01-backup.md` — 执行前备份
- `loop/2-loop/02-execute.md` — 具体执行计划
- `loop/2-loop/03-verify.md` — 验证结果
- `note/iter95-2loop-extension.md` — 综合分析

## 确认状态

> ⚠️ 等待人类确认
> 请审阅以上目标设定。
> 确认：在文件顶部写下 `CONFIRMED 1`（同意）或 `CONFIRMED 2` + 修改建议。
> **AI 不可修改已确认区块中的任何内容。**
