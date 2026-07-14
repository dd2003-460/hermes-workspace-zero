# 03-任务分解（Iteration 80）

> 所属规格：`/Users/a1-6/Desktop/workspace/loop/1-loop/03-任务分解.md`
> 迭代编号：80
> 输入：`02-目标澄清-iteration80.md`（验收标准）
> 输出：`03-任务分解-iteration80.md`（子任务 DAG 列表）
> 时间：2026-07-11

---

## 一句话任务

编写 helicity 翻转对称性数值验证脚本 `scripts/verify-helicity-flip-symmetry.py`，在空间相位 exp(-ik·Δx) 存在时检验 Γ^V → -Γ^V 的对称性。

---

## DAG 依赖图

```
                    ┌──────────────────┐
                    │        ST1       │  设计并编写验证脚本框架
                    │  (detector tensor E,           │
                    │   chiral_corr, 天空网格)       │
                    └───────┬──────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │    ST2     │   │    ST3     │   │    ST4     │
   │ T1: 共面   │   │ T2: 反射   │   │ T3: 空间   │
   │ Γ^V ≈ 0    │   │ 对称性     │   │ 相位       │
   └──────┬─────┘   └──────┬─────┘   └──────┬─────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                            ▼
                    ┌────────────┐
                    │    ST5     │
                    │ T4: 非共面 │
                    │ Γ^V ≠ 0    │
                    └──────┬─────┘
                           │
                           ▼
                    ┌────────────┐
                    │    ST6     │
                    │ 运行验证   │
                    │ 全部通过   │
                    └────────────┘
```

**DAG 说明**：
- ST1 是基础框架，必须最先完成
- ST2（T1）、ST3（T2）、ST4（T3）基于 ST1 框架并行开发，各自测试互不干扰
- ST5（T4）在 ST1 完成后即可开始（不依赖 ST2-ST4），但与 ST6 串行
- ST6 依赖 ST2、ST3、ST4、ST5 全部完成

---

## 子任务列表

### ST1: 设计并编写 helicity flip 验证脚本框架

**目标**：编写脚本骨架，包含所有物理计算的独立实现（不导入 Iter11 脚本）。

**输入**：
- `02-目标澄清-iteration80.md` 验收标准
- `note/P-chiral-orf-analytical.md` §4.3 反射对称性证明（参考物理模型）
- `scripts/verify-chiral-orf-analytical.py` 函数签名参考（仅参考，不可复用代码）

**输出**：
- 文件 `scripts/verify-helicity-flip-symmetry.py`（框架版本）
- 包含以下独立实现的核心函数：
  1. `olc_transfer_function(f, L, cos_nu)` — OLC 单臂链路传递函数
  2. `antenna_FA(n_theta, n_phi, u_theta, u_phi)` — 探测器张量 E 天线方向图
  3. `compute_chiral_corr(f, L1, L2, u_vec, v_vec, include_phase)` — 计算 chiral_corr 和被积函数 P^V(θ, φ)
  4. `build_sky_grid(ntheta, nphi)` — 构建 60×120 θ×φ 网格
  5. `compute_gamma_V(...)` — 计算 Γ^V（积分 chiral_corr × 网格测度）
  6. 探测器参数常量：Taiji（L=3e6, 倾角≈0）、LISA（L=2.5e6, 倾角≠0）
  7. 空间相位因子：`phase = exp(-2j * pi * f * path / c)`，path = projected baseline ≈ 1 AU
- 4 个测试函数骨架（空函数体，含 docstring）：
  - `test_t1_coplanar()`
  - `test_t2_reflection()`
  - `test_t3_spatial_phase()`
  - `test_t4_noncoplanar()`
- TestResult 类和测试报告输出函数（JSON 格式）

**验收标准**：
- AC-5 部分：脚本可 `python3 scripts/verify-helicity-flip-symmetry.py --dry-run` 运行，输出测试名称和参数（结果为 SKIP）
- 所有核心函数不 import 自 `11-multi-constellation-chiral-orf.py`
- 反射变换显式使用 `(θ, φ) → (θ, 2π-φ)` 坐标映射
- 空间相位因子显式为 `exp(-2j * pi * f * path / c)`

**回滚**：删除 `scripts/verify-helicity-flip-symmetry.py` 即可回滚。

**置信度**：0.92 — 已有 `verify-chiral-orf-analytical.py` 作为参考，物理模型完全明确，独立实现路径清晰。

**依赖**：null

---

### ST2: 实现 T1 — 共面 Taiji×Taiji 的 Γ^V ≈ 0

**目标**：验证 Taiji×Taiji 共面构型下，反射对称性导致 Γ^V ≈ 0。

