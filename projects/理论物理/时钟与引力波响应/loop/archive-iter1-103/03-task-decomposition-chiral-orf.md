# 03-任务分解 — Iteration 32: 整合手征引力波计算解析 ORF

> **Decomposer Output**
> **Iteration**: 32
> **Phase Spec**: `/Users/a1-6/Desktop/workspace/loop/1-loop/03-任务分解.md`
> **Input**: `loop/1-loop/01-clarification.md`, `loop/1-loop/02-goal-definition.md`
> **Status**: completed
> **Last updated**: 2026-07-09

---

## 1. DAG 总览

```
ST1 (Hu I1-I4 + OLC sinc 统一推导)  ─┐
                                       ├──→ ST3 (验证脚本 + 代码实现) ──→ ST4 (全面验证)
ST2 (小臂近似解析推导)  ──────────────┘
```

- **ST1 和 ST2 可并行**（两个都产出数学笔记，互不依赖）
- **ST3 依赖 ST1**（代码实现需要统一公式）
- **ST3 不依赖 ST2**（解析代码可以在小臂近似完成之前实现通用的 Hu I1-I4 框架）
- **ST4 依赖 ST3**（验证需要代码完成）

---

## 2. 子任务定义

### ST1: Hu I1-I4 + OLC sinc 统一推导（Gamma^I 和 Gamma^V）

| 字段 | 内容 |
|------|------|
| **输入** | `note/P0-1-hu-prd-understanding.md`, `note/P1-1-chiral-physics.md`, `note/P2-1-olc-principles.md`, `note/P3-phase3-cross-comparison.md` |
| **输出** | `note/P-chiral-orf-analytical.md`（完整解析推导笔记） |
| **Agent** | general-purpose |
| **优先级** | P0 |
| **依赖** | None（与 ST2 并行） |
| **置信度** | 0.85（sinc 留数计算可能复杂） |

#### 具体物理任务

在 Hu PRD (111.084065) 的通用 ORF 框架下，将 OLC sinc 转移函数代入，重新推导 Gamma^I(f) 和 Gamma^V(f) 的 I1-I4 表达式。

**关键公式必须推导：**

1. **统一转移函数** — 展示 OLC sinc 如何替代 Hu 指数：
   ```
   T_one^OLC = (i2πfL/c) · sinc[(πfL/c)(1-n̂·û)] · exp[-i(πfL/c)(1-n̂·û)]
   ```
   与 Hu 的指数形式：
   ```
   T_one^Hu = (1+n̂·u)/2 · [1 - exp(-iβ(1+n̂·u))]
   ```
   **差异分析**：(a) prefactor 不同 — sinc 的 iβ vs Hu 的 (1+n̂·u)/2; (b) 函数形式 — sinc vs exponential; (c) 极点结构 — sinc 在原点有可去极点，Hu 无极点

2. **Gamma^I 的 I1-I4 表达式** — 显式写出：
   ```
   Γ^I_ij(f) = Σ_{k=1}^{4} c_k(f) · I_k + boundary_terms
   ```
   其中每个 I_k 的留数计算必须包含：
   - 极点的识别（z_0, ..., z_4）
   - 每个极点的留数（Residue at z_i）
   - 最终求和（Σ Res_i）

3. **Gamma^V 的 I1-I4 表达式** — 显式写出：
   ```
   Γ^V_ij(f) = Σ_{k=1}^{4} c_k^V(f) · I_k^V + boundary_terms
   ```
   其中 I_k^V 包含天线模式乘积 (F_i^+ F_j^× - F_i^× F_j^+)
   **必须展示**：交叉偏振项如何与 sinc 转移函数耦合

4. **极点分析** — sinc 函数的零点：
   ```
   sinc(x) = sin(x)/x = 0 when x = nπ (n=±1,±2,...)
   ```
   这些零点在复平面上是否产生新的极点？留数定理是否仍然适用？

5. **共面论证** — 显式证明 (n̂₁ × n̂₂)·d̂ = 0 ⇒ Γ^V = 0

#### 交付物格式要求

