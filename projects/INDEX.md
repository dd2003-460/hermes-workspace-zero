# Projects — 工作区项目索引

**最后更新**: 2026-05-05（领域学科重新分类：引力波/认知拓扑/理论物理标准化）

---

## 项目分类（按领域学科）

### 理论物理
| 项目 | 索引号 | 描述 |
|------|--------|------|
| `D1-grav-waves/` | [GW.1] | NANOGrav 引力波背景、PTA谱指数、范畴论在引力波中的应用 |
| `D1-academic-AI/` | [DAI.1] | Chimera动力学 + 认知拓扑 + 语言信息几何 + 代理自主性理论（D1-D52理论迭代） |

**D1-academic-AI 结构**：
```
D1-academic-AI/INDEX.md
├── papers/          → 已完成学术论文（约50篇）
├── theories/        → 理论迭代（chimera-dynamics/, cognitive-topology/, language-geometry/）
├── chimera_lab/     → 实验脚本 + 结果数据
├── raw/             → 原始ideas
├── labs/simulations/→ 仿真实验
├── memory/          → 探索记录（含 S9, S12, S18, D4, A1 等归档探索）
├── modules/         → 可复用代码模块
├── architecture/    → 系统设计文档
└── tasks/           → 任务状态 + 队列索引
```

### 计算/信息论
| 项目 | 索引号 | 描述 |
|------|--------|------|
| `D1-academic/` | [DA.0] | Bayesian 视觉推理计算框架 + 学术资料库 |
| `cosmos-thesis-review/` | [CTR.1] | 宇宙学关联函数 180页博士论文评审（已完成） |

**D1-academic 结构**：
```
D1-academic/INDEX.md
├── bayesian-frame/      → 后验推理计算框架
├── 学术/               → 论文PDF、笔记、翻译
│   └── 资料库/文献资料/理论物理/
│       └── (文献存储，cosmos-thesis-review 已独立)
```

### 写作/输出
| 项目 | 索引号 | 描述 |
|------|--------|------|
| `D1-writing/` | [DW.1] | 写作/输出相关工作 |

### 系统/记忆
| 项目 | 索引号 | 描述 |
|------|--------|------|
| `D1-memory/` | [DM.1] | 记忆系统（用户配置、探索归档、系统状态） |

---

## workspace 顶层（基础设施）

| 路径 | 描述 |
|------|------|
| `CLAUDE.md` / `AGENTS.md` / `SOUL.md` | 全局原则 + 红线约束 |
| `loop/` | Ralph loop 框架（1-loop/ 2-loop/） #workspace |
| `scripts/` | 自动化脚本 #workspace |
| `tasks/` | 全局任务板 #workspace |
| `wiki/` | 领域知识文档 #workspace |
| `TASKS.md` / `MEMORY.md` / `README.md` / `USER.md` | 系统文件 |

---

## 递归索引可达性

从 `projects/INDEX.md` → 各项目 `INDEX.md` → 各子层 `INDEX.md` → 每个 paper/idea 应层层可达。

---

*按 CLAUDE.md 原则：创建文件前必须检查存在性、层级限制和索引更新*
