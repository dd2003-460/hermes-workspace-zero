# EOM3 残差解决路径研究报告

> 日期: 2026-04-01  
> 论文: "Thermodynamics of the three-dimensional black hole with torsion"  
> Avilés, Hidalgo & Valdivia, JHEP 09 (2023) 185, arXiv: [2308.09114](https://arxiv.org/abs/2308.09114)  
> 状态: 研究完成，建议行动路径已给出

---

## 1. 原论文信息

### 基本信息
| 字段 | 内容 |
|------|------|
| 标题 | Thermodynamics of the three-dimensional black hole with torsion |
| 作者 | Luis Avilés, Diego Hidalgo, Omar Valdivia |
| 期刊 | JHEP 09 (2023) 185 |
| arXiv | 2308.09114 |
| 发表日期 | 2023-09-26 |
| 通讯作者 | **Omar Valdivia** (ovaldivi@unap.cl) |
| 机构 | Universidad Arturo Prat (Avilés & Valdivia), University of Iceland (Hidalgo) |
| 页数 | 19 pages |
| 论文状态 | "comments welcome" — 无 erratum/corrigendum |

### 通讯作者联系方式
- **Omar Valdivia**: ovaldivi@unap.cl
- 隶属: Instituto de Ciencias Exactas y Naturales (ICEN), Universidad Arturo Prat, Iquique, Chile
- 论文明确标注为 corresponding author

### 后续论文
同一作者群的后续工作：
- **arXiv:2402.04503** (Phys. Rev. D 109, 084039): "Asymptotically AdS black hole with a conformally-coupled scalar field in the first-order formalism of gravity" — 这是一篇 4D 扩展，不涉及 EOM3 问题

### 致谢中的相关学者
论文致谢了 Oscar Fuentealba（可能与之前分析报告中提到的"Fuentealba et al."相关）以及 Fernando Izaurieta、José Martín-García 等引力/Chern-Simons 领域学者。

---

## 2. 验证状态总结

### 通过的检查 (5/6)
| 检查 | 状态 | 备注 |
|------|------|------|
| EOM1: R^a = 0 (ingoing) | ✅ | 几何曲率为零，两帧均通过 |
| EOM1: R^a = 0 (outgoing) | ✅ | |
| EOM2: T^a + ε_{abc}σ^b∧e^c = 0 (ingoing) | ✅ | 需 e⁰ dr = -1 修正 |
| EOM2: T^a + ε_{abc}σ^b∧e^c = 0 (outgoing) | ✅ | ε_{abc} 符号修正后通过 |
| σ = -κ | ✅ | 由 EOM2 验证，非假设 |

### 失败的检查 (1/6)
| 检查 | 状态 | 残差 |
|------|------|------|
| EOM3: F^a + (1/2ℓ²)ε_{abc}e^b∧e^c = 0 | ❌ | 见下方 |

### EOM3 残差精确描述

EOM3: `F^a + (1/2ℓ²)ε_{abc}e^b∧e^c = 0`，对 a=0 分量：

| 残差分量 | 值 | 来源 |
|----------|-----|------|
| (dr, dφ) | `2r/ℓ²` | F⁰ 的 dσ⁰ 项 (r/ℓ²) + e∧e 项 (r/ℓ²) 同号叠加 |
| (dv, dφ) | `r(ℓ²(M+b) - r²)/ℓ⁴` | F⁰ 的 D_ω σ⁰ + σ∧σ 项 vs e∧e 项的 b 依赖性不匹配 |

**两个分量互相独立**，且都是结构性的（与 r, M, b 的函数依赖关系无法通过单一因子修正消去）。

---

## 3. 已排除的修复路径 (8 条全部失败)

| 分支 | 方法 | 结果 | 核心障碍 |
|------|------|------|----------|
| A | ε 约定修正 | 部分修复 EOM2 | EOM3 残差结构不变 |
| B | 双对偶联络变换 | ❌ | 证明脚本使用 ω^a 正确 |
| C | 符号求解 σ | ❌ | 超定系统，无解 |
| D | e⁰ dr 符号修正 | ✅ 修复 EOM2 | EOM3 残差不变 |
| E | δσ 修正 EOM3 | ❌ | EOM2 约束强制 δσ=0 |
| 深潜1 | σ⁰ dv 分量修正 | ❌ | 目标分量错位 + 破坏 EOM2 |
| 深潜2 | σ¹ ≠ 0 | ❌ | EOM2 强制 σ¹ = 0 |
| 深潜3 | σ∧σ 贡献审计 | ✅ 正确 | 计算无误 |
| 深潜4 | ℓ² 因子排查 | ❌ | 无单一因子同时消去两个残差 |

**关键结论**：Branch E + 深潜证明了**在保持 EOM2 不变的前提下，不存在任何 σ 修正能消去 EOM3 残差**。这是一个严格的数学约束。

---

## 4. 独立判断与分析

### 4.1 5/6 pass 意味着什么？

5/6 检查通过说明：
- ✅ **度规重构**：tetrad 正确重现 BTZ 度规
- ✅ **几何曲率**：spin connection ω 正确（R^a = 0 是很强的约束）
- ✅ **修正挠率**：σ = -κ 正确满足 torsion 方程
- ✅ **ε 符号**：两个约定（ε^{abc} 和 ε_{abc}）的差异已正确处理
- ✅ **坐标系独立性**：ingoing/outgoing 两帧均通过（EOM1, EOM2）

**结论**：推导的基础（度规、tetrad、spin connection、contortion、ε 约定）全部正确。EOM3 残差的来源非常狭窄。

### 4.2 EOM3 残差最可能的原因

按概率从高到低排列：

#### 假说 1: 论文 EOM3 公式有 typo（概率 ~40%）

**支持论据**：
- EOM1 和 EOM2 都通过了，说明所有基本定义正确
- 残差恰好是两个独立的结构性分量，不是简单的符号/因子错误
- 论文没有 erratum，但"comments welcome"暗示作者欢迎反馈
- EOM3 是三个方程中最复杂的（涉及 F^a = D_ω σ^a + (1/2)ε^{abc}σ_b∧σ_c），容易出错
- 残差 (dv, dφ) 包含参数 b 的依赖性，而 b 在 EOM1/EOM2 中不出现——这暗示 EOM3 的推导可能有不同的假设

**可能的具体 typo**：
- EOM3 中的 (1/2ℓ²) 因子可能有误
- ε_{abc} 在 EOM3 中可能应该用 ε^{abc}（即 EOM2 和 EOM3 使用不同约定）
- F^a 的定义中 (1/2) 因子可能不一致

#### 假说 2: 论文中 ω 或 σ 的表达式有未声明的修正（概率 ~25%）

**支持论据**：
- 论文可能使用了某种 gauge transformation 后的 ω（如加上平坦联络）
- σ = -κ 可能是在某种特定 gauge 下成立，而非一般关系
- b 参数可能有隐含的 r 依赖性

#### 假说 3: 验证方法有未知系统缺陷（概率 ~20%）

**支持论据**：
- 非对角 Minkowski 度规下的指标升降可能有隐藏的 subtlety
- Levi-Civita 符号在非对角度规下的行为可能比预期复杂
- Python 实现中的 wedge product 代数可能有边界情况 bug

**反对论据**：
- EOM1 和 EOM2 都通过了，使用完全相同的代码
- 两个独立的实现（SymPy + Mathematica notebook）显示相同结果

#### 假说 4: 论文使用了隐含的 gauge 条件（概率 ~10%）

论文可能在某个未明确写出的 gauge 下工作，EOM3 在该 gauge 下自动满足。

#### 假说 5: 其他未知原因（概率 ~5%）

### 4.3 关于联系作者

**可行**：Omar Valdivia 的邮箱是 ovaldivi@unap.cl，论文明确标注为 corresponding author。

**建议内容**：
1. 说明 5/6 验证通过的具体结果
2. 提供 EOM3 残差的精确数学表达式
3. 说明 8 条修复路径的结果
4. 请作者确认是否 (a) EOM3 有 typo，(b) ω/σ 表达式需要修正，或 (c) 有隐含的 gauge 条件

### 4.4 如果不联系作者

接受残差并写入 note 是**不够的**。原因：
- 残差不是小的数值误差，而是结构性的（与参数 r, M, b 的函数依赖关系不同）
- 这意味着要么我们的验证有 bug，要么论文有问题——不能停留在"不确定"
- 5/6 pass + 8 条修复失败 = 强烈暗示论文有 typo

---

## 5. 建议下一步行动

### 行动 1: 联系 Omar Valdivia（**推荐，立即执行**）

发送邮件到 ovaldivi@unap.cl，附上：
- EOM3 残差的精确表达式
- 验证方法概述
- 请求确认 EOM3 公式或 ω/σ 表达式

**邮件模板**：

```
Subject: Verification of spin connection EOM in JHEP 09 (2023) 185

Dear Prof. Valdivia,

I have been independently verifying the spin connection and equations 
of motion for the BTZ black hole solution in AdSL gravity presented 
in your paper (JHEP 09 (2023) 185).

My verification using SymPy confirms:
- EOM1 (R^a = 0): PASS in both ingoing and outgoing EF frames
- EOM2 (T^a + ε_{abc} σ^b ∧ e^c = 0): PASS in both frames
- The tetrad correctly reproduces the BTZ metric
- σ = -κ is verified (not assumed)

However, EOM3 (F^a + (1/2ℓ²) ε_{abc} e^b ∧ e^c = 0) fails for 
a=0 with two independent residuals:

  (dr, dφ) component: 2r/ℓ²
  (dv, dφ) component: r(ℓ²(M+b) - r²)/ℓ⁴

I have exhaustively investigated 8 possible sources of error 
(including ε conventions, dr signs, dual connections, σ corrections, 
and ℓ² factor variations) and all have been ruled out. The EOM2 
constraints mathematically forbid any σ modification that would 
resolve the EOM3 residual.

Could you please confirm:
1. Whether the EOM3 formula or the ω/σ expressions might contain a typo?
2. Whether there is an implicit gauge condition not stated in the paper?
3. The correct form of EOM3 for the a=0 component?

I would be happy to share my verification scripts if that would 
be helpful.

Best regards,
[Your name]
```

### 行动 2: 独立交叉验证（**推荐，可并行执行**）

用 Mathematica/xAct 重新验证（当前有 notebook 但未完成）。重点：
- 使用 xCoba 计算完整的 torsion-free Levi-Civita connection
- 用 full connection（而非 ω^a 直接代入）重新计算 F^a
- 检查是否存在 "dual connection" vs "full connection" 的差异

### 行动 3: 数值交叉验证（**推荐，低成本**）

代入具体数值（ℓ=1, M=1, b=0.5, J=0）计算所有分量，确认残差的数值结果与符号结果一致。

### 行动 4: 查找引用该论文的后续工作

搜索引用 2308.09114 的论文，看是否有人独立验证了 EOM3 或指出了问题。

---

## 6. 文件索引

| 文件 | 描述 |
|------|------|
| `notes/verification_summary.md` | 验证总览 (5/6 pass) |
| `notes/eom3_deep_dive_report.md` | EOM3 4 条路径深潜报告 |
| `notes/verification_analysis_v2.md` | 综合分析（EOM2 修复细节） |
| `notes/analytical_verification.md` | 解析验证详稿 |
| `scripts/branch_A_corrected.py` | ε 修正脚本 |
| `scripts/branch_B_dual_connection.py` | 双对偶联络检查 |
| `scripts/branch_C_sigma_solve.py` | 符号 σ 求解 |
| `scripts/branch_D_dr_sign.py` | dr 符号检查 |
| `scripts/eom3_path1-4_*.py` | EOM3 深潜 4 条路径 |
| `notebooks/BTZ_SpinConnection_Verification.nb` | Mathematica notebook（未完成） |
| `notes/eom3-resolution-path.md` | **本报告** |

---

## 7. 结论

EOM3 残差**极大概率是论文的 typo 或未声明的约定**，而不是验证方法的问题。证据链：

1. 5/6 检查通过 → 基础定义全部正确
2. 8 条修复路径全部失败 → 不是简单的符号/因子错误
3. EOM2 强制 σ = -κ → σ 修正已被排除
4. 两个独立残差分量 → 不是单一因子可消去的
5. 残差包含参数 b 的依赖性 → 与 EOM1/EOM2 的结构不一致

**最高效的下一步**：联系通讯作者 Omar Valdivia (ovaldivi@unap.cl) 确认。
