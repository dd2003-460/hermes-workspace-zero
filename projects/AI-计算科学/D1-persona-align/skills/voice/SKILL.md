# voice — 路由层（thin pointer）

> origin: ai · 本文件只做路由，不存实体。one source of truth 在别处，避免重复。

## 真源（唯一）
语言层实体在 **author-voice-mining** 项目，不在本目录：
- `projects/写作-社会系统/author-voice-mining/outputs/author-voice/SKILL.md`（写作 SKILL，含 7 标志手法 + 反面清单 + 自检）
- `projects/写作-社会系统/author-voice-mining/outputs/voice_features.md`（271 条 / 26.4 万字实测数字：句长39/第一人称0.675/所以220 vs 但是27/可能207/应该67）
- `projects/写作-社会系统/author-voice-mining/outputs/user_corpus.jsonl`（271 条原始语料）

## 本项目的量化工具
`projects/AI-计算科学/D1-persona-align/scripts/drift-check.py` — 把 voice_features.md 的目标数字变成可跑的 0-100 成璐度得分（persona L7 漂移重锚用）。

## 用法定位
- 要"写得像成璐" → 读 author-voice SKILL
- 要"验证写得像不像成璐" → 跑 drift-check.py
- 本文件只负责让人/AI 知道去上面两个地方
