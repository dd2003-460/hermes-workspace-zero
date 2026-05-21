# Projects — 工作区项目索引

**最后更新**: 2026-05-19（persona-align T3 完成, DPA.1 状态更新）

---

## 项目分类（按领域学科）

### 理论物理

| 项目 | 索引号 | 描述 |
|------|--------|------|
| `D1-grav-waves/` | [GW.1] | **arXiv 就绪 v4**：Extended Functorial QFT 框架用于 PTA 引力波源判别（10页/303K，24 refs，Round 11 审查 15/15 修复完成） |
| `D1-anyon-hawking/` | [AH.1] | 视界上的任意子拓扑动力学 — **原始研究**：任意子统计、纽结理论、黑洞视界（有探索笔记，无论文产出） |

### AI / 计算科学

| 项目 | 索引号 | 描述 |
|------|--------|------|
| `D1-persona-align/` | [DPA.1] | **T1-T5b 完成，T6 部署**：scorer + chenglu personality + 68 LoRA samples |
| `D1-academic-AI/` | [DAI.1] | **arXiv 就绪**：DistCat 2-Cat 统一框架（2-范畴距离导出，13页/298K）、Chimera 动力学、D40 AI 精度-可访问性权衡 |
| `D1-academic/bayesian-frame/` | [DA.0.1] | **arXiv 就绪 v2.0**：Bayesian 感知推理框架（|sin(4θ)| 为核心发现，11页/871K，JCR 论文） |
| `cosmos-thesis-review/` | [CTR.1] | 宇宙学关联函数 180页博士论文评审（已完成） |

### 写作 / 系统

| 项目 | 索引号 | 描述 |
|------|--------|------|
| `D1-writing/` | [DW.1] | 写作/输出相关工作 — **⚠️ 与 D1-academic/学术/写作/ 86% 重叠**，建议保留 D1-writing |
| `D1-memory/` | [DM.1] | 记忆系统（用户配置、探索归档、系统状态） |
| `D1-continuous-agent/` | [CA.1] | Agent 持续循环机制研究 — stop hook 分析、Hermes 兼容层探索 |

---

## workspace 顶层（基础设施）

| 路径 | 描述 |
|------|------|
| `CLAUDE.md` / `AGENTS.md` / `SOUL.md` | 全局原则 + 红线约束 |
| `loop/` | Ralph loop 框架（1-loop/ 2-loop/） |
| `scripts/` | 自动化脚本 |
| `tasks/` | 全局任务板 |
| `wiki/` | 领域知识文档 |
| `tools/` | 工具脚本（search_web.py 等） |
| `TASKS.md` / `MEMORY.md` / `README.md` / `USER.md` | 系统文件 |

---

## 递归索引可达性

从 `projects/INDEX.md` → 各项目 `INDEX.md` → 各子层 `INDEX.md` → 每个 paper/idea 应层层可达。

---

*按 CLAUDE.md 原则：创建文件前必须检查存在性、层级限制和索引更新*
