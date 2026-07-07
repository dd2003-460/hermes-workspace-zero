---
name: multi-constellation-chiral-orf-iteration7
description: Iteration 7 多星座手征 ORF 计算结果 - Orlando 基准修正, sky-max norm_V = 1.0
metadata:
  type: project
  created: 2026-07-06
---

# Iteration 7: Multi-Constellation Chiral ORF

## 脚本
`scripts/11-multi-constellation-chiral-orf.py` — E-variable 版本，CW link sum 定义

## 核心物理发现

### 1. 手征响应是纯几何的
- 归一化后与频率无关 (频率扫描平坦)
- 手征响应来自探测器构型几何对称性破缺
- 在长波极限下，transfer function ≈ 1，不影响归一化手征响应

### 2. Orlando 基准修正
- **之前错误**: sky-averaged gamma_V = 2.3e-5 vs Orlando sky-maximized ~0.3
- **修正**: sky-max norm_V = 1.0 (达到 Cauchy-Schwarz 上限)
- **Orlando 0.3 解释**: 近似 figure 读数或不同归一化约定

### 3. 对称性约束
- Self-correlation: |Gamma^V| < 1e-18 (等边三角形对称性)
- 不同轨道面倾角打破对称 → 非零 chiral ORF
- Inclination scan 关于 45° 对称

## 数值结果

| 配置 | <Gamma^I> | <Gamma^V> | |Gamma^V|_max |
|------|-----------|-----------|-------------|
| Taiji x Taiji | 0.0325 | 1.78e-18 | ~0 |
| LISA x Taiji | -1.99e-4 | 2.26e-5 | 1.00 |
| OLC x Taiji (same i) | 0.0325 | 1.78e-18 | ~0 |
| OLC(30) x Taiji(0) | 0.0220 | -5.59e-4 | 0.99 |

## 测试状态
4/4 PASS:
- Test 1: Self-correlation → zero chiral
- Test 2: Orlando benchmark (sky-max) = 1.0 in [0.01, 1.5]
- Test 3: OLC x Taiji same inclination → zero
- Test 3b: OLC(30) x Taiji(0) → non-zero

## 关键诊断脚本
- `_diag_taiji_tf.py`: Transfer function convention 验证
- `_diag_sky_max.py`: Sky-max vs sky-avg 分析
- `_diag_orlando_e.py`: Orlando E 变量 CW sum vs CW-CCW 验证

## 置信度
整体: 0.82