`note/P-chiral-orf-analytical.md` 必须包含：
- **至少 5 个编号公式**（从 (1) 到 (5)+，每个必须完整推导，不跳步）
- **Hu I1-I4 框架的留数计算** — 必须显式展示 5 个极点的留数求和
- **OLC sinc 转移函数的极点结构** — 必须分析 sinc(πfL(1-n̂·û)/c) 的零点/极点
- **Gamma^V 的完整被积函数表达式** — 包括天线模式乘积、sinc 平方、空间相位因子
- **共面 Γ^V = 0 的显式证明** — 从数学上展示三重标量积论证
- **格式**：Markdown 带 MathJax（$$ ... $$ 环境）

#### 验收标准

| # | 标准 | 验收方式 |
|---|------|---------|
| A1 | 至少 5 个编号公式，从第一性原理推导 | 手动审查 |
| A2 | Hu I1-I4 留数计算完整（5 个极点） | 公式中必须出现 z_0, z_1, z_2, z_3, z_4 |
| A3 | OLC sinc 转移函数明确替代 Hu 指数 | 笔记中必须出现 T_one^OLC 和 T_one^Hu 的对比 |
| A4 | Gamma^V 被积函数完整（天线 + sinc + 相位） | 公式中必须包含 [F_i^+ F_j^× - F_i^× F_j^+] 项 |
| A5 | 共面 Γ^V = 0 有显式证明 | 推导中必须出现 (n̂₁ × n̂₂)·d̂ = 0 的论证 |
| A6 | 极点分析（sinc vs 指数） | 必须分析 sinc 的零点/极点结构 |

---

### ST2: 小臂近似（kL << 1）解析推导

| 字段 | 内容 |
|------|------|
| **输入** | `note/P2-1-olc-principles.md`, `note/P3-phase3-cross-comparison.md` |
| **输出** | `note/P-chiral-orf-analytical.md` Section 2（与 ST1 同一文件） |
| **Agent** | general-purpose |
| **优先级** | P0 |
| **依赖** | None（与 ST1 并行） |
| **置信度** | 0.90（小臂近似是标准技术，风险低） |

#### 具体物理任务

在小臂近似 $kL \ll 1$（即 $fL/c \ll 1$）下，sinc 函数可展开为：

```
sinc(x) = 1 - x²/6 + O(x⁴)
```

代入 ORF 积分，得到纯几何解析表达式。

**关键公式必须推导：**

1. **小臂近似下的 T_one^OLC**：
   ```
   T_one^OLC ≈ (i2πfL/c) · [1 - (πfL/c)²(1-n̂·û)²/6] · exp[-i(πfL/c)(1-n̂·û)]
             ≈ -(4π²f²L²/c²)(1-n̂·û) + O((fL/c)³)
   ```
   最低阶必须显式给出。

2. **Gamma^I 的小臂近似**：
   ```
   Γ^I_ij(f) ≈ (4π²f²L_i²L_j²/c⁴) · ∫(d²Ω/4π) (1-n̂·û_i)(1-n̂·û_j) Σ_A F_i^A F_j^A · e^{i2πf n̂·Δr_ij/c}
   ```
   进一步在 $fL/c \to 0$ 极限下（空间相位也展开），必须给出纯几何积分的精确解析结果：
   ```
   Γ^I_ij(f → 0) = geometric_constant(i_1, i_2, delta)
   ```
   其中 $i_1, i_2$ 是探测器倾角，$\delta$ 是两探测器连线夹角。

3. **Gamma^V 的小臂近似**：
   ```
   Γ^V_ij(f) ≈ (4π²f²L_i²L_j²/c⁴) · ∫(d²Ω/4π) (1-n̂·û_i)(1-n̂·û_j) [F_i^+ F_j^× - F_i^× F_j^+] · e^{i2πf n̂·Δr_ij/c}
   ```
   在 $fL/c \to 0$ 极限下，必须给出显式解析结果，**特别标注**对 $(\hat{n}_{1} \times \hat{n}_{2}) \cdot \hat{d}$ 的依赖。

4. **LISA×Taiji 数值预测**：对于 $i_1=60°$、$i_2=0°$、$\delta=60°$，必须给出：
   - 小臂近似下的 Gamma^I(0) 和 Gamma^V(0) 的数值
   - 与 Orlando 2021 Figure 5 的对比（定性，不要求定量匹配）

#### 交付物格式要求

（与 ST1 同一文件 `note/P-chiral-orf-analytical.md`，作为 Section 2）

