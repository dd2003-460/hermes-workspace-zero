# 📑 笔记索引 — 面积量子化黑洞 QNM 调研

**项目**: D1-area-quantized-black-hole-QNM
**最后更新**: 2026-06-12
**用途**: 导航索引——每个链接对应一个有独立内容的文件

---

## 阅读顺序（逻辑流）

从顶层结论开始，按需要的深度向下追溯：

```
08-synthesis/conclusion.md  ← 最终结论（先看这个）
  ├── 01-literature/        ← 文献综述与 PDF 深度分析
  ├── 02-theory/            ← 理论框架与推导
  ├── 03-numerical-method/  ← 求解器 v6→v23 完整迭代（合并后）
  ├── 04-benchmark/         ← 基准验证
  ├── 05-kerr-extension/    ← Kerr 扩展
  ├── 06-area-quantization/ ← I-5 面积量子化结果
  ├── 06-kerr-qnm-scan/     ← P0 完整扫描
  ├── 07-observability/     ← I-6 观测可测性
  └── archive/              ← 旧求解器版本
```

---

## 各阶段文件清单

### 01-literature/ — 文献综述

| 文件 | 内容 |
|------|------|
| [summary.md](01-literature/summary.md) | 12 篇核心文献 R1-R12 总览 |
| [02-pdf-deep-analysis-*.md](01-literature/02-pdf-deep-analysis-maggiore-agullo-chakravarti.md) | Maggiore/Agullo/Chakravarti PDF 深度分析 |
| [01-summary-and-research-plan.md](01-literature/01-summary-and-research-plan.md) | 调研总结与研究计划 |
| [reading-log.md](01-literature/reading-log.md) | 逐篇阅读笔记 |

### 02-theory/ — 理论推导

| 文件 | 内容 |
|------|------|
| [01-theoretical-framework.md](02-theory/01-theoretical-framework.md) | 理论框架概述 |
| [02-derivation-notes.md](02-theory/02-derivation-notes.md) | 详细推导（Kerr 度规、Regge-Wheeler 修正等） |

### 03-numerical-method/ — 求解器迭代（v6→v23）

**合并后单一主文档**：

| 文件 | 内容 |
|------|------|
| [01-solver-iteration-history.md](03-numerical-method/01-solver-iteration-history.md) | **v6→v23 完整迭代史**：Leaver(v6-10)→Shooting(v11-13)→FDTD(v14-23)，包含所有失败根因、决策点和最终稳定方案 |

**之前拆分为 8 个文件，现已合并。旧文件保留但标记为过时，新读者请直接阅读上述主文档。**

### 04-benchmark/ — 基准验证

| 文件 | 内容 |
|------|------|
| [01-benchmark-calculation-log.md](04-benchmark/01-benchmark-calculation-log.md) | v6-v10 基准测试全过程 |

### 05-kerr-extension/ — Kerr 扩展

| 文件 | 内容 |
|------|------|
| [05-i4-kerr-design.md](05-kerr-extension/05-i4-kerr-design.md) | I-4 Kerr 黑洞基准设计 |
| [06-v22-kerr-diagnostic.md](05-kerr-extension/06-v22-kerr-diagnostic.md) | v22 Kerr(l=2) 诊断 |
| [07-v23-l3-kerr-diagnostic.md](05-kerr-extension/07-v23-l3-kerr-diagnostic.md) | v23 Kerr(l=3) 诊断 |

### 06-area-quantization/ — I-5 面积量子化结果

| 文件 | 内容 |
|------|------|
| [01-i5-qbh-results.md](06-area-quantization/01-i5-qbh-results.md) | I-5 负结果（反射率无效） |

### 06-kerr-qnm-scan/ — P0 完整扫描

| 文件 | 内容 |
|------|------|
| [01-p0-kerr-qnm-scan-results.md](06-kerr-qnm-scan/01-p0-kerr-qnm-scan-results.md) | P0 36 组 Kerr QNM 扫描结果 |

### 07-observability/ — I-6 观测可测性

| 文件 | 内容 |
|------|------|
| [signal-analysis.md](07-observability/signal-analysis.md) | I-6 信号可观测性分析 |

### 08-synthesis/ — 综合结论

| 文件 | 内容 |
|------|------|
| [conclusion.md](08-synthesis/conclusion.md) | **最终结论**：回答老师调研问题 |

### archive/ — 旧版本归档

| 类型 | 文件 |
|------|------|
| 关键版本求解器 | `d1-qbh-qnm-solver-v{6,10,11,20,23,25}.py`（6 个关键版本） |
| 旧运行记录 | `05-v21-kerr-fdtd-run-OUTDATED.md`, `06-i4-kerr-v21-run-results-OUTDATED.md` |
| Python 脚本 | `d1-p0-kerr-qnm-scan.py`, `diagnose_v10.py` |

**其他求解器版本（v7-9, v12-19）仅保留代码，无独立分析文档。**

---

## 逻辑链总览

```
文献调研 (01-literature)
  → 理论框架 (02-theory)
    → 求解器迭代 (03-numerical-method/01-solver-iteration-history.md)
      → Leaver(v6-10) NaN → Shooting(v11-13) RK4卡死 → FDTD(v20) 稳定
    → 基准验证 (04-benchmark) — FDTD v20 误差<1%
    → Kerr 扩展 (05-kerr-extension) — v22/v23 发现 aω<~0.7 框架有效
    → 面积量子化 (06-area-quantization) — I-5 负结果
    → P0 扫描 (06-kerr-qnm-scan) — 36 组 Kerr QNM
    → 观测可测性 (07-observability) — I-6 回答老师
      → 综合结论 (08-synthesis) — 最终交付
```

---

## 外部状态源

| 文件 | 用途 |
|------|------|
| [tasks/TASKS.md](../tasks/TASKS.md) | 任务状态（唯一状态源） |
| [INDEX.md](../INDEX.md) | 项目级索引（目录入口） |

---

*origin: ai — 2026-06-12 重构*
*逻辑链：从结论追溯→按需深入→求解器故事只在一个文件*
