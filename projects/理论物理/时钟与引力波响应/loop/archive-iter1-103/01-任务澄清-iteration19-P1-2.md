# 1-loop/01 任务澄清 — Iteration 19: P1-2 三角探测器网络的手征 ORF

## 背景
- 论文 v17 已编译通过（53 页，无 error）
- 所有已知 bug 已修复（天线方向图 bug, helicity flip, 空间相位, 倾斜探测器）
- Iter36 手征 ORF 解析推导 (7/7 PASS)
- Iter80 helicity flip 对称性数值验证 (4/4 PASS)
- paper v17 已加入 §3.5.6 倾斜 LISA×Taiji 结果 (Γ^V ≈ 7.75e-3)
- `ralph-loop.local.md`: NO_FURTHER_WORK: true

## 当前阻塞任务 (task-decomposition-v2)
P0-2, P0-3, **P1-2**, P1-3, P2-2, P2-3 — 均为分析/理解类工作

## 本轮选择: P1-2

### 任务描述
编写 `note/P1-2-chiral-orf-triangular.md`，涵盖：
1. **Gamma^V 的数学定义和物理含义** — 奇宇称 ORF 从 Hu 通用框架的推导
2. **平面三角探测器 Γ^V = 0 的镜面对称性严格证明** — 基于反射对称性
3. **非共面构型 Γ^V ≠ 0 的条件** — 倾斜角与 Γ^V 的关系
4. **与已有代码/结果的对应** — `scripts/10-olc-chiral-orf-triangular.py` 和 Iter36/80 结果

### 完成标准 (task-decomposition-v2 §质量标准)
- [ ] 原文引用至少 5 处公式/段落（Hu PRD, JCAP 2025）
- [ ] 推导至少包含 3 个中间步骤
- [ ] 物理直觉解释对每个关键公式
- [ ] 与项目已有工作的对比分析
- [ ] 至少 2 条自我提问和回答

### 参考文件
- `raw/PhysRevD.111.084065(1).txt` — Hu PRD 文本
- `raw/JCAP2025_Chiral.txt` — JCAP 手征论文文本
- `note/P-chiral-orf-analytical.md` — 已有手征 ORF 解析推导 (39KB)
- `note/P3-phase3-cross-comparison.md` — 三文献交叉对比
- `scripts/10-olc-chiral-orf-triangular.py` — 手征 ORF 计算脚本
- `paper/main-paper.tex` §3.5.4-3.5.6 — 已有论文内容

### 判定标准
1. 能回答 "Hu 框架中 Γ^V 的完整定义是什么？"
2. 能回答 "为什么平面三角 Γ^V = 0？反射对称性如何作用？"
3. 能回答 "非共面构型的几何条件是什么？"
4. 能回答 "P-chiral-orf-analytical.md 的推导与 Hu/JCAP 是否一致？"

---

## ⚠️ 等待人类确认
请审阅以上目标设定。
确认：在文件顶部写下 `CONFIRMED 1`（同意）或 `CONFIRMED 2` + 修改建议。
**AI 不可修改已确认区块中的任何内容。**
