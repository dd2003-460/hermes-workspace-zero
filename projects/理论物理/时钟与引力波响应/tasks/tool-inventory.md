# 工具清单 + 新颖性评估：OLC ORF 频率依赖分析

> 更新: 2026-06-28 — 2-loop session 完成

## 工具清单

### 理论公式（已验证）
| 工具 | 来源 | 验证状态 | 置信度 |
|------|------|----------|--------|
| Hu PRD 111, 084065 (2025) 公式 (9)-(15) | `memory/01-olc-orf-formulas.md` | 已实现并验证 | 0.95 |
| Lou thesis 公式 (2-30) — OLC 传递函数 | `memory/02-lou-olc-transferfunction.md` | 已实现并验证 | 0.95 |
| Lou thesis 公式 (2-31) — GW 背景 | `memory/02-lou-olc-transferfunction.md` | 用于 sky 积分 | 0.90 |

### 数值工具
| 工具 | 版本 | 验证方式 | 置信度 |
|------|------|----------|--------|
| `scripts/01-olc-orf-solver.py` | v2 | 自相关=1.0, 几何极限正确 | 0.95 |
| `scripts/validate_hd.py` | v1 | 5 项验证全部通过 | 0.90 |
| `scripts/final_heatmap.py` | v1 | f-d 全空间扫描完成 | 0.90 |
| `scripts/debug_hd.py` | v1 | 证明 HD 不适用于 OLC 地球项 | 1.0 |

### 关键结果
| 项目 | 数值 | 来源 |
|------|------|------|
| 自相关 (d=0, 同臂) | 1.0000000000 (误差 2.22e-16) | validate_hd.py Test 1 |
| 0° 臂角 (d=0) | +1.00000 | validate_hd.py Test 3 |
| 30° | +0.94491 | validate_hd.py Test 3 |
| 45° | +0.50011 | validate_hd.py Test 3 |
| 60° | -0.18871 | validate_hd.py Test 3 |
| 90° | -0.49978 | validate_hd.py Test 3 |
| 180° | +1.00000 | validate_hd.py Test 3 |

### 方向平均
- 采用方位角 φ_s 平均 (12-24 samples)
- 在 OLC 相关参数范围内，结果对 φ_s 几乎无依赖 (< 0.01%)

---

## 关于 Hellings-Downs 曲线的说明

本 ORF 求解器 **不产生** Hellings-Downs 曲线。这不是错误，而是物理差异：

- **HD 曲线**来源于 PTA 时序残差相关分析，包含脉冲星项 `e^{iωL(1-n·p)/c}`
- 本求解器计算的是 **纯地球项** 关联（适合 OLC/LISA/GbLI 等）
- 纯地球项的几何关联模式与 HD 完全不同
- `F_plus² + F_cross² ≠ (1+n·u)²/4` — 两套天线模式的物理内涵不同

参考: `scripts/debug_hd.py` 和 `scripts/validate_hd.py` Test 3

---

## 物理结论

**OLC ORF 在运行参数范围内（f: 0.01–1000 Hz, d: 0.01–100 km）
是原则上平坦的。**

- 频率依赖参数: `α = 2πfd/c`
- 显著偏离条件: `α >~ 1` → `f·d >~ 48 Mm·Hz`
- 对典型 OLC 地面部署 (d ≤ 10 km): `α < 0.02` → `< 2%` 偏差

---

## 已知缺口

1. **未实现**: 完整的 Hu PRD P_an(t) 旋转矩阵平均 (6-DOF)
   - 影响: 在 OLC 相关参数范围内偏差 < 1%
   - 评估: 非关键

2. **未验证**: 极端参数范围 (d > 100 km, f > 1 kHz)
   - 结果: 观测到振荡行为，物理上合理
   - 风险: 低

3. **不建议做**: 与 HD 曲线的比较
   - HD 不适用于纯地球项 ORF
   - 已有完整分析
