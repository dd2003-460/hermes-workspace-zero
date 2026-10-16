# Projects — 工作区项目索引

**最后更新**: 2026-10-16（结构整理：删除 4 个分解测试桩项目；顶层 D1-* 归入领域目录；写作-社会系统 提升为顶层领域）

> **活跃项目入口**: [ACTIVE.md](ACTIVE.md) — 自动聚合的 loop 状态面板（由 `scripts/aggregate-active.sh` 生成）
> 各项目固定路径: `<project>/loop-state.json`

---

## 项目分类（按领域学科）

### 理论物理

| 项目 | 索引号 | 描述 |
|------|--------|------|
| `理论物理/D1-grav-waves/` | [GW.1] | **arXiv 就绪 v6**：Extended Functorial QFT 框架用于 PTA 引力波源判别 |
| `理论物理/D1-anyon-hawking/` | [AH.1] | **arXiv 就绪 v4**：视界上的任意子拓扑动力学 |
| `理论物理/D1-area-quantized-black-hole-QNM/` | [AQ.1] | **loop it 13**：面积量子化黑洞QNM（Teukolsky+AIM路线） |
| `理论物理/D1-goal-investigation/` | [DGI.1] | **loop it 14**：Agent goal 机制 + loop状态管理研究 |
| `理论物理/cosmos-thesis-review/` | [CTR.1] | 宇宙学论文综述 |
| `理论物理/2026春复习/` | [CR.1] | 2026 年春季复习材料 |
| `理论物理/quantum-ec/` | [QEC.1] | 量子纠错（七阶段方法：预言落纸 + 跑模型复算验证） |

### AI / 计算科学

| 项目 | 索引号 | 描述 |
|------|--------|------|
| `AI-计算科学/D1-persona-align/` | [DPA.1] | Persona 对齐机制（8原则+6维度+3行为约束） |
| `AI-计算科学/D1-academic-AI/` | [DAI.1] | **arXiv 就绪**：DistCat 2-Cat 统一框架、Chimera 动力学 |
| `AI-计算科学/D1-academic/` | [DA.1] | 广义学术工作（BayesFrame、方法论工具、学术协作） |
| `AI-计算科学/D1-memory/` | [DM.1] | 记忆系统 |
|| `AI-计算科学/D1-continuous-agent/` | [CA.1] | Agent 持续循环机制 |
|| `AI-计算科学/D1-browser-auto/` | [DBA.1] | **待启动**：本地 AI 驱动 Playwright 操控浏览器与网页大模型对话 |
| `D1-ralph-field-centric/` | [DRF.1] | **待启动**：RALPH 字段中心化重构规划（放宽主 agent 限制、字段级流动、按字段派发调研 subagent，评估弱模型稳定性/质量） |
| `AI-计算科学/D1-gpu-inference-hardware/` | [DGH.1] | GPU 推理硬件优化空间研究（矩阵/tensor 硬件计算；推理场景硬件还能怎么优化） |
| `AI-计算科学/D1-gpu-research-2026/` | [DGR.1] | GPU 本地推理研究（2026，含 web-llm 交叉验证） |
| `AI-计算科学/D1-hintfree-decomposition/` | [DHF.1] | 无提示词目标分解（hint-free goal decomposition）实验 |
| `decomp/` | [DC.1] | **总目标**：通用任务分解 prompt（总目标与总计划见其 README）；7 个相关 GPU/分解项目归档于 `archive/`（映射表见 `archive/README.md`）；RALPH loop 驱动，台账 = `tasks/state.md`；远端 = dd2003-460/decomp-bench |

### 写作 / 社会系统

| 项目 | 索引号 | 描述 |
|------|--------|------|
| `写作-社会系统/D1-aging-economics/` | [DAE.1] | 老龄化对区域经济影响实证研究 |
| `写作-社会系统/D1-writing/` | [DW.1] | 写作工作 |
| `写作-社会系统/D1-writing/motivation_society/` | [DMS.1] | 《动机社会》中文书稿(ctex+xelatex)——RALPH 接管:干净编译 + 按 part1_core_logic 风格修缮后续 AI 生成章节；Stop 钩子强制分解+进度条 |
| `写作-社会系统/author-voice-mining/` | [AVM.1] | 作者声音挖掘（写作风格 data + scripts + outputs） |

---

## workspace 顶层（基础设施）

**说明**：workspace 顶层文件不在 projects/ 管理范围内，详见 `AGENTS.md`。

| 路径 | 描述 |
|------|------|
| `AGENTS.md` | 全局原则 + 红线约束 |
| `ralph-loop.global.md` | 全局循环指令 |
| `TASKS.md` | **唯一状态来源**（`/Users/a1-6/Desktop/workspace/TASKS.md`） |
| `scripts/` | 自动化脚本 |
| `wiki/` | 领域知识文档 |
| `memory/` | 系统记忆 |
| `skills/` | 技能定义 |
| `tools/` | 工具脚本 |
| `CLAUDE.md` / `README.md` | 系统文件 |

---

## 递归索引可达性

从 `projects/INDEX.md` → 各项目 `INDEX.md` → 各子层 `INDEX.md` → 每个 paper/idea 应层层可达。

*loop/ 目录已于 2026-06-10 删除，task.state.json 已于 2026-06-11 删除。2026-06-23 新增 loop-state.json + ACTIVE.md 面板。*

---

*按 AGENTS.md 红线 0 原则：创建文件前必须检查存在性、层级限制和索引更新*
