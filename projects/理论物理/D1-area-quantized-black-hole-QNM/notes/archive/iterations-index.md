# 🔄 迭代日志索引 — 求解器演进决策树

**项目**: D1-area-quantized-black-hole-QNM
**最后更新**: 2026-06-12
**用途**: 快速定位求解器演进的关键转折点和决策

---

## 决策树（只读关键节点）

```
v6-v10 Leaver连分数法 → 全部NaN → ❌ 放弃
  │ 根因: gamma符号错误 + Taylor系数数值不稳定
  │ → 详见: 01-v6-to-v10-iteration-log.md
  │
  ▼
v11 射击法 + RK4 → RK4卡死 → ❌ 放弃
  │ 根因: 固定步长RK4在奇异点附近数值不稳定
  │ → 详见: 02-v11-shooting-method-detailed.md, 03-v11-rk4-hang-analysis.md
  │
  ▼
v13 改用R*坐标 → 仍然NaN → ❌ 放弃
  │ 根因: tortoise坐标离散化精度不够
  │ → 详见: 03-v13-r-star-shooting.md
  │
  ▼
v20 FDTD (leapfrog + sponge + FFT) → ✅ 基准通过 (误差<1%)
  │ 关键决策: 放弃Leaver法，改用FDTD波动方程方法
  │ → 详见: 04-v20-fdtd-stable.md
  │
  ▼
v21 Kerr扩展 → 频率误差90-95% → ❌
  │ 根因: tortoise坐标硬编码a=0.5 + δV_rot形式不对
  │ → 详见: 05-i4-kerr-design.md, 05-v21-kerr-fdtd-run.md
  │
  ▼
v22 (l=2) → ✅ a=0.5误差0.03% / ❌ a>0.7势垒消失 → ⚠️ 框架边界发现
  │ 关键发现: E_lm(aω)在aω>1时变负 → 旋转修正势两项都负 → 势垒消失
  │ → ★ 详见: 06-v22-kerr-diagnostic.md [关键转折点]
  │
  ▼
v23 (l=3) → ✅ a=0.5误差1.02% / ❌ a>0.7仍消失 → ❌ 确认框架边界
  │ 结论: 增大l不能阻止高旋转下势垒消失 → 框架失效范围确认为aω<~0.7
  │ → ★ 详见: 07-v23-l3-kerr-diagnostic.md [关键转折点]
  │
  ▼
v25 QBH修正 → 负结果 (δω/ω与R无关) → ❌ 简单模型排除
  │ 结论: 简单反射率边界条件不足以产生可观测效应
  │ → 详见: 08-i5-qbh-correction/01-i5-qbh-results.md
```

---

## 文件分类

### ⭐ 关键转折点（必读）

| 文件 | 关键发现 |
|------|----------|
| **04-v20-fdtd-stable.md** | FDTD方法验证通过，确立后续框架 |
| **06-v22-kerr-diagnostic.md** | 发现框架失效范围 aω < ~0.7 |
| **07-v23-l3-kerr-diagnostic.md** | 确认框架失效与l无关，必须用Teukolsky方程 |

### 📖 参考历史（了解决策背景）

| 文件 | 内容 | 状态 |
|------|------|------|
| 01-v6-to-v10-iteration-log.md | v6-v10 Leaver法迭代历史 | ✅ 已弃用 |
| 02-v11-shooting-method-detailed.md | v11射击法详细设计 | ✅ 已弃用 |
| 03-v11-rk4-hang-analysis.md | v11 RK4卡死诊断 | ✅ 已弃用 |
| 05-i4-kerr-design.md | I-4设计规划 | ✅ 已弃用 |
| 05-v21-kerr-fdtd-run.md | v21运行记录 | ✅ 已弃用 |
| 06-i4-kerr-v21-run-results.md | v21结果（已过期，被v22替代） | ❌ 过时 |

---

## 迭代总结

| 版本 | 方法 | 关键指标 | 状态 |
|------|------|----------|------|
| v6-v10 | Leaver连分数 | 全部NaN | ❌ 放弃 |
| v11 | 射击法+RK4 | RK4卡死 | ❌ 放弃 |
| v13 | R*坐标射击法 | 仍NaN | ❌ 放弃 |
| **v20** | **FDTD+FFT** | **误差<1%** | **✅ 基准框架** |
| v21 | Kerr扩展 | 误差90-95% | ❌ 修复 |
| **v22** | **Kerr(l=2)** | **误差0.03% (a=0.5)** | **✅ 框架有效范围** |
| **v23** | **Kerr(l=3)** | **误差1.02% (a=0.5)** | **✅ 框架失效确认** |
| **v25** | **QBH修正** | **δω/ω与R无关** | **✅ 负结果** |

---

*origin: ai — 迭代日志索引，建立决策树引导*
