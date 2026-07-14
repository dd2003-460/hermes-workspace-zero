# 01-任务澄清 — Iteration 40

**状态**: completed
**输入**: loop state (iter 36 COMPLETE), QC reports (P0-1/P1-1/P2-1), fork decision (iter 2)
**时间**: 2026-07-10

## 盘点

| 任务 | 产出文件 | QC | 状态 |
|------|---------|-----|------|
| P0-1 Hu PRD 理解 | note/P0-1-hu-prd-understanding.md | QC Iter1 PASS | DONE |
| P1-1 JCAP 手征物理 | note/P1-1-chiral-physics.md + appendix | QC Iter2 PASS | DONE |
| P2-1 OLC 原理 | note/P2-1-olc-principles.md | QC Iter2 PASS | DONE |
| P3 交叉对比 | note/P3-phase3-cross-comparison.md | — | DONE |
| chiral ORF 解析 | note/P-chiral-orf-analytical.md | 1-loop COMPLETE | DONE |

## 迭代 40 目标

基于 fork decision (P1-1+P2-1, 2026-07-08) 的建议，进入第二批子任务：

1. **P0-2**: Hu PRD 公式 vs 项目代码 (scripts/01-olc-orf-solver.py) 逐行对应
2. **P1-2**: Hu vs 楼明智一致性交叉验证（ORF 定义是否一致）
3. **P2-2**: OLC 构型变换下的 ORF 不变性（楼论文明证明 vs 我们理解）

**产出**: 三份理解笔记 + 一份交叉对比文档

## 收敛标准

- [ ] P0-2: 输出 note/P0-2-hu-vs-code-analysis.md，列出至少 5 处公式对应关系
- [ ] P1-2: 输出 note/P1-2-hu-lou-consistency.md，回答 "Hu 框架是否包含 OLC ORF？"
- [ ] P2-2: 输出 note/P2-2-olc-invariance.md，完整复现楼论文构型变换证明

## 并行策略

三个任务互相不依赖，可并行派发。
