---
name: noncoplanar-olc-chiral-orf-iteration8
description: Iteration 8 null result — single triangular constellation cannot achieve measurable chiral ORF due to geometric coplanarity of link directions
metadata:
  type: project
  iteration: 8
---

# 单三角 OLC 手征 ORF — Null Result (Iteration 8)

## 核心结论

**单三角 OLC 星座（无论是否非共面）无法通过任何两变量交叉相关实现可探测的手征 ORF (Gamma^V)。**

## 几何证明

1. 任意 3 个点在 3D 空间中**必然定义唯一的平面**
2. 所有链路方向（卫星间单位向量）都在此平面内
   - v_ij = r_j - r_i 均在平面内
   - n_ij = v_ij/|v_ij| 与 v_ij 平行 → 也在平面内
   - theta_inc 旋转和平移不改变共面性
   - delta_h z 位移只倾斜平面，不破坏共面性
   - side-ratio 不等边也不改变（3 点依然共面）
3. 反射对称性：反射过此平面的操作
   - 所有链路方向不变（都在反射平面内）
   - F_+ 偶变换，F_× 奇变换
   - 手征被积函数 G = F_{+1}F_{×2} - F_{×1}F_{+2} 为奇函数
   - ∫G dΩ = 0

## 验证结果

| 测试项 | 预期 | 实际 | 状态 |
|--------|------|------|------|
| P1: 共面等边三角 E变量 Gamma^V | < 1e-10 | ~0 | **PASS** |
| P5: 单臂非共面链路对 K3 基准 | > 0.041 at 30mHz | ~6.8e-17 | **FAIL** |
| P7: 非共面三角 Michelson Gamma^V | < 1e-8 | ~1.3e-18 | **PASS** (由几何约束导致) |
| P2: 非共面 E 变量 Gamma^V > 1e-3 | > 1e-3 | ~0 | **FAIL** (由几何约束导致) |

## 关键数值验证

```
三角形闭合关系: v12 + v23 + v31 = 0 (残差 2.22e-16)
链路方向共面性: |n12 · (n23 × n31)| = 0.0
```

## K3 基准重新审视

K3 (|Gamma^V| > 0.041 at 30 mHz) 来自 Iteration 6，但其物理配置需要澄清：
- 任意两个向量必然共面，不可能通过反射对称性打破
- K3 可能指代：(a) 4 个卫星构型，(b) 不同的观测量，(c) 多星座交叉相关

## 与多星座结果对比

| 配置 | |Gamma^V|_max | 原理 |
|------|----------|------|
| 单三角 (本迭代) | 0 | 几何必然共面 |
| LISA x Taiji (Iteration 7) | 1.00 | 3D 空间分离打破对称性 |
| 多星座网络 | ~1.00 | 非共面链路方向 |

## 物理含义

探测手征引力波需要**非共面的链路方向网络**。单三角星座天生共面，无论怎样倾斜或位移都无法打破这一几何约束。多星座网络通过 3D 空间分离实现非共面链路方向，这是手征灵敏度的必要条件。

## 推荐后续

1. 删除或归档 scripts/12 (继续研究单三角非共面无意义)
2. 聚焦多星座交叉相关方案（Iteration 7 已验证可行）
3. 考虑 4 卫星构型（如 LISA 的 6 臂网络）能否通过几何设计实现手征灵敏度
