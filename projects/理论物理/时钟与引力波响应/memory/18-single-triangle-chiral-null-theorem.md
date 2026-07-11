---
name: single-triangle-chiral-null-theorem
description: Theorem: any 3-satellite triangular constellation has identically zero chiral ORF (Gamma^V) for any two-variable cross-correlation, due to geometric coplanarity of all link directions
metadata:
  type: project
  iteration: 8
---

# 单三角手征 ORF Null 定理

## 定理

任意 3 卫星三角星座，所有两变量交叉相关的手征 ORF Gamma^V 恒等于零。

## 证明

1. 任意 3 点在 3D 空间必然定义唯一平面
2. 所有链路方向单位向量 n_ij = (r_j - r_i)/|r_j - r_i| 均在此平面内
3. 反射过此平面：n_ij 不变（在反射平面内），F_+ 偶，F_× 奇
4. 手征被积函数 G = F_{+1}F_{×2} - F_{×1}F_{+2} 为奇函数
5. 天区积分 ∫G dΩ = 0

## 验证

- 数值验证: |n12 · (n23 × n31)| = 0.0 (机器精度)
- theta_inc 旋转 / delta_h z 位移 / side-ratio 不等边均不能打破共面
- 独立 Agent 验证 4 个问题无 loopholes
- E 变量自相关 Gamma^V = 0 是代数恒等式 (Re(z) - Re(z*) = 0)

## 推论

探测手征引力波需要非共面链路方向 — 多星座网络 (3D 空间分离) 或 4+ 卫星构型

## 来源

- Iteration 8 M1 fork + M2 zero-test (2026-07-10)
- memory/17-noncoplanar-olc-chiral-orf-iteration8.md (详细记录)
