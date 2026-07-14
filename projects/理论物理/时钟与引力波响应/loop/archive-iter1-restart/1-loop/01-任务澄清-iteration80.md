# 01-任务澄清（Iteration 80）

> 所属规格：`/Users/a1-6/Desktop/workspace/loop/1-loop/01-任务澄清.md`
> 迭代编号：80（新 round 首轮）
> 输入：Iteration 36 遗留 gap + Iteration 79 完成状态
> 时间：2026-07-11

---

## 一句话任务（不超过3行）

编写 helicity 翻转对称性数值验证脚本，在空间相位 exp(-ik·Δx) 存在时检验 Γ^V → -Γ^V 的对称性。
验证 Γ^V 奇偶性在非共面构型（LISA-Taiji）下的数值表现。

## 边界

- **范围**：
  - 编写新的验证脚本 `scripts/verify-helicity-flip-symmetry.py`
  - 验证 Γ^V 在反射变换下的奇偶性：P^V(n̂) → -P^V(n̂')
  - 验证空间相位因子 exp(-2πif·Δx/c) 不破坏 helicity 翻转对称性
  - 覆盖共面（Taiji x Taiji, Γ^V = 0）和非共面（LISA x Taiji, Γ^V ≠ 0）两种场景
  - 在多种频率下重复验证

- **边界**：
  - 不做非共面 Γ^V 的解析推导（那是 Iter 36 第一个 gap，留给后续迭代）
  - 不修改已有脚本 `11-multi-constellation-chiral-orf.py`
  - 不做论文更新（Iteration 79 已覆盖）
  - 不扩展至 helicity 翻转对 chi = V/I 参数空间依赖的影响

## 失败标准

- 脚本无法独立运行并输出全部 4 个测试用例结果
- 测试 T1（共面 Γ^V ≈ 0）失败：|Γ^V| > 1e-6（在 f → 0 极限下）
- 测试 T2（反射对称性）失败：P^V(θ, φ) + P^V(θ, 2π-φ) 相对偏差 > 1%
- 测试 T3（空间相位下对称性保持）失败：包含/不包含空间相位时 Γ^V 比值偏离 1.0 超过 5%
- 测试 T4（非共面 Γ^V ≠ 0）失败：LISA-Taiji 在 f=0.01 Hz 下 |Γ^V| < 1e-10

## 硬约束

- 所有数值结果必须来自独立的验证脚本（不与 Iter11 脚本共享代码实现，仅共享物理模型）
- 反射变换必须显式使用 (θ, φ) → (θ, 2π-φ) 坐标映射，不可用启发式旋转
- 空间相位因子必须使用 exp(-2πif·Δx/c)，其中 Δx = |x_LISA - x_Taiji| ≈ 1 AU
- 测试必须覆盖至少三个频率点：f = 0.001, 0.01, 0.1 Hz
- 数值积分网格分辨率不低于 60×120（θ×φ）

## 已有条件

- **Iter11 脚本**: `scripts/11-multi-constellation-chiral-orf.py` (1127 行)，包含空间相位因子，已验证通过
- **验证脚本**: `scripts/verify-chiral-orf-analytical.py` (610 行)，7/7 PASS，作为参考实现
- **解析推导**: `note/P-chiral-orf-analytical.md` (845 行)，含 Γ^V 宇称奇性证明（§4.3）和五极点留数
- **Orlando 2021 benchmark**: `scripts/11-multi-constellation-chiral-orf.py` 含 `cmd_benchmark_orlando()` 函数
- **理论背景**: Γ^V 是宇称奇 ORF，被积函数 P^V = F_+1·F_x2 - F_x1·F_+2 在反射变换下变号
- **Iteration 79 产出**: 论文 §3.5 已更新空间相位 exp(-ik·Δx) 结果（40.38% 偏差）
- **Python 环境**: numpy, matplotlib 可用

---

## 被跳过的待办

| 待办 | 优先级 | 跳过原因 |
|------|--------|----------|
| 非共面 Γ^V 解析验证（超越小臂近似） | P1 | 需要深入的理论推导，非纯数值任务，留给 Iter 81+ |
| 反射对称性适用范围的理论限定 | P2 | Iter 36 sub-brain 质疑已在 P-chiral-orf-analytical.md §4.3 中部分覆盖 |

---

## 确认

```
---
## 任务澄清完成
- 状态：已完成
- 置信度：0.85
- next_brain: 进入 1-loop/02 目标澄清
```
