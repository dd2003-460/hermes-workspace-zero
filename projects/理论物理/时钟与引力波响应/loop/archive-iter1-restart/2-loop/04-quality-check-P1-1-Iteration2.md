# P1-1 QC Iter2: 手征引力波的物理基础

- **QC 轮次**: Iter2（re-QC）
- **QC 对象**: `note/P1-1-chiral-physics.md` + `note/P1-1-appendix-normalization.md`
- **置信度**: 0.87
- **QC 状态**: **PASS**

## QC 来源: QC Iter1 要求

报告: `loop/2-loop/04-quality-check-P1-1-Iteration1.md`
置信度: 0.50，FAIL。四项失败：

1. **缺失归一化证明** (AC1): 附录无 |h_R|^2 + |h_L|^2 = |h_+|^2 + |h_×|^2 的代数验证
2. **Gamma^V 宇称奇性推导不完整** (AC2): 无完整从 e^P_{ab} 宇称变换到 mirror-symmetric 网络 Gamma^V=0 的推导链
3. **公式缺乏物理解释** (AC3): chi_orb(f) 为捏造公式，S^V = h_R^2 - h_L^2 量纲错误
4. **引用错误** (AC6): JCAP §3.1 应为 §3.2（eq. 3.3）

## Iter2 逐项验证

### AC1: 归一化证明 — PASS

附录 A.1-A.1.2（~55 lines）完整验证：

- **A.1**: |h_R|^2 = (|h_+|^2 + |h_×|^2 + i(h_+ h_×^* - h_× h_+^*)) / 2 — 展开验证
- **A.1.1**: |h_L|^2 = (|h_+|^2 + |h_×|^2 - i(h_+ h_×^* - h_× h_+^*)) / 2 — 展开验证
- **A.1.2**: Sum → cross terms cancel → |h_+|^2 + |h_×|^2 — 结论正确

附加验证 e^R_{ab}(e^R_{ab})* = 2（Hu PRD eq. 2）

### AC2: Gamma^V 宇称奇性完整推导 — PASS

附录 A.2（~65 lines）5步推导：

- **Step 1**: e^+_{ab}(-k̂) = e^+_{ab}(k̂) (偶), e^×_{ab}(-k̂) = -e^×_{ab}(k̂) (奇) — 给出 3×3 矩阵显式表示
- **Step 2**: Δ_{abcd}(-k̂) = -Δ_{abcd}(k̂) — Gamma^V 核函数宇称奇 — 矩阵运算验证
- **Steps 3-4**: 完整积分表达式在宇称变换下推导 — Jacobian = 1, k → -k, Δr → -Δr
- **Step 5**: Mirror-symmetric 网络 ⇒ Gamma^V = -Gamma^V ⇒ Gamma^V = 0 — 结论正确

### AC3: 捏造公式已移除，替换为 grounded 公式 — PASS

- **chi_orb(f) 已移除**，替换为 JCAP §2, eq. 2.6 的 chi(f) = (S_R - S_L)/(S_R + S_L)
- **S^V = h_R^2 - h_L^2 已移除**，替换为 S_R(f), S_L(f)（功率谱密度，量纲正确）
- 附录 A.3 新增 Seto PRL 97 151101 (2006)、Alexander PRD 74 024028 (2006)、Hu PRD 111 084065 (2025) 共 3 个非 JCAP 引用，对 chi(f) 频率依赖性进行物理分析

### AC4: 核心公式引用 — PASS

- main doc §5.2 eq. 2.9 (line 160): Gamma^I + Gamma^V 同时出现，交叉相关公式 ⟨s_i s_j^*⟩ = 1/2 delta(f-f')[Gamma^I I + Gamma^V V] — 与 JCAP §2.1 eq. 2.9 一致
- main doc §5.3 eq. 2.10 (line 167): 宇称奇 ORF 定义，e^+ e^× - e^× e^+ 组合 — 与 JCAP §2.1 eq. 2.10 一致
- main doc §2.1 eq. 2.3 (line 22): 张量基 e^R_{ab} = (e^+_{ab} + i e^×_{ab})/sqrt(2) — 与 JCAP §2 eq. 2.3 一致
- main doc §2.1 eq. 2.4 (line 27): 光应变 h_R = (h_+ - i h_×)/sqrt(2) — 与 JCAP §2 eq. 2.4 一致

### AC5: 推导链完整性 — PASS

- 附录 A.2 提供完整推导链，5 步从张量宇称变换到 Gamma^V = 0 结论
- main doc §5.3 提供 3 条物理直觉解释（宇称变换、几何三重积、可观测信号）

### AC6: 引用错误修正 — PASS

- main doc §3.1 line 102: JCAP §3.1 → **已修正为 JCAP §3.2**
- eq. 3.3 确实在 §3.2（能量密度定义）中

### AC7: 物理诠释 — PASS

- main doc line 81: "I正比于引力波的能量通量，而V正比于引力波角动量的手征部分" — Stokes 参数物理解释已添加
- main doc §5.3 对 Gamma^V 宇称奇性提供 3 条物理直觉
- main doc §4.1 列举 3 种宇称破坏宇宙学模型机制

### AC8-AC10: 其余检查 — PASS

- AC8: chi(f) 取值范围 [-1,1] 正确 — main doc §3.2
- AC9: Gamma^V 的探测条件（非共面探测器）正确 — main doc §5.1-5.3
- AC10: 与项目代码的关系讨论正确 — main doc §7

## 置信度评估

- **信心 0.87**（vs Iter1 的 0.50）
- 提升原因：五项子任务全部完成，捏造公式已移除，引用错误已修正，完整推导链已建立
- 保留不确定性：附录的矩阵计算虽正确，但未与 JCAP 原文逐行对照验证（原文无显式 3×3 矩阵）

## QC 结论

**P1-1 QC Iter2 PASS** — 可以进入 2-loop/05 置信度判断阶段。

## 参考文献

1. JCAP05(2025)050 — Circularly polarized SGWB search with triangular detector networks
2. Seto PRL 97, 151101 (2006) — Prospects for detection of circular polarization of GW background
3. Alexander PRD 74, 024028 (2006) — Chern-Simons modification of gravity
4. Hu PRD 111, 084065 (2025) — General ORF framework for PTA and interferometers
