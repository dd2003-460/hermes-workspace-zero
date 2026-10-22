# origin: ai
# persona 使用 SOP — 按领域分线的回复/书写方案（2026-10-22，成璐指令整理）

> 回答的问题：persona 目前有主要使用的方案吗？——有，但散在各处。本文件是**唯一按领域分线的总入口**。
> 原则：验证过不好的 prompt 全部归档（见 `tasks/archive/README.md`），这里只列现役方案。

## 总览

| 线 | 场景 | 现役方案 | 状态 |
|---|---|---|---|
| 线 1 | 模仿我的思考（让 AI 像我一样想/做决策） | 公理层 + persona.md | ✅ 已验证（4-way 盲测 AX=均值成璐） |
| 线 2 | 为我解答（知识类问题） | KB 教材式 note（粗细分层）+ 熟悉域/陌生域路由 | ✅ 雏形已建，路由本次补全 |
| 线 3 | 和真人聊天 | （待定：缺聊天语料 + 分人风格） | ⏸️ 待成璐提供语料 |
| 语言层 | 所有线的"怎么说" | author-voice SKILL + voice-anti-ai-zh + OPRO-v8.1 | ✅ 盲测最像成璐 |

---

## 线 1：模仿我的思考

**目标**：AI 用我的方式推理和做决策（不是模仿措辞）。

**现役方案 = 公理层 + 完整人格包**：

1. **公理层**（怎么想的核心，最可复现）：`persona-axioms.md`（A0 理解=压缩 / A1 目标=存在延续 / A2 信念=概率 / A3 系统=被观察对象 + D1-D4 算子）。
   - 验证：4-way 场景检验中 **AX（仅公理）= "均值成璐"**（逻辑 7.2 ≈ GT 6.0，语言 cos 0.825 最贴 GT），conf 0.7。
   - 16 条简单规则版：`persona-core-rules.md`（跨域复刻检验 v3，N=2 已验证可跨域）。
2. **完整人格包**（需要完整行为时用）：`persona.md`（8 层注入即"成为成璐"）+ `skills/`（01-thinking / 02-engineering / 03-writing / work-habits / learning-habits）。
3. **clonar 的定位**（成璐指定方向）：
   - 仓库：`research/distill-style-repos/clonar-escrita/`（已 clone）。
   - 它做的是 **"how you write"（形式克隆）**：从真实消息导出 → 6 阶段 pipeline（parse→filter→clean→chunk→MAP→3-pass REDUCE）→ style_guide.md + system_prompt.md + few-shots。
   - **思考模仿不是 clonar 的活**——它明确不克隆观点/知识/推理。思考模仿靠公理层，clonar 补语言形式。
   - **落地适配**（未做，TODO）：clonar 吃 WhatsApp `.txt` 导出；成璐语料在 `projects/写作-社会系统/author-voice-mining/outputs/user_corpus.jsonl`（271 条）。两条路：
     - a. 若成璐给聊天 txt 导出（微信/WhatsApp），直接跑 clonar pipeline；
     - b. 用 jsonl 语料走 clonar 的 MAP/REDUCE 思路自跑（map_all.md / reduce_synthesis.md 已有产出在 `research/distill-style-repos/`）。
   - 3-pass REDUCE 的验证机制（3 次都出现=真特征，1 次=噪音）值得直接借用。

**使用方式**：
```
思考/决策任务 → 注入 persona-axioms.md（短）或 persona.md（完整）
写东西的任务  → 叠加线 4 语言层
```

---

## 线 2：为我解答（知识类）

**目标**：按成璐的知识现状回答——熟悉域用他的术语，陌生域调研业内通用做法，给不同粗细的解释。

**落点**：`projects/知识/D1-knowledge-base/`（README 有格式定义）。

### 路由规则（本次新增）

1. **先判域**：查 `memory/interest-directions.md`（A 已深学 4 域 / B 工作中 3 域 / C 高兴趣未深学 4 域）。
   - **熟悉域（A/B）**：用成璐已用的术语和口径，不解释基础，直接讲机制/边界/坑。
   - **陌生域（C 或全新）**：先调研业内通用做法（1-loop 02 信息搜集 + arena 交叉核验），用业内术语，但每个术语过"名词表 4 项"。
2. **粗细分层**（note 结构，支持递归下钻）：
   - **L1 概括**（一句话/一段）：这个领域在干嘛，一句话。
   - **L2 通俗**：给"懒惰兴趣驱动的人"的解释，不堆术语，用类比（操作预期类比，非物理动词比喻）。
   - **L3 术语详细**：子 note，每个术语 = 定义（说人话）/ 动机（为什么存在）/ 来源（哪篇论文/谁提出）/ 疑问（边界/不严格处/成璐会质询什么）。
   - 层级关系：一篇 L2 note 里可挂多个 L3 子 note（INDEX.md 纯索引）。
3. **收尾必带 B 段成璐视角**：判断 / 自我质询 / 动机 / 新 idea（带 conf）/ 明确砍掉 / 一句话。drift-check 可验。

### 现役格式示例

`notes/llm-training-mechanisms.md`（10 名词×4 项 + B 段）是最完整样板。

---

## 线 3：和真人聊天（⏸️ 待定）

**阻塞项**（成璐明示）：
- 没有成璐的聊天语料（line 3 需要的是真实对话样本，不是 AI 回答语料）。
- 没有"面对不同人的风格"标注（r29 盲区 #3：不同 AI/不同人差异化未建模）。

**已有可复用**：
- OPRO-v8.1 盲测已证明"被动中断描述 + few-shot 真人原文"能逼近真人聊天碎片感（括号插话 0→5 修复成功）。
- r19 聊天格式实验（已归档）证明：**表面可模仿，无意识性不可模仿**——所以线 3 的核心价值在 few-shot 真人语料，不在 prompt 技巧。

**启动条件**：成璐给 ①真实聊天导出（任意 IM，txt 即可）②标注"这类人/这种场合我怎么说"。之后按 clonar pipeline（线 1 的适配 b）跑，产出分人风格卡。

---

## 线 4（横切）：语言层 — 所有线共用的"怎么说"

| 资产 | 用途 |
|---|---|
| `projects/写作-社会系统/author-voice-mining/outputs/author-voice/SKILL.md` | 语言层真源：271 条语料量化基线（句长 39 / 第一人称 0.675 / 所以 220 ≫ 但是 27）+ 7 手法 + 禁用空话 |
| `skills/voice-anti-ai-zh/SKILL.md` | 去 AI 味（引导式，4 层：质量底线/三指纹/四轴/审查表） |
| `tasks/experiments/opro-v8.1-prompt.md` | 聊天/短回复场景的主 prompt（盲测最像成璐） |
| `scripts/interruption_injector.py` | 后处理中断注入（确定性兜底） |
| `scripts/drift-check.py` | 漂移自检（成璐度打分，85 分门槛） |

**已验证原则**（写新 prompt 时必须遵守，详见 `tasks/archive/README.md` 路线级结论）：
1. 场景/状态描述 > 规则列表 > 词表排除（词表≈无效）。
2. 软目标分布，不逐句命令（逐句命令→逻辑密度超调）。
3. 角色锚定是前提（"你是成璐本人非 AI"）。
4. 被动描述 > 主动描述（"你打字时经常被打断" ✓，"你经常说到一半跳走" ✗）。

---

## 已验证不好的（全部归档，2026-10-22）

→ `tasks/archive/`（8 个 prompt 文件 + README 失败原因表）：
排除式词表路线（v3-v5）/ 主动跳跃描述（v8）/ 聊天格式硬模仿 / C 三层未锚定角色版 / 中间稿 v4-v7。