**输入**：
- ST1 输出的脚本框架
- `02-目标澄清-iteration80.md` AC-1 验收标准

**输出**：
- 完整实现的 `test_t1_coplanar()` 函数
- 对 f = 0.001, 0.01, 0.1 Hz 分别计算 Γ^V
- 输出每个频率的 |Γ^V| 值和 PASS/FAIL 判定

**验收标准**：
- AC-1：所有三个频率 |Γ^V| < 1e-6
- AC-1 额外：f = 0.001 Hz 时 |Γ^V| < 1e-8
- 使用 60×120 网格
- 判定逻辑与 AC-1 完全对应

**回滚**：修改 `test_t1_coplanar()` 为空函数或返回 None，脚本其他部分不受影响。

**置信度**：0.93 — Iter11 脚本已验证 Taiji×Taiji Γ^V ≈ 0；物理模型已知；边界条件清晰（共面=两个相同探测器相同取向）。

**依赖**：ST1

---

### ST3: 实现 T2 — 反射对称性逐点验证

**目标**：在 60×120 网格上逐点验证 P^V(θ, φ) + P^V(θ, 2π-φ) ≈ 0。

**输入**：
- ST1 输出的脚本框架
- `02-目标澄清-iteration80.md` AC-2 验收标准

**输出**：
- 完整实现的 `test_t2_reflection()` 函数
- 对 Taiji×Taiji 和 LISA×Taiji 分别逐点计算：
  - `deviation(θ, φ) = |P^V(θ, φ) + P^V(θ, 2π-φ)| / (|P^V(θ, φ)| + |P^V(θ, 2π-φ)| + 1e-20)`
- 报告 max(deviation) 和 mean(deviation)

**验收标准**：
- AC-2：max(deviation) < 0.01（1%）
- AC-2：mean(deviation) < 0.001（0.1%）
- 对 Taiji×Taiji 和 LISA×Taiji 两个场景均 PASS

**回滚**：修改 `test_t2_reflection()` 为空函数或返回 None。

**置信度**：0.90 — 这是被积函数层面的逐点验证，不涉及积分收敛性。解析证明（§4.3）确认 P^V 是宇称奇函数。唯一风险是 chiral_corr 实现中是否包含了空间相位（空间相位在反射下可能不对称）。需要确认空间相位 `exp(-2πif·path/c)` 的 path 在 (θ, φ) → (θ, 2π-φ) 下是否保持不变。

**依赖**：ST1

---

### ST4: 实现 T3 — 空间相位下 helicity flip 对称性保持

**目标**：验证空间相位因子 exp(-2πif·Δx/c) 不破坏 helicity flip 对称性。

**输入**：
- ST1 输出的脚本框架
- `02-目标澄清-iteration80.md` AC-3 验收标准

**输出**：
- 完整实现的 `test_t3_spatial_phase()` 函数
- 对 LISA×Taiji 在 f = 0.001, 0.01, 0.1 Hz 下：
  - 计算 Γ^V_with_phase 和 Γ^V_without_phase
  - 逐点验证含/不含空间相位时的 helicity flip 偏差
- 输出比值 |Γ^V_with / Γ^V_without| 和 helicity flip 偏差

**验收标准**：
- AC-3：不含空间相位时 helicity flip 偏差 max < 1%
- AC-3：含空间相位时 helicity flip 偏差 max < 2%
- AC-3：比值在物理预期范围内（不要求精确 1.0）

**回滚**：修改 `test_t3_spatial_phase()` 为空函数或返回 None。

**置信度**：0.85 — 这是本次迭代最核心的"新增"验证。物理论证：空间相位只依赖于路径长度投影，反射变换下投影不变，因此相位因子在 (θ, φ) → (θ, 2π-φ) 下不变，而 chiral_corr 变号，总被积函数仍变号。但数值上需要确认 path 计算在反射变换下确实不变。

**依赖**：ST1

---

### ST5: 实现 T4 — 非共面 LISA×Taiji 的 Γ^V ≠ 0

**目标**：验证非共面构型下 Γ^V 可检测且非零。

**输入**：
- ST1 输出的脚本框架
- `02-目标澄清-iteration80.md` AC-4 验收标准

**输出**：
- 完整实现的 `test_t4_noncoplanar()` 函数
- 对 LISA×Taiji 在 f = 0.001, 0.01, 0.1 Hz 下计算 Γ^V
- 验证 Γ^V 的符号在 helicity flip 下翻转（自洽性检查）

