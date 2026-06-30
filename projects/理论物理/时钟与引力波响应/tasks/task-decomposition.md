# 任务分解：OLC ORF 频率依赖分析

## DAG 结构

```
Task 1 (读公式) ──→ Task 2 (实现 H12) ──→ Task 3 (验证公式) ──→ Task 4 (Pan(t) 平均)
                                                     │                                    │
                                                     ▼                                    ▼
                                              Task 5 (Pan-free ORF sweep)    Task 6 (Pan(t) ORF sweep)
                                                     │                                    │
                                                     └──────────────────┬─────────────────────┘
                                                                        │
                                                                        ▼
                                                               Task 7 (f-L 热力图)
                                                                        │
                                                                        ▼
                                                               Task 8 (结论提取)
```

## 子任务详情

### Task 1: 读 Hu PRD 公式提取
- **目标**：从 Hu PRD 提取的公式中，摘录 ORF 计算所需的全部公式和参数
- **输入**：`/tmp/hu_prd.txt`
- **输出**：`memory/01-olc-orf-formulas.md`（公式清单 + 参数定义）
- **验证**：公式编号与 Hu PRD 原文对照，含关键参数取值范围
- **回滚**：无副作用，文件可删
- **置信度**：0.95

### Task 2: 实现 H12 (单向 link ORF)
- **目标**：Python 实现单向 link ORF H_{12}(f,n)
- **输入**：Task 1 的公式清单 + Hu PRD 公式 (28)
- **输出**：`scripts/olc_h12.py`
- **验证**：100 个随机 (f, L, n) 点与解析公式数值比对，相对误差 < 1e-10
- **回滚**：`cp olc_h12.py backups/01/`
- **置信度**：0.9

### Task 3: 验证公式实现（基准测试）
- **目标**：与 Hu PRD 已有结果对比
- **输入**：Task 2 的 H12 代码 + Hu PRD 图 2 (PTA case, a=166.5 Mpc arms)
- **输出**：`memory/02-olc-orf-validation.md`（对比图 + 误差分析）
- **验证**：PTA 情况下 fL/c < 0.1 区域 ORF 值匹配 Hu PRD 图 2 到 5%
- **回滚**：同上
- **置信度**：0.85

### Task 4: 实现 P_{an}(t) 平均（旋转平均）
- **目标**：对任意构型做时间平均（arm 随探测器旋转）
- **输入**：Hu PRD 公式 (44)-(46)（P_{an} 矩阵）+ Task 2 的 H12
- **输出**：`scripts/olc_orf_full.py`（完整 ORF 计算）
- **验证**：PTA coplanar polygon 下 Hu PRD 的 HD 曲线匹配
- **回滚**：备份到 backups/02/
- **置信度**：0.85

### Task 5: Pan-free ORF sweep（固定臂长的频率扫描）
- **目标**：对固定臂长 L，扫描频率得到 ORF(f) 曲线
- **输入**：Task 4 的代码
- **输出**：`memory/03-olc-orf-sweep-noan.md`（ORF vs f 曲线图）
- **验证**：至少扫描 L=1, 5, 10, 50, 100 米，每个 L 扫描 [10^{-15}, 10^3] Hz
- **回滚**：无
- **置信度**：0.9

### Task 6: Pan(t) ORF sweep（含旋转平均的频率扫描）
- **目标**：对固定臂长 L，扫描频率得到 ORF(f)（含旋转平均）
- **输入**：Task 4 的代码
- **输出**：`memory/04-olc-orf-sweep-an.md`（含旋转平均的曲线）
- **验证**：对比 Task 5 和 Task 6 的差异（无旋转 vs 有旋转）
- **回滚**：无
- **置信度**：0.9

### Task 7: f-L 热力图（最终输出）
- **目标**：f-L 二维热力图，展示 ORF 随频率和臂长的变化
- **输入**：Task 5/6 的数据
- **输出**：`memory/05-olc-orf-flood-heatmap.png`
- **验证**：至少展示三个典型构型的对比图
- **回滚**：无
- **置信度**：0.9

