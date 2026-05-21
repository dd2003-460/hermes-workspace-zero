---
name: Iteration 80 — Round 7 审查修复：3 Critical + 5 Should-fix
description: 修复 Prop 4.8 Δr_s 下界、Thm 1.4 KL 假设、universal 矛盾、章节编号等
type: reference
---

## iteration 80 结果

### Round 7 审查核心发现（agent a484cbbe6d75faac9）

3 个 Critical Issues：
1. Prop 4.8 下界缺失 Δr_s 贡献 — 修复：显式计算 ∂h_tt/∂r_s，使用 R² 梯度非零均值定理
2. Thm 1.4 假设 δ = KL 散度 — 修复：定理前提增加假设"δ 由观测空间的散度函数产生"
3. Abstract "universal" vs "different universality classes" — 修复：
   - Abstract: "universal" → "structural universality"
   - 统一框架 Sec 1: 区分框架模式的 universal 与临界指数的 universality
   - Sec 9.1: α 从 "2-categorical invariant" → "reflects structural properties"
   - EMRI-D26 映射: α ∈ (1,2) → 分别说明 D1 (1.84) 和 EMRI (0.5)

5 个 Should-fix：
A. 定义 4.5 添加 η 非标准范畴说明
B. Fisher-Rao 唯一性对非统计例子的过度声称 — 添加限定
C. EMRI-D26 映射论文章节编号错误 — Section 8(文献关联)/8(Paper II)/9(待完成) → 9/10/11
D. Thm 5.2 Schwarzschild 点歧义 — 明确 "r_s = r_s* > 0 fixed"
E. α 作为 invariant 矛盾 — 统一框架 Sec 9.1 重述

### LaTeX 转换产物
- papers/latex-pandoc-convert/ — 统一框架 + EMRI 证明的 pandoc 自动转换
- 统一框架：13 页，零错误
- EMRI 证明：14 页，零 warning

### arXiv 提交状态
- D1-grav-waves: 编译通过，tarball 127K，清单 11/11 pass
- DistCat: 4 篇论文全部修复，需 LaTeX 转换后才能提交（或作为 markdown 提交到 math.CT）

### 下一步
- 选项 1：DistCat 作为 markdown 提交到 arXiv（arXiv 接受 markdown 吗？不接受，必须 LaTeX/PDF）
- 选项 2：将 4 篇 markdown 论文手动转换为 LaTeX（高工作量）
- 选项 3：使用 pandoc 自动转换 + 手动修复（约 5-8 轮 iteration）
- 选项 4：作者决定如何处理 DistCat 提交（可能与 D1-grav-waves 合并或单独提交）