**验收标准**：
- AC-4：所有频率 |Γ^V| > 1e-10
- AC-4：Γ^V 符号在 helicity flip 下翻转（即 ∫P^V dΩ 与 ∫P^V(reflected) dΩ 符号相反）

**回滚**：修改 `test_t4_noncoplanar()` 为空函数或返回 None。

**置信度**：0.90 — Iter11 脚本已验证 LISA×Taiji Γ^V ≠ 0。此任务主要是数值重现。自洽性检查（符号翻转）与 T2 验证方式相同。

**依赖**：ST1

---

### ST6: 运行脚本，验证全部测试通过，确认数值结果物理一致性

**目标**：集成所有测试，运行完整脚本，确认全部 PASS。

**输入**：
- ST2-ST5 输出的完整测试函数
- ST1 输出的脚本框架

**输出**：
- 完整运行的 `scripts/verify-helicity-flip-symmetry.py`
- 全部 4 个测试用例的 PASS/FAIL 结果
- 每个测试的关键数值输出（|Γ^V|、偏差值、比值等）
- 总运行时间 < 120 秒
- 结构化 JSON 输出（或带可解析标记的纯文本）

**验收标准**：
- AC-5：脚本正常输出全部 4 个测试结果
- AC-1：T1 全部 PASS
- AC-2：T2 全部 PASS
- AC-3：T3 全部 PASS
- AC-4：T4 全部 PASS
- 运行时间 < 120 秒
- 数值结果与 P-chiral-orf-analytical.md §4.3 的解析论证一致

**回滚**：ST2-ST5 各自可独立回滚（空函数），不影响 ST1 框架和其他测试。

**置信度**：0.88 — 整体交付置信度。ST1-ST5 的置信度高（0.85-0.93），集成风险主要来自：(1) 空间相位实现中的 baseline 计算是否正确（2）60×120 网格的数值稳定性。两项均在 Iter79 和 Iter11 中有处理经验。

**依赖**：ST2, ST3, ST4, ST5

---

## 并行策略

| 阶段 | 并行任务 | 说明 |
|------|---------|------|
| 阶段 A | ST1 | 基础框架，串行开始 |
| 阶段 B | ST2, ST3, ST4 | 三个测试并行开发，共享 ST1 框架但测试逻辑互不干扰 |
| 阶段 C | ST5 | 可与 ST2-ST4 并行（也仅依赖 ST1），或放在阶段 B 之后 |
| 阶段 D | ST6 | 必须串行等待 ST2-ST5 全部完成 |

**建议执行**：阶段 A → 阶段 B（3 个并行）+ ST5 并行（共 4 个并行）→ 阶段 D

---

## 总预计时间

| 子任务 | 预计时间 | 说明 |
|--------|---------|------|
| ST1 | 30-45 分钟 | 独立实现所有物理函数，含 docstring 和框架 |
| ST2 | 10-15 分钟 | T1 测试逻辑简单（阈值判定） |
| ST3 | 15-20 分钟 | T2 需要逐点计算偏差统计 |
| ST4 | 15-20 分钟 | T3 需要两套计算（含/不含空间相位） |
| ST5 | 10-15 分钟 | T4 测试逻辑简单（非零检测） |
| ST6 | 10-15 分钟 | 集成运行、调试、确认 |
| **总计（串行）** | **90-130 分钟** | |
| **总计（并行）** | **65-85 分钟** | 阶段 B+C 并行执行 |

---

## 关键物理假设（质询记录）

| # | 假设 | 置信度 | 验证方式 |
|---|------|--------|---------|
| 1 | 空间相位在反射 (θ, φ) → (θ, 2π-φ) 下不变 | 0.90 | ST3 验证：含/不含相位时 helicity flip 偏差仍 < 2% |
| 2 | Taiji×Taiji 是共面构型 | 0.95 | 两个探测器倾角均 ≈0（与黄道面夹角极小） |
| 3 | LISA×Taiji 是非共面构型 | 0.90 | LISA 和 Taiji 轨道平面有 ~几度夹角 |
| 4 | 60×120 网格对 helicity flip 逐点验证足够精细 | 0.85 | T2 的逐点验证不依赖积分收敛性，网格分辨率影响较小 |
| 5 | chiral_corr 的 chiral 定义（Fp1·Fx2 - Fx1·Fp2）与解析证明中的 P^V 等价 | 0.95 | 直接来自 JCAP Eq. 2.10 |

---

## 确认区块

```
---
## ⚠️ 等待人类确认
请审阅以上任务分解和依赖关系。
确认：在文件顶部写下 `CONFIRMED 1`（同意）或 `CONFIRMED 2` + 修改建议。
**AI 不可修改已确认区块中的任何内容。**
```