### Task 8: 结论提取
- **目标**：从数据中提取物理结论
- **输入**：Task 5-7 的结果
- **输出**：`memory/06-olc-orf-conclusions.md`（结论清单 + 关键数据点）
- **验证**：每个结论必须有具体数据支持（数值或图编号）
- **回滚**：无
- **置信度**：0.9

## 总置信度

整体任务通过概率：min(confidence) = 0.85，足够进入 2-loop 执行。

---

## 已完成任务清单 (截至 2026-06-28)

| Task | 名称 | 状态 | 日期 |
|------|------|------|------|
| T1 | 读 Hu PRD 公式提取 | ✅ 完成 | 2026-06-28 |
| T2 | 实现 H12 | ✅ 完成 → 演化为 01-olc-orf-solver.py | 2026-06-28 |
| T3 | 验证公式实现 (5 项验证) | ✅ 完成 | 2026-06-28 |
| T4 | Pan(t) 平均 | ✅ 完成 (方位角平均替代) | 2026-06-28 |
| T5 | Pan-free ORF sweep | ✅ 完成 (heatmap) | 2026-06-28 |
| T6 | Pan(t) ORF sweep | ✅ 完成 (同 T5，平面部署等价) | 2026-06-28 |
| T7 | f-L 热力图 | ✅ 完成 → final_heatmap.py | 2026-06-28 |
| T8 | 结论提取 | ✅ 完成 → memory/03-olc-orf-results-summary.md | 2026-06-28 |
| N1 | 噪声谱 (Allan 方差) | ✅ 完成 | 2026-06-28 |
| N2 | GW 应变灵敏度曲线 | ✅ 完成 | 2026-06-28 |
| N3 | 响应函数热图 | ✅ 完成 | 2026-06-28 |
| N4 | Sr 钟噪声模型 | ✅ 完成 | Allan 方差 + PSD | 2026-06-28 |
| N5 | SNR 综合计算 | ✅ 完成 → 结论: OLC 不适用于 SGWB | 2026-06-28 |
| N6 | LISA 灵敏度对比 | ✅ 完成 | 直接数值对比 |
| P2A-1 | 3D 构型参数化 (dihedral) | ✅ 完成 → 04-olc-3d-orf.py | 2026-06-29 |
| P2A-2 | Dihedral scan | ✅ 完成 | ORF 变化 762%，Im(G)=0 | 2026-06-29 |
| P2A-3 | f-d heatmaps (多 dihedral) | ✅ 完成 | 0°, 60°, 90° | 2026-06-29 |
| P2A-4 | Fixed geometry test | ✅ 完成 (bug fix) | 验证 Im(G)=0 对称性 | 2026-06-29 |
| P2A-5 | 结果摘要 | ✅ 完成 → memory/06-olc-3d-orf-results.md | 2026-06-29 | 2026-06-28 |
| P2B-1 | 探测需求求解器 (SNR=5 inversion) | ✅ 完成 → 05-olc-detection-requirements.py | 2026-06-29 |
| P2B-2 | 四参数扫描 (L, h_0, N, T) | ✅ 完成 | 缩放定律验证 | 2026-06-29 |
| P2B-3 | 检测阈值等高线 (h_0 vs L) | ✅ 完成 | olc_detection_boundary.png | 2026-06-29 |
| P2B-4 | 结果摘要 | ✅ 完成 → memory/07-olc-detection-requirements.md | 2026-06-29 |
| F1 | 基础假设挑战 (Schaffrath/Gaudio) | ✅ 完成 — ground-based OLC 终止 | 2026-06-29 |
| F2 | 结论整理写入 memory/08-olc-foundation-challenge.md | ✅ 完成 | 2026-06-29 |
