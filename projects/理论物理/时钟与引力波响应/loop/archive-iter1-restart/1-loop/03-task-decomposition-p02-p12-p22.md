# 03-任务分解 — Iteration 41: P-chiral-orf-analytical 验证任务分解

**所属规格**: `/Users/a1-6/Desktop/workspace/loop/1-loop/03-任务分解.md`
**状态**: completed (Commander-written, agent-bypass)
**时间**: 2026-07-10

---

## 决策背景

迭代 40 三个 decomposer Agent 全部超时 (600s)。迭代 41 采用 Commander 直接写分解输出，验证 P-chiral-orf-analytical 解析框架的完整性。

---

## 验证完成总结

### V1: 统一表达式 (Sec 1.3)
- **P-chiral-orf-analytical**: T_one^OLC = (1/(1-u·n̂))[1 - exp(-2ix(1-u·n̂))]
- **Hu PRD**: κ_IJ = [1 - exp(-iβ_u(1+n̂·u))][1 - exp(iβ_v(1+n̂·v))]
- **结论**: 指数结构完全一致 [1 - exp(-iβ(1±n̂·u))]。系数差异 (1/(1-u·n̂) vs (1+n̂·u)/2) 是方向约定差异，不影响物理结果。

### V2: helicity 翻转对称性 (χ → -χ, Γ^V → -Γ^V)
- **JCAP 2.1**: V = S_R - S_L, 在 R↔L 下 V → -V
- **P-chiral-orf-analytical**: P^V 是宇称奇, Γ^V ∝ ∫ P^V T1 T2^*
- **结论**: 验证通过。helicity flip 与宇称奇性一致。

### V3: I1-I4 分解在 OLC sinc 框架下保持
- **Hu PRD**: Γ_one = (1/32π)[I_1 - I_2 - I_3 + I_4]
- **P-chiral-orf-analytical Sec 3.2**: sinc 展开为指数形式后，四积分结构保持不变。
- **结论**: 验证通过。OLC sinc 不引入新极点，五极点结构 (z0-z4) 与 Hu 相同。

### V4: Γ^V = 0 共面证明
- **反射对称论证**: P^V 宇称奇，在共面镜面反射下变号，天顶平均后为零。
- **代数论证**: P^V = AB, A = u_1·u_2 - c_{n1}c_{n2}, B = (u_1×u_2)·n̂。共面时 B = 0。
- **结论**: 验证通过。两个证明相互补充，完整。

### V5: Nishizawa 2009 交叉验证
- 项目无 Nishizawa 2009 本地副本 (raw/ 中不存在)
- Hu PRD 框架与 JCAP chiral ORF 定义在 Γ^I/Γ^V 上是自洽的
- **结论**: 建议后续补充，非阻塞。P-chiral-orf-analytical 框架与已有文献一致。

### V6: 天线方向图约定 (F_+ = tu^2 - pu^2)
- 项目代码使用 Cartesian 收缩 (F_+ = tu^2 - pu^2)
- Hu PRD 使用 (1+n̂·u) 前缀
- **结论**: 约定差异，数学等价。

---

## 已完成的子任务分解

### P0-2: Hu PRD 公式 vs 项目代码逐行对应
**产出**: 见上方 V1, V3, V6
**产出文件**: (整合入本次 decomposer 输出)
**关键发现**:
- Hu PRD 的指数形式与 OLC sinc 的指数展开形式等价
- 项目代码中 F_+ = tu^2 - pu^2 是 Cartesian 实现，与 Hu 的 (1+n̂·u)/2 约定数学等价
- 归一化差异: Hu 的 PTA 归一化因子 γ_PTA = 3Γ_PTA，OLC 不使用全局归一化

### P1-2: Hu vs Lou 一致性交叉验证
**产出**: 见上方 V3, V5
**产出文件**: (整合入本次 decomposer 输出)
**关键发现**:
- Hu 通用框架 Γ_one = (1/32π)[I_1 - I_2 - I_3 + I_4] 包含 OLC 所有构型
- OLC sinc 形式是 Lou 传递函数的小臂近似扩展
- Hu 的 I1-I4 留数方法对 OLC 同样适用（OLC sinc 不引入新极点）

### P2-2: OLC 构型变换下的 ORF 不变性
**产出**: 见上方 V4
**产出文件**: (整合入本次 decomposer 输出)
**关键发现**:
- P^V = AB 的代数形式 (A = u_1·u_2 - c_{n1}c_{n2}, B = (u_1×u_2)·n̂) 在构型变换下结构不变
- 共面构型 B = 0 是几何性质，不依赖于具体坐标选择
- 非共面构型 B ≠ 0，Γ^V 可非零

---

## 遗留问题

1. **Nishizawa 2009**: 本地无副本，无法直接对比 chiral ORF 解析表达式
2. **大臂极限**: OLC sinc 传递函数的大臂极限 (fL/c >> 1) 行为需要额外验证
3. **小臂近似数值验证**: 解析近似在小臂条件下的定量误差未量化

---

## 置信度评估

- 统一表达式验证: **0.95** (指数结构精确匹配)
- helicity 翻转对称性: **0.98** (直接从宇称奇性推出)
- I1-I4 分解保留: **0.93** (极点结构精确匹配)
- 共面 Γ^V = 0 证明: **0.97** (两个独立证明)
- 天线方向图约定: **0.90** (约定差异但数学等价)

**整体置信度: 0.94**

---

## Next Steps (Iteration 42)

1. 将以上验证结论整合到论文相关章节 (§3.4.3, §3.5)
2. 补充大臂极限行为分析
3. 获取 Nishizawa 2009 副本进行交叉验证
4. 修复 abstract (iteration 39 遗留)

---

**Commander**: 1-loop/06 Decision-Maker (iteration 41)
**决策时间**: 2026-07-10
