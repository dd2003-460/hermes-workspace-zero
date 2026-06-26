---
name: decision-enter-2loop-teukolsky-aim
description: Iter 18 decision — 进入2-loop，实现Teukolsky+AIM
metadata:
  type: project
---

# 1-loop Decision (Iter 18) — 进入 2-loop

## 现状盘点

- I-1~I-6 + P0 全部完成
- FDTD 框架在 a>0.7 失效（RW方程不适用于Kerr）
- AIM 在 Schwarzschild (a=0) 已验证收敛（dehghan 公式，N=4-6，rel_D 指标）
- Teukolsky+AIM 是唯一路线（iter 5 决策 + iter 4-12 AIM 经验支撑）

## 决策

**enter_2loop: true**

理由：
1. Task 明确：Teukolsky 方程的 AIM 数值求解
2. 基准明确：Berti 2009 Table II 的 Kerr QNM 频率
3. 已有产出：8 个 AIM 脚本提供 coefficient 实现模式和 scaling 经验
4. 阻塞项无：无需外部数据，Berti 2009 已有数值参考

## 2-loop 执行计划

Step 1: 阅读 Berti 2009 中 Teukolsky 方程的 AIMS 离散化实现细节（Master 变量 r → x 变换，separation 公式）
Step 2: 实现 Kerr Teukolsky coefficient 函数 p1(x,a,omega,l,m) 和 p2(x,a,omega,l,m)
Step 3: 套用已有 AIM 框架（dehghan 公式验证版）做 Schwarzschild 回归测试（a=0 结果应与已有解一致）
Step 4: 逐步增加 a（0.1→0.3→0.5→0.7→0.9），与 Berti 2009 基准比较

## 置信度

0.85 — AIM 在 a=0 已验证，Teukolsky coefficient 是确定性公式（有文献参考）。唯一不确定：convergence window 在 Kerr 区域的行为（已有 Schwarzschild 经验推断 N=6-8 足够）。
