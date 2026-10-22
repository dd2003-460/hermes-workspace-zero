# D1-persona-align — 项目结构索引

**origin: ai** · 2026-10-21（结构整理时新建，补 AGENTS.md 红线 0 标准结构；内容以各文件为准）

> 纯索引：只描述下一层有哪些目录/文件。先读 `persona.md`（入口）与 `loop-state.json`（进度）。

| 路径 | 说明 |
|------|------|
| `persona.md` | 人格入口（L1-L8 层定义） |
| `persona-sop.md` | **按领域分线的使用 SOP（总入口）**：线1模仿思考/线2知识解答/线3真人聊天(待定)/线4语言层横切 |
| `persona-core-rules.md` | 16 条简单规则（跨域复刻检验 v3） |
| `persona-axioms.md` | 公理层完整推导链（16 条导出表；最短版见 AGENTS.md 公理层节） |
| `unification-first-principles.md` | 统一框架第一性原理 |
| `thinking-budget.md` | 思考预算协议（L0/L1/L2；最短版见 AGENTS.md） |
| `GITHUB-RESEARCH.md` | GitHub 成熟方案调研记录 |
| `identity/` | who-i-am / how-i-think / how-i-write（身份三层） |
| `skills/` | persona 技能树：SKILL.md 根 + 01-thinking / 02-engineering / 03-writing + voice / work-habits / learning-habits |
| `research/` | 语料与蒸馏：corpus / distill-style-reports / distill-style-repos / human-vs-ai-input |
| `tasks/` | 当前临时状态：decomposition.md（行动分解 r16）+ experiments/（现役 prompt：opro-v8.1 等）+ archive/（已验证不好的 prompt 归档，带失败原因表）+ scenario-raw/（情景引导 GT/S1-S3） |
| `memory/` | 探索记录（完整，不可删除）：复刻检验 v1-v3、delivery-report r25/r29/r30、qanda-ledger、persona-crosscheck-claude 等 |
| `loop-artifacts/` | 1-loop 阶段产物：stages/ + retro-test/ + open-questions.md |
| `scripts/` | drift-check.py / scenario-score.py / interruption_injector.py |
| `loop-state.json` | loop 进度指针（r31，T45 待最终交付） |
