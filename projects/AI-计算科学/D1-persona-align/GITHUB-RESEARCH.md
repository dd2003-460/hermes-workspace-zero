# GitHub 蒸馏方法论调研

> origin: ai | 2026-07-20 | 目的：为「完整复刻成璐」寻找并验证可复用的开源方法论
> 方法：curl api.github.com/search/repositories + 逐仓库读 README（web_search 工具缺 DEEPSEEK_API_KEY 不可用，改用 GitHub REST API 直接搜）

## 一句话结论

GitHub 上「蒸馏出个人 / 让 AI 成为你」这条线已经收敛到一个范式：**SOUL.md / identity-file 范式**。
最佳实践来自 4 个互补仓库，本项目直接采纳其结构与方法。

## 关键仓库（按相关度排序）

| 仓库 | 一句话 | 采纳了什么 |
|---|---|---|
| **raunakkathuria/iclone** | "Clone yourself into a git repo — your identity, judgment, and writing voice as plain files an AI can read" | **结构**：`identity/`(薄索引) + `skills/`(实体) + `memory/`。核心模式原话：*"identity files are a thin index; the skills hold the substance; one source of truth per thing."* |
| **alchaincyf/nuwa-skill** | "reconstruct how a person **THINKS**, not copy vocabulary — extract mental models, decision heuristics, values, communication patterns, behavioral boundaries, recurring ways of reasoning" | **思路层方法论**：复刻"怎么想"，不是复刻"说过什么"。本项目 how-i-think + work-habits 两层正是干这个。 |
| **Twynzen/soul-md** | 经验指南，8 层 SOUL.md 架构，27+ 生产 agent | **8 层架构 + 漂移重锚**。三条改变认知的发现见下。 |
| **relunctance/soul-forge** | 记忆演化系统，自动更新 SOUL/USER/IDENTITY/MEMORY/AGENTS/TOOLS.md | **持续演化触发条件**：同模式≥3 次 / 用户纠正≥2 次 / 新偏好 / 里程碑 → 更新。本项目 memory/ 按此演化。 |

辅助参考：
- **artttj/awesome-agent-personas** — 总索引（Persona Distillation / Cognitive Clones / Chinese Agent Ecosystem 分节）。
- **AntonioTF5/soul-spec** — SOUL.md 开放文件格式 spec + JSON schema + validator。
- **iamnotagamer46/context-optimizer** — 审计/打分(CHS 0-100)/重写 SOUL.md、AGENTS.md、MEMORY.md、USER.md。
- **Valeneunemployable6106/awesome-persona-skills** — 中文 persona / 角色 / agent skill 项目合集。
- **muneeb61/Digital-Personality-Clone** + **MohdAbdulRah/PersonaTwin** — 从 WhatsApp 聊天记录克隆人格（NLP+RAG+LLM），验证"从交互数据蒸馏"可行。

## soul-md 的三条改变认知的发现（2024–2026 学术）

1. **persona 漂移是数学上必然的**（Li et al., COLM 2024）：~8 个对话轮内即出现显著漂移，原因是注意力对初始 system-prompt token 的衰减。→ **结论：设计用于"恢复/重锚"，不是"预防"。** 本项目 persona.md 内置"重锚清单"。
2. **persona 不提升事实准确度**（Zheng et al., EMNLP 2024，162 个 persona）：对性能的影响基本随机。→ **SOUL.md 的真正价值 = 品牌一致性 + 语气对齐 + 行为可追溯**，不是"更强"。本项目目标是"像成璐"，不是"比成璐强"。
3. **SOUL.md 是攻击向量，不是防御**（Zhang et al. 2025）：对抗性 persona 调制可降 50–70% 拒绝率。→ 安全靠架构层（工具限制/只读挂载/输出分类器），不靠把身份文件写好。本工作区已有 sandbox 只读策略兜底。

## 成璐现有资产的映射（对齐 > 新建）

| 复刻层 | 现状 | 本项目动作 |
|---|---|---|
| 语言/voice | ✅ `projects/写作-社会系统/author-voice-mining/outputs/author-voice/SKILL.md`（122L，语料 271 条 26.4 万字，含真实统计特征） | 复用，how-i-write.md 做薄索引指向它 |
| 思维/方法论 | ✅ 根 `AGENTS.md`（思考方式/Plan五步/自我质询/置信度驱动） | 不复制，how-i-think.md 做薄索引 + 补 nuwa 式"心智模型/启发式"提炼 |
| 工作习惯 | ⚠️ 散在 AGENTS.md（任务优先级/Red Lines/默认决策画像）+ 语料里的任务 brief 习惯 | **新建** skills/work-habits/SKILL.md（这是缺失的实体层） |
| 身份整合 | ⚠️ AGENTS.md 是全局 SOUL，但不是"薄索引+技能"结构，也没有重锚机制 | **新建** persona.md（8 层整合 + 漂移重锚） |

> 红线遵守：AGENTS.md 非临时内容**禁止修改**。本包是 AGENTS.md 的**补充与操作化**，不替换。
