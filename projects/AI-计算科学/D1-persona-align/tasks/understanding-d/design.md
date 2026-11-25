# origin: ai
# understanding-d 设计（阶段 02）— 采集/整合型 goal，改动项 = 新产出文件 + 通道
# 原则：全部只增不删，回滚 = git revert / 删文件；不动任何既有文件内容（除台账追加）

## 改动项表
| ID | 目标文件 | 改动 | 回滚 | 验证（前后对照） |
|----|---------|------|------|----------------|
| T1 | projects/AI-计算科学/D1-persona-align/tasks/understanding-d/idea-inventory-v1.md | 新建：工作区 idea/猜想盘点，≥40 条，每条 = 标题+一句话+来源路径+原文引用≤30字+状态(已做/在做/未做) | 删文件 | 前=文件不存在；后=存在且 `grep -c "^### " file` ≥40，随机抽 5 条 grep 原文引用可命中源文件 |
| T2 | tools/objfunc/signal-classification-v3.json + objfunc-signal-log.md 追加 | 11 月增量信号：extract→过滤→27b 粗筛→Lead delta | 删 v3 json + git revert 台账 | 前=v2 无 2026-11 stats；后=v3 stats.monthly 含 2026-11 且 signals 新增条目 quote 可 grep 回 state.db |
| T3 | tools/objfunc/imap-test-receipt.json + 脚本 | 新建：IMAP 测试拉取脚本+回执（Google+QQ） | 删文件 | 前=无通道；后=回执含 fetched_subject+date，脚本可重跑 |
| T4 | projects/AI-计算科学/D1-persona-align/memory/general-thinking-template-v2-*.md | 新建：语料思考模式挖掘产出（≥5 条新思考习惯+原文证据） | 删文件 | 前=template 停在 20261124 版；后=v2 存在且每条习惯的 quote 可 grep 回 corpus/ 原文 |

## 正交性
T1(工作区 idea) / T2(直聊信号) / T3(邮件通道) / T4(AI 对话语料) 四个数据源互不重叠；产出文件互不覆盖。
## 依赖
T3 依赖 D 提供 app password（blocked-on-D，不阻塞其他）；T1/T2/T4 可并行（不同 sub，但 T2 粗筛占 vLLM → T2 粗筛与 T1 不并发跑 27b，T1 纯读文件不碰 8787，可并发）。
## 执行顺序
T1(sub, 纯读) ∥ T4(Lead, 纯读) → T2(sub 粗筛 27b → Lead delta) → T3(等 D) → 整合(3.x) → 前沿调研(4.1, 1-loop)
