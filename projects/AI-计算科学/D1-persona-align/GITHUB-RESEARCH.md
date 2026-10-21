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

## r15 补充: 去AI味方案对比 (2026-10-19)

> 来源: 1-loop 02 调研（r15 轮），3 个去AI味方案的要点与关系。为 T2 任务 voice-anti-ai-zh.md 提供框架依据。

### 3 方案对比

| 方案 | 层级 | 规则数 | 优势 | 风险 | 定位 |
|---|---|---|---|---|---|
| **clearmode** (eugeniughelbur/clearmode, 英文, MIT, 零依赖) | 总框架/编辑验收 | 4轴 + 43规则 (P1-12/H1-16/S1-10/D1-5) | 最完整: 4轴权重(Plain30/Human30/Structured25/Dense15) + 单JSON编译所有target(skill/AGENTS.md/Cursor/Vale/system prompt) + 量化scoring(start100, error2.0x/warn1.0x/review0.4x, 每250词归一, gate_default=80) | 纯英文, 中文AI味指纹不同("值得注意的是/综上所述" vs delve/leverage) | ★最匹配。借框架结构, 词表另建中文 |
| **Voice DNA** (shaswatco/anti-ai-writing-style, 英文, npx安装) | 核心风格诊断层 | 3结构性指纹 + banned words 90+ | 针对性强: ①Metronome Rhythm(句长均匀15-20词) ②Puffery&Significance Inflation(testament/realm/tapestry) ③Negative Parallelisms("This isn't just X; it's Y"=单一最大统计指纹) | 规则少, 覆盖面窄, 英文 | 诊断层: 与clearmode四轴不冲突, 互补 |
| **Humanizer-zh-academic** (Smith-2758, 27星, 中文学术) | 交互式skill | 5规则类别(学术卖弄/机械句法/空洞总结/高危排版/AI检测逻辑) | 唯一中文方案: 先确认严肃度+角色再改写, 借鉴 op7418/Humanizer-zh + Wikipedia "Signs of AI writing" | 核心 SKILL.md 未深读(需后续补), 定位学术写作 | 压回真实学生写作(朴实严谨自然, 不空泛不装腔) |

### 关键洞察

1. **英文方案需中文化** — 中文AI味指纹与英文不同: 英文是 delve/leverage/testament, 中文是"值得注意的是/综上所述/不难发现/赋能/抓手"。借框架结构(4轴权重+分层规则), 词表必须另建中文。
2. **分层不冲突** — clearmode 4轴 = 总框架/编辑验收层; Voice DNA 3指纹 = 诊断层(规则少针对性强); 词表 = 后处理检查器。三者是分层关系, 不是竞争。
3. **clearmode 核心规则速记** — H6 No negative parallelism (ERROR, "it's not just X; it's Y"=单一最强AI指纹) / H13 Vary sentence length (打破metronome) / H11 Name the source or drop the claim / D1 Delete test (无数字/名/机制/后果=填充) / D3 No throat-clearing opener (ERROR, 首句别浪费setup) / H12 No assistant voice (ERROR)
4. **clearmode 词表规模** — slop_words~100 (delve/realm/harness/unlock/tapestry/paradigm/cutting-edge/revolutionize/leverage/synergy/game-changer/testament/foster/showcase/holistic/burgeoning/ubiquitous...) / slop_phrases~70 (in today's fast-paced/at the end of the day/sheds light on/dive deep/here's the thing...) / banned_openers (Furthermore/Moreover/Additionally/Notably/Importantly/Certainly/Undoubtedly...)
5. **clearmode profiles** — general(句25/段4/grade9) / technical(28/5/11) / social(20/2/8) / agent(20/6/9)

### 与本项目关系 (T2 voice-anti-ai-zh.md)

- 借鉴 **clearmode 4轴结构** (Plain/Human/Structured/Dense 权重框架) + **Voice DNA 3指纹** (Metronome/Puffery/Negative Parallelisms 诊断层)。
- **词表换成中文**: 不用 clearmode 的 slop_words, 另建中文AI味词表("值得注意的是/综上所述/不难发现/赋能/抓手/闭环/对齐/拉齐/沉淀..."等)。
- **成璐语料"不是…而是"96次 = 高负载纠偏**: 不列入禁表(语料高频, 禁了会扭曲语体), 列入审查表, 用三票制判别(是否真冗余/是否有对比信息量/是否可换更短表达)。
- Humanizer-zh-academic 的交互模式(先确认严肃度+角色)可借鉴为 T2 的可选入口。

