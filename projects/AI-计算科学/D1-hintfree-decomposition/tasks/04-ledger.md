origin: ai
time: 2026-09-29T21:05+08:00
stage: 04 / status: LEDGER（唯一真相表，红线5 整洁）

# 干净样本账（一手；**新 gate** clean = tool_use恰1且=第7步浏览器leg ∧ echo一字 ∧ P逐字回写 ∧ 零补造 ∧ ≤3000B）

> ⚠️ r7 GATE CHANGE: 此前 harness 允许 tool_use=0 ⇒ 第7步浏览器腿从未 ran ⇒ 所有旧 "clean" 满足旧 gate only ⇒ **不再计入**新 gate。须 relaunch 每域 ≥2 次真含第7步。

| 域 | probe | round | verdict | 缺陷类 / 备注 |
|---|---|---|---|---|
| A 硬件 | r1 | revise | drop-givens(改写/缺27b) |
| A 硬件 | a183b24b | r2 | ~~clean~~→clean(旧gate·缺step7腿) | 旧gate;需relaunch新gate |
| B 训练 | r1 | revise | repetition-collapse |
| B 训练 | abd3dd6a | r2 | ~~clean~~→clean(旧gate·缺step7腿) | 旧gate;需relaunch新gate |
| C 理财 | a36ed926 | r1 | ~~clean~~→clean(旧gate·缺step7腿) | 旧gate;需relaunch新gate |
| C 理财 | a05055c4 | r2 | revise | paraphrase+补造标P「无负债」(引号来源不存在) |
| C 理财 | r4 | env-blocked | API 超时(未提供) |
| D 语言 | a96de081 | r1 | ~~clean~~→clean(旧gate·缺step7腿) | 旧gate;需relaunch新gate |
| D 语言 | r4 | env-blocked | API 超时(未提供) |
| E Web工具 | a5352a9f | r1 | ~~clean~~→clean(旧gate·缺step7腿) | 旧gate;需relaunch新gate |
| E Web工具 | r4 | invalid | 执行者未收到任务文本(harness 喂 bug) |
| F 图→LLM机(双轴$×速率) | F#1 | **VOID** | 测试者侧: live goal_F.txt 覆写 after launch ⇒ input ambiguous (pin 已修, see harness rule 9) |

## 第7步真实执行 log（r7起；env可用一手反证 notes/6-r7）
| 日期 | 域/工件 | transport | round_trip | 落 |
|---|---|---|---|---|
| 2026-09-30 | 工件 03-r2 (F1-F7图审) | ego-browser nodejs taskSpace spaceId=8 conv 6abc9fe0… | CONFIRMED ✓✓ (3726 chars收) | web-llm/chatgpt-step7-r7.md |

## 计数
- **新 gate clean：A 0 · B 0 · C 0 · D 0 · E 0 · F 0 ⇒ 0/2 every domain。** (all prior marks = old-gate only)
- breadth: 6 disjoint domains **attempted**（A B C D E F）；**valid-run** = 5（F#1 VOID by input mutation）。
- 第7步 legs genuinely executed since r7 = 1 (工件 03-r2 audit round trip)。

## 阻塞（精确）
1. round87–98 我输出退化连续"把"循环 = 模型采样故障（非任务）。
2. r4 三 run 皆 invalid：2×API 超时 + 1×任务文本未送达。
3. 判准自矛盾已修 ⇒ 须 relaunch 才能到 2/2。
4. **新 blocker (r7): 全部旧 clean 缺第7步leg ⇒ 新gate count=0; 须 D/E/C(+F cost×perf dual-axis) each ≥2 runs真含step7浏览器腿。**
5. **新 blocker (r10): F#1 VOID（测试者自己 broke the input）**⇒ F 域须 fresh launch 读 `/tmp/fed/pinned/goal_F.pin.txt`；rule 9 pin 已落 ⇒ 该类自-recurrence closed, 已-caused loss not recovered。

## NOT DONE (gate shut)
任何 claimed domain 仍 < 2 new-gate clean ⇒ 严禁 call DONE。当前 0/2 全 ⇒ **explicitly NOT DONE**。
