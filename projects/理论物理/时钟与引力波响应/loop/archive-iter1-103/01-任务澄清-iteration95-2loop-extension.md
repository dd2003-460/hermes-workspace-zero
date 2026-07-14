# 1-loop/01 任务澄清 — Iteration 95: 2-loop Extension

> 创建时间: 2026-07-12
> 来源: gap-analysis.json (iter36), confidence 0.85
> 状态: 待人类确认

## 背景

task-decomposition-v2 (P0-P4, 16 子任务) 全部完成。
gap-analysis 判定: 置信度 0.85 > 0.70 阈值, 可进入 2-loop 执行层。

但 gap-analysis 仍标记了 3 个 medium/low 影响项目需要在 2-loop 中补充:

## 待处理项目

### 1. 非共面 Gamma^V 解析验证 (Medium Impact)
- **维度**: 非共面 Gamma^V 解析表达式（超越小臂近似）
- **背景**: 当前代码使用小臂近似 (ka << 1) 计算 Gamma^V。非共面构型 (如 LISA-Taiji) 中空间相位因子 exp(-ik·Δx) 不可忽略。
- **已有基础**: Iter11 实现了空间相位因子, Gamma^V sky-avg=1.34e-5, sky-max norm=0.999939
- **缺失**: 超越小臂近似的一般网络 Gamma^V 解析表达式
- **验证方法**: 对非共面构型 (倾斜 LISA × Taiji, 夹角 θ) 解析计算 Gamma^V(θ), 验证与数值结果一致性

### 2. Helicity 翻转对称性数值交叉检查 (Medium Impact)
- **维度**: Helicity flip symmetry — χ→-χ under Γ^V→-Γ^V
- **背景**: 手征 ORF 的 helicity flip 对称性: Γ^V(χ) = -Γ^V(-χ)
- **已有基础**: Iter80 验证了 4/4 测试 PASS, 包含空间相位因子
- **缺失**: 在一般网络中 (非等边三角) 验证 χ→-χ 时 Γ^V→-Γ^V
- **验证方法**: 选取不等边网络 (不同臂长), 对同一组引力波参数计算 χ→-χ 的 Γ^V, 验证反对称性

### 3. Nishizawa 2009 交叉验证 (Low Impact)
- **维度**: 与 Nishizawa PRD 79, 082002 的 chiral ORF 结果对比
- **背景**: Nishizawa 2009 是最早系统研究 GW 手征探测的论文
- **缺失**: 将当前 Γ^V 结果与 Nishizawa 公式在相同构型下对比
- **验证方法**: 在 LISA 共面构型下, 对比两种公式的 Γ^V 数值, 应一致

## 目标

1. 对 medium 项目逐一产生可验证的解析或数值结果
2. 将置信度从 0.85 提升到 0.90+
3. 产出可以直接写入论文的结果

## 判定标准

- Medium 项目 1: 给出非共面 Γ^V 的 sky-averaged 解析表达式, 数值验证相对误差 < 5%
- Medium 项目 2: 在 3 个不同不等边网络构型下验证 helicity flip 反对称性
- Low 项目: 在 2 个标准构型下数值对比一致

## 确认状态

> ⚠️ 等待人类确认
> 请审阅以上目标设定和判定标准。
> 确认：在文件顶部写下 `CONFIRMED 1`（同意）或 `CONFIRMED 2` + 修改建议。
> **AI 不可修改已确认区块中的任何内容。**
