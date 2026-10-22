# 领域知识图谱

> origin: ai · goal-32d9335d round 2 · 各项目的关系、依赖、当前阶段

## 项目全景

```
workspace/
├── projects/
│   ├── decomp/                    # 分解能力测试（T4 消融实验）
│   │   ├── bench/prompts/variants/  # C0/C1-small/C2-expos/C9-plain/C9-open
│   │   ├── bench/runs/             # σ-baseline + ablation-L1 + _arena-battle
│   │   └── loop-state.json         # iteration 1, status active
│   ├── AI-计算科学/
│   │   ├── D1-persona-align/      # persona 对齐（T45 实验设计）
│   │   │   ├── research/           # arena-robustness/decomposition-orthogonality/s2-s3-challenge
│   │   │   ├── knowledge/          # decision-preferences/efficiency-bottlenecks/domain-graph
│   │   │   └── loop-state.json     # iteration 36, status active
│   │   ├── D1-gpu-inference-hardware/  # GPU 推理硬件（RALPH 格式）
│   │   │   └── loop-state.json     # iteration 900, status running
│   │   ├── D1-ai-for-mat-science/  # AI 材料科学
│   │   ├── D1-academic-AI/         # 学术 AI
│   │   ├── D1-quantum/             # 量子
│   │   ├── D1-computational-biology/  # 计算生物学
│   │   └── D1-* (其余 D1 项目)
│   ├── 媒体/                      # 视频渲染（Step E）
│   ├── 理论物理/                   # orf + bh-spectrum（保留）+ 其余 deprecated
│   └── INDEX.md                   # 项目索引
├── AGENTS.md                       # 全局规范（红线/思考预算/工具优先）
├── projects/ACTIVE.md              # 活跃项目面板（自动聚合）
└── 个人/                           # APPROVALS.md + APPROVALS-TEMPLATE.md
```

## 项目依赖关系

```
decomp (T4 消融)
  ├── 依赖: arena 通道（ego-browser）→ P1 瓶颈
  ├── 产出: TEST-CATALOG.md + 14/33 份 run 数据
  └── 阻塞: arena 通道系统性失败（P1）

persona-align (T45 实验设计)
  ├── 依赖: experiment-design-t45.md（MISSING）+ API key + 样本
  ├── 产出: research/（S1-S5 瓶颈分析）+ knowledge/（决策偏好/效率瓶颈/领域图谱）
  └── 阻塞: experiment-design-t45.md MISSING（r12 BLOCKED）

gpu-inference (RALPH 格式)
  ├── 依赖: RALPH 格式（Commander 模式）+ ralph apply
  ├── 产出: loop-artifacts/stages/04.5/r1/web-llm/（先例）
  └── 阻塞: RALPH 格式需 ralph apply（r4 BLOCKED）

媒体 (Step E)
  ├── 依赖: 渲染 SOP（rendering-sop.md 已落盘）
  ├── 产出: ffmpeg 帧序列方案（Remotion 弃用 D6）
  └── 阻塞: 无（可执行）

area-quantized (deprecated)
  ├── 依赖: RALPH 格式 + 网络 + 计算
  ├── 产出: task.md（RW 框架失效 a>0.90, Teukolsky+AIM 唯一路径）
  └── 状态: deprecated（m01404 标记）
```

## 当前阶段

| 项目 | 阶段 | 状态 | 阻塞 |
|------|------|------|------|
| decomp | T4 消融（14/33 份） | active | P1 arena 通道 |
| persona-align | T45 实验设计 | active | experiment-design-t45.md MISSING |
| gpu-inference | RALPH 格式 | running | ralph apply |
| 媒体 | Step E（渲染 SOP） | active | 无 |
| area-quantized | deprecated | deprecated | — |

## 效率瓶颈 → 项目映射

| 瓶颈 | 受影响项目 | 优先级 |
|------|-----------|--------|
| P1 arena 通道 | decomp | 最高 |
| P2 goal 结束太快 | 全部 | 高（已修） |
| P3 项目优先级不对 | 全部 | 高（已修） |
| P4 subagent 并发限制 | 全部 | 中（不可修） |
| P5 思考 token 预算 | 全部 | 中（已内化） |

## 给 Lead 的建议

- 每轮开始前，查本图谱，确认项目依赖 + 当前阶段
- P1 未修 → 不派 arena subagent（decomp 阻塞）
- 媒体无阻塞 → 可执行（Step E 渲染 SOP）
- area-quantized deprecated → 跳过
