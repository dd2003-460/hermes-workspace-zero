# D1-generalization — LLM 泛化能力实证

**主题**：LLM 的压缩/泛化行为实证——自发跨域理论应用、调试策略 vs 信息论最优、"有能力 vs 懒得用"的区分实验。

**核心问题**：LLM 的跨域理论应用是"潜在但没触发"还是"没学到"？割裂在策略选择还是归纳容量？

---

## memory/（探索记录，不删）

| 文件 | 内容 |
|------|------|
| `codearc-smoke-27b-debugging-20261120.md` | 27b CodeARC 冒烟（n=5，调试=语义归纳非信息论最优，P4 trace） |
| `codearc-n20-rerun-20261120.md` | n=20 重跑 R1（63%） |
| `codearc-n20-clean-final-20261120.md` | n=20 两轮对比（均值 58% / 可靠解题率 44% / 翻转 28%；vs o3-mini 52.7%） |
| `collision-llm-debugging-info-theoretic-20261120.md` | 撞车调研（理论 2020 已有，实证 gap 存在）+ 主张修正（chat 测试+跨域探针反驳"不会自发用最优策略"） |
| `bench-coverage-collision-20261120.md` | bench 覆盖度撞车 |
| `crossdomain-probe-27b-20261120.md` | 跨域自发抽象探针（6/6 命中）+ edge 实验收口（翻转 1/5 → 瓶颈=归纳容量非策略） |
| `crossdomain-expdesign-claude-vs-27b-20261121.md` | 实验设计问题 27b vs Claude 对照 diff（D 的 bitter-lesson 评分修正两家均未自发给出） |
| `generalization-survey-snowball-20261121.md` | 泛化/跨域滚雪球调研（三条线×前沿：类比争议线/压缩-泛化线/动力系统线 + 5 个套磁对象 + 设计命中表） |
| `raw-outputs/` | 模型原始输出（对照实验素材，保留原文） |

## tasks/（临时状态）

- `decomposition.md` — 分解树 + 待办
- `outreach-sop-20261121.md` — **套磁 SOP**（5 阶段管线：发现→草稿→发送→follow-up→追踪复盘；抄 GitHub 3 工具范式，不重造轮子）
- `cold-email-design-20261121.md` — 套磁邮件模板（4 套 A-D）+ 发送纪律 + UCAS 邮箱 deliverability

---

*来源：2026-11-21 从 D1-persona-align/memory/ 迁出（D 指令：泛化类测试规整到主题下）。评测 SOP：skill `local-llm-bench-eval`。*
