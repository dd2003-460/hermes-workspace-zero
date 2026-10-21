# origin: ai
# 三类语料分文件夹 · 针对性蒸馏（2026-10-21）

按「输入/输出/社交」三类分开，各自独立蒸馏，目标是像 clonar v2 一样像。

## 目录

| 文件夹 | 类型 | 内容 | 蒸馏目标 |
|--------|------|------|----------|
| `ai-chat/` | 我对 AI 的**输入** | 和 AI 聊天时我说的话（基本是问问题，因为我懂的不多） | 聊天风格（已有 clonar v2） |
| `writing/` | 我的**写作输出** | main 第一个 chapter 第一节（生存的偶然性） | 写作风格（新蒸馏） |
| `social/` | 我和别人的**社交聊天** | 互相交流，亲疏不同（待成璐提供） | 社交风格（占位，等语料） |

## 语料清单

### ai-chat/（AI 聊天输入）
- `corpus_input.txt` — 86 条 / 89K 字，29 条唯一用户消息（源自 author-voice-mining 语料）
- 已蒸馏：`../distill-style-repos/output_clonar_escrita.md`（MAP/REDUCE）
- v2 改进：`../distill-style-repos/output_clonar_v2_improvements.md`（去腔调+去重复）
- 盲测场景：`../../tasks/scenario-raw/`（GT 10 组 + S1/S2/S3）

### writing/（写作输出）
- `ch1-s1-生存的偶然性-raw.tex` — 第一个 chapter（存在或者毁灭）第一节，L41-97
- 源：`projects/写作-社会系统/D1-writing/motivation_society/archive/refactor-workspace-2026-10-05/corpus_raw/part1_core_logic_chapter1_nature_motivation.tex`
- 蒸馏：待做（用 clonar MAP/REDUCE 方法蒸馏写作风格）

### social/（社交聊天，占位）
- 待成璐提供「我和别人聊天（互相交流，社交，亲疏不同）」的语料
- 收到后按同样方法蒸馏

## 蒸馏方法（统一）
1. **MAP**：逐条/逐段提取风格特征（词汇/句法/语气/篇章/修辞/情感/视角/格式）
2. **REDUCE**：合并成 style_guide + system_prompt + few_shot
3. **去腔调**（v2 规则）：去 AI 腔调、去实质性重复、让 AI 输出自己的思考不用额外腔调
4. **盲测**：选场景，用蒸馏 prompt 生成，和 GT 对比

## 关键区分
- **AI 聊天**：单向提问为主（我不懂→问），语料短、碎片、问号多
- **写作**：长文、论证、有结构（章节/小节/tcolorbox），语料长、逻辑链
- **社交**：双向交流、有情绪、亲疏不同（待补充）
