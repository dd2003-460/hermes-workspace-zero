# D1-persona-align

**状态**: persona-v3 框架完整 (8 原则 + 6 维度 + 3 行为约束) + MATO DPA v2 + 三层评估 + 22 篇外部研究 + T1-T47 全部完成 + 动态工作流 4 种方案全部部署
**创建**: 2026-05-18
**最近更新**: 2026-06-02 (iteration 365)

## 子目录

| 目录 | 说明 |
|------|------|
| [tasks/](tasks/) | 任务文件 (T1-T47 全部完成) |
| [memory/](memory/) | 105 idea analyses + 187 iteration logs (1-365) + 21 external research reviews |
| [memory/archive/](memory/archive/) | 归档的早期文件 (v2-era, early-t2-era) |
| [raw/](raw/) | 原始研究素材 |
| [researches/](researches/) | 研究报告 + 独立论文总结 |
| - [Chimera-Frontier-Review-2024-2026.md](researches/Chimera-Frontier-Review-2024-2026.md) | Chimera 前沿综述 (8 papers, 2024-2026) |
| - [MetaCognitive-LLM-Review-2024-2026.md](researches/MetaCognitive-LLM-Review-2024-2026.md) | Meta-cognitive LLM 综述 (5 papers, 2025-2026) |
| - [MetaCognitive-AI-Review-2024-2026.md](researches/MetaCognitive-AI-Review-2024-2026.md) | Meta-cognitive AI 综述 (16 papers, 2024-2026) |
| - [Neural-Chimera-Review-2024-2026.md](researches/Neural-Chimera-Review-2024-2026.md) | Neural chimera 综述 (4 papers, 2024-2026) |
| - [MultiAgent-LLM-Frontier-2024-2026.md](researches/MultiAgent-LLM-Frontier-2024-2026.md) | Multi-agent LLM 前沿 (4 papers, 2024-2026) |
| - [LLM-Hardware-LongContext-Analysis.md](researches/LLM-Hardware-LongContext-Analysis.md) | 长文本 LLM 推理硬件分析 |
| - [Agent-Performance-Analysis.md](researches/Agent-Performance-Analysis.md) | Agent 性能需求分析 |
| - [MetaCognitive-Test-Chimera-Basin-Geometry.md](researches/MetaCognitive-Test-Chimera-Basin-Geometry.md) | Meta-cog prompt TEST 1: Basin geometry (expert-level validation) |
| - [MetaCognitive-Test-Neural-Chimera-Bridging.md](researches/MetaCognitive-Test-Neural-Chimera-Bridging.md) | Meta-cog prompt TEST 2: Neural chimera bridging (novel insight) |
| - [ThinkingPatterns-FrontierMapping.md](researches/ThinkingPatterns-FrontierMapping.md) | 11 思维模式 × 前沿研究系统性对照 (iteration 18) |
| [eval_results/](eval_results/) | 评估运行结果 JSON + 真实会话记录 (21 个文件) |
| [scripts/](scripts/) | 23 个活跃评估工具脚本 |
| [scripts/archive/](scripts/archive/) | 归档脚本 (30 个, INDEX.md 有完整说明) |
| [persona-evolve/](persona-evolve/) | persona-evolution 分析 |
| [memory/thinking-patterns-complete.md](memory/thinking-patterns-complete.md) | 成璐完整思维模式提取 (11 个模式 + Prompt 模板) |
| [meta-cognitive-research-prompt.md](meta-cognitive-research-prompt.md) | Meta-cognitive research prompt — 让任何 LLM 以成璐的思维方式探索研究 |

## 顶层文件

| 文件 | 说明 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | 项目约束 (5 条红线, 评估基线) |
| [README.md](README.md) | 系统文档 (迭代 267-360, 三模评估体系) |
| [persona-manifest-v3.txt](persona-manifest-v3.txt) | 8 原则最优提示词 (80 字符) |
| [persona-v3-prompt.txt](persona-v3-prompt.txt) | 完整 persona-v3 prompt (6 维度 + self-preservation + MATO DPA) |
| [persona-v3-evaluation-summary-2026-05-31.md](persona-v3-evaluation-summary-2026-05-31.md) | 完整评估报告 |