Section 2 必须包含：
- **至少 4 个编号公式**（(6) 到 (9)+）
- **小臂近似展开的完整步骤**（从 sinc 展开到 Gamma^I/V 解析结果，不跳步）
- **Gamma^V 对非共面因子的显式依赖** — 必须展示 $(\hat{n}_1 \times \hat{n}_2) \cdot \hat{d}$
- **LISA×Taiji 的数值预测** — 给出 $|\Gamma^I(0)|$ 和 $|\Gamma^V(0)|$ 的具体数值

#### 验收标准

| # | 标准 | 验收方式 |
|---|------|---------|
| B1 | 小臂近似 sinc 展开完整 | 公式中必须出现 sinc(x) = 1 - x²/6 + ... |
| B2 | Gamma^I 和 Gamma^V 的小臂近似都给出 | 两个公式都必须有编号 |
| B3 | Gamma^V 对非共面因子的依赖显式 | 公式中必须出现 (n̂₁ × n̂₂)·d̂ |
| B4 | LISA×Taiji 数值预测 | 必须有具体数值（不只是符号表达式） |
| B5 | fL/c → 0 极限下的纯几何结果 | 必须给出几何常数（不依赖 n̂ 的表达式） |
| B6 | 与 Orlando 2021 的对比 | 必须引用并比较 |

---

### ST3: 验证脚本（解析求解器 + 数值积分对比）

| 字段 | 内容 |
|------|------|
| **输入** | `note/P-chiral-orf-analytical.md`（ST1+ST2 产出）, `note/P0-1-hu-prd-understanding.md`, `scripts/01-olc-orf-solver.py`（已验证的 OLC ORF solver）, `scripts/11-multi-constellation-chiral-orf.py`（含 bug，参考） |
| **输出** | `scripts/verify-chiral-orf-analytical.py`（完整验证脚本，含测试） |
| **Agent** | general-purpose |
| **优先级** | P1 |
| **依赖** | ST1（统一公式）, ST2（小臂近似公式） |
| **置信度** | 0.90（这是纯编码任务，风险取决于 ST1/ST2 的质量） |

#### 具体代码任务

编写 `scripts/verify-chiral-orf-analytical.py`，包含以下模块：

**模块 1: 几何工具（几何常数计算）**
```python
def sky_average_orf(notation, detector1, detector2):
    """Numerical sky-average of ORF using Monte Carlo or grid integration.
    Uses OLC transfer function T_one^OLC (NOT Hu exponential).
    """
```

**模块 2: 解析公式实现（来自 ST1+ST2）**
```python
def gamma_I_analytical(notation, detector1, detector2, freq):
    """Gamma^I from Hu I1-I4 + OLC sinc — ST1 formula (X)."""
    pass

def gamma_V_analytical(notation, detector1, detector2, freq):
    """Gamma^V from Hu I1-I4 + OLC sinc — ST1 formula (Y)."""
    pass

def gamma_I_small_arm(freq, detector1, detector2):
    """Gamma^I in small-arm approximation — ST2 formula (6)."""
    pass

def gamma_V_small_arm(freq, detector1, detector2):
    """Gamma^V in small-arm approximation — ST2 formula (7)."""
    pass
```

**模块 3: 验证测试**
```python
def test_coplanar_gamma_v_zero():
    """AC-1: coplanar network must have Gamma^V ≈ 0."""
    pass

def test_noncoplanar_gamma_v_detectable():
    """AC-2: LISA×Taiji must have non-zero Gamma^V."""
    pass

def test_gamma_I_consistency():
    """AC-3: Gamma^I must match 01-olc-orf-solver.py."""
    pass

def test_analytical_vs_numerical():
    """AC-4: analytical vs numerical < 5% for fL/c < 0.1."""
    pass

def test_small_arm_boundary():
    """AC-4 boundary: relative error > 5% when fL/c > 0.1."""
    pass

def test_physical_consistency():
    """Q-4: Gamma^I symmetric, Gamma^V antisymmetric, Gamma^I(0) const, etc."""
    pass
```

#### 代码质量要求

- **物理常数**：$c = 299792458$ m/s, $L = 2.5 \times 10^9$ m（LISA arm length）
- **SI 单位制**：频率以 Hz 为单位，长度以 m 为单位
- **inline 注释**：每个关键步骤必须引用公式编号（如 "# ST1 formula (3)"）
- **docstring**：每个函数必须有清晰 docstring（输入、输出、物理含义）
- **引用公式编号**：函数 docstring 中必须引用产出文件中的公式编号