## 核心脚本 (scripts/)

### 统一评估管道

| 脚本 | 功能 |
|------|------|
| [unified_eval.py](scripts/unified_eval.py) | 一键 pipeline (gap + chameleon + trajectory + 语义 + 核心关键词) |
| [integration_test.py](scripts/integration_test.py) | 端到端集成测试 (11 项) |
| [regression_test.py](scripts/regression_test.py) | 回归测试 (编译 + 完整) |
| [persona_keywords.py](scripts/persona_keywords.py) | 共享关键词库 (DIMENSION_KEYWORDS + CORE_KEYWORDS) |
| [semantic_alignment_checker.py](scripts/semantic_alignment_checker.py) | TF-IDF + concept coverage 语义对齐评估 |

### 评估与检测

| 脚本 | 功能 |
|------|------|
| [persona_v3_gap_filler_v2.py](scripts/persona_v3_gap_filler_v2.py) | 加权匹配 + 语义增强 (--core 核心关键词注入) |
| [chameleon_collapse_detector.py](scripts/chameleon_collapse_detector.py) | 维度多样性检测 |
| [emptrajectory_eval.py](scripts/emptrajectory_eval.py) | 轨迹级评估 |
| [persona_v3_dashboard.py](scripts/persona_v3_dashboard.py) | 全局对齐度仪表盘 |
| [persona_v3_batch_enhance.py](scripts/persona_v3_batch_enhance.py) | 批量增强 idea 文件 |

### 测试时优化

| 脚本 | 功能 |
|------|------|
| [test_time_optimize.py](scripts/test_time_optimize.py) | MATO-inspired dynamic priority |
| [textbo_prompt_optimizer.py](scripts/textbo_prompt_optimizer.py) | TextBO greedy keyword optimizer |

### 其他工具

| 脚本 | 功能 |
|------|------|
| [sync_personality.py](scripts/sync_personality.py) | 同步 prompt 到 Hermse config |
| [section_alignment_test.py](scripts/section_alignment_test.py) | Section 级维度对齐测试 |
| [temporal_stability_test.py](scripts/temporal_stability_test.py) | 多轮对话稳定性测试 |
| [cross_dim_ortho.py](scripts/cross_dim_ortho.py) | 跨维度正交化实验 |
| [persona_v3_alignment_checker.py](scripts/persona_v3_alignment_checker.py) | 中文单文件对齐度检测 |
| [persona_v3_alignment_checker_en.py](scripts/persona_v3_alignment_checker_en.py) | 英文单文件对齐度检测 |
| [generate_analyses.py](scripts/generate_analyses.py) | 批量生成 idea 分析 |
| [quality_check.py](scripts/quality_check.py) | 质量检查 |
| [integrate_persona.py](scripts/integrate_persona.py) | 跨项目集成 |

## 递归索引

见各子目录 `INDEX.md`。
| - [Paper-Outline-Chimera-Stable-Attractors.md](researches/Paper-Outline-Chimera-Stable-Attractors.md) | Chimera 论文提纲 (6 contributions, PRL/Chaos target) |
| - [Agentic-AI-Frontier-June-2026.md](researches/Agentic-AI-Frontier-June-2026.md) | Agent 前沿综述 (6 papers, June 2026) || - [Neural-Chimera-Review-2024-2026.md](researches/Neural-Chimera-Review-2024-2026.md) | 神经网络 chimera 综述 (4 papers, 2024-2026) || - [MultiAgent-LLM-Frontier-2024-2026.md](researches/MultiAgent-LLM-Frontier-2024-2026.md) | 多智能体 LLM 综述 (4 papers, 2024-2026) || - [MetaCognitive-AI-Review-2024-2026.md](researches/MetaCognitive-AI-Review-2024-2026.md) | Meta-cognitive AI 综述 (16 papers, 2024-2026) || - [MetaCognitive-Test-Chimera-Basin-Geometry.md](researches/MetaCognitive-Test-Chimera-Basin-Geometry.md) | Meta-cognitive prompt 测试 (basin geometry, 结论与专家一致) |