#### 验收标准

| # | 标准 | 验收方式 |
|---|------|---------|
| C1 | 脚本通过 `--tests` 模式 | `python3 scripts/verify-chiral-orf-analytical.py --tests` 全部 PASS |
| C2 | AC-1 测试 PASS | 共面网络 Gamma^V < 10⁻⁶ |
| C3 | AC-2 测试 PASS | LISA×Taiji sky-max Gamma^V ∈ [0.01, 1.5] |
| C4 | AC-3 测试 PASS | Gamma^I vs 01-olc-orf-solver 相对误差 < 5% |
| C5 | AC-4 测试 PASS | 解析 vs 数值相对误差 < 5%（fL/c < 0.1） |
| C6 | AC-5 测试 PASS | 小臂近似边界（fL/c > 0.1 时误差增大） |
| C7 | Q-4 测试 PASS | 对称性、反对称性、低频极限 |
| C8 | 每个测试运行时间 < 60s | 计时器检查 |
| C9 | 公式编号引用在代码中 | grep 检查 docstring 中的公式编号 |

---

### ST4: 综合验证与总结

| 字段 | 内容 |
|------|------|
| **输入** | `scripts/verify-chiral-orf-analytical.py`（ST3 产出）, `note/P-chiral-orf-analytical.md` |
| **输出** | 无新文件 — ST3 的测试输出即为验证结果 |
| **Agent** | general-purpose |
| **优先级** | P2 |
| **依赖** | ST3 |
| **置信度** | 0.85（取决于 ST3 代码质量） |

#### 具体任务

运行 ST3 产出的验证脚本，记录所有测试结果。

如果有任何测试 FAIL：
1. 诊断失败原因（公式错误 or 代码错误）
2. 修正后重新测试
3. 最多迭代 3 次

#### 验收标准

| # | 标准 | 验收方式 |
|---|------|---------|
| D1 | 全部 6 个测试 PASS | `--tests` 输出 |
| D2 | 至少 1 个失败被诊断和修复 | 日志中必须有修复记录 |
| D3 | 运行时间 < 60s | 计时器检查 |

---

## 3. 并行策略

```
Iteration N:
  ST1 (解析推导)  ──→ 并行  ──→  ST2 (小臂近似)    ──→  (same file, Section 2)
  ↓                                              ──→
  ↓                                              ──→
  └──────────────────────────────────────────────┼──→ ST3 (验证脚本)
                                                 │
                                                 ↓
                                             ST4 (综合验证)
```

- **ST1 和 ST2 并行执行**（两个都产出数学笔记，不相互依赖）
- **ST3 等待 ST1 完成后开始**（需要统一公式）
- **ST3 不依赖 ST2**（通用解析代码可以先写，小臂近似作为额外测试）
- **ST4 等待 ST3 完成后运行**（需要代码完成）

---

## 4. 全局约束引用

本任务分解遵循以下约束：
- **RALPH Loop 规则**：1-loop(6阶段) → 2-loop(6阶段)
- **规则7**：Commander 不亲自写代码/跑脚本，通过 Agent 分发
- **规则8**：每轮结束必须派发 sub-brain 质疑
- **CLAUDE.md 规则**：P1 实际问题优先，P2 完成度低优先，P3 可理解性优先，P4 持续行动不询问

---

## 5. 失败处理

| 失败场景 | 处理方案 |
|----------|---------|
| ST1 的 sinc 留数计算过于复杂 | 给出最低阶近似（只在小臂近似下），ST2 继续执行 |
| ST3 的公式引用无法对应 | 检查 ST1 的公式编号，修正后重新测试 |
| AC-1 失败（共面 Gamma^V ≠ 0） | 检查交叉偏振项的符号约定和 sinc 的 prefactor |
| AC-3 失败（Gamma^I vs 01-olc-orf-solver 不一致） | 检查归一化约定（1/4π vs 其他）和天线模式定义 |
| AC-4 失败（解析 vs 数值误差 > 5%） | 检查小臂近似的适用边界（fL/c < 0.1） |

---

*Decomposer: Phase 3 Agent, Iteration 32*
*Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>*
*Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>*
