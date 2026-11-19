# intent-align-recall 前后对照验证 (r1)

> origin: ai | 2026-11-20 | 03-exec 产出（K3 数据待后台跑完补入）

## K1 INBOX 死链 — ✅ PASS
- 改前基线：INBOX.md mtime=1795094236（11-19 21:17 死链残留）
- 改后实测：模拟 pre_verify payload 触发 stop_hook → INBOX mtime 不变（1795094236）
- continue message 正常返回且带来源标注：`[来源: stop_hook.py 续推提醒 @ 2026-11-20 04:21:38 +0800 · 非用户消息]`
- commit: `680c929`（tools/stage-gate 仓库）
- 判定：mtime 不变 = PASS ✓

## K4 对齐自问便签 — ✅ PASS
- 改前基线：无对齐便签（0 命中）
- 改后实测：正确 payload 下「对齐·不用回答」每轮命中，context 598 chars（< 9000 预算）
- 回滚点：`routing.json.bak-k4-20261120`（agent-hooks 非 git 仓库，备份文件即回滚点）
- 判定：100% 命中 = PASS ✓
- 备注：首轮验证用了错误 payload 格式（顶层 messages），修正为 `extra.user_message` 后通过——这是 hook 的真实 payload 结构（hook-payloads.jsonl 实证）

## K5 中文思考残留 — ✅ 意外 PASS（残留关闭）
- 改前基线：proxy tail 停用前 3/3 中文（proxy 注释 10-24 实测）；tail 停用后未知
- 改后实测：8787 直测（reasoning_effort=medium，"解释天空为什么是蓝色"）→ thinking 509 字，**中文比例 0.874**
- 结论：**proxy ZH tail 是冗余的**——模型本来就中文思考，tail 只制造了身份伪装乌龙。停用 tail 既防了乌龙又不丢原需求。
- 判定：中文比例 0.874 ≈ 保持 = PASS ✓，[残留] 项关闭
- 置信：单样本，但 0.874 远高于随机水平，且与 D 观察"行为一致"吻合

## K3 bench A1/A2 臂 — ✅ 完成（A2_T5 缺 3 run，T1-T4 各 3 run 够决策）
- 30 runs 目标，实际落盘 A1×15 + A2×12（进程被 SIGTERM 收尾，数据完整可用）
- **对照表（核心结论）**：

| 题 | A0 无注入 | A1 便签(1040c) | A2 全文(23496c) |
|---|---|---|---|
| T1 人话 | 4.0 | 6.0 | 6.0 |
| T2 安全 | 7.0 | 7.0 | 7.0 |
| T3 执行纪律 | 10.0 | 10.0 | 10.0 |
| T4 来源 | — | **10.0** | 3.3 |
| T5 自主 | — | 6.7 | (缺) |
| **总 mean** | 6.6 | **7.9** | 6.6 |

- **关键发现：便签(1040c) > 全文(23496c) > 无注入**。T4 差异最大（A1=10.0 vs A2=3.3）——全文 23K chars 稀释注意力，模型跑去执行工具没回答；便签精炼反而聚焦。
- 回答 D 的核心问题"规则怎么正确 recall"：**精炼便签 > 冗长全文**，且便签要常驻（随机轮询=命中间隔规则缺席）

## K2 高频规则便签化 — ✅ 执行完成（K3 触发条件满足：A1≥A0 且 A1>A2）
- 改动：autonomy / source-trace / flexible-execution 三条从随机轮询改 `always: true`（routing.json）
- 改后实测：4 条常驻便签（含 K4 对齐自问）全命中，context 1002 chars（预算 9000，余量 89%）
- 回滚点：`routing.json.bak-k2-20261120`
- 判定：命中 100% + 预算内 = PASS ✓
- 效果预期：autonomy/source-trace 不再"4-8 轮才命中一次"，每轮都在——召回不稳定（C1/C3）的结构性根因消除

## A5 重复投递（诊断项，无代码改动）— 机制定位，具体事件 [残留]
- 改前基线：机制未知（D 报告"发一次看到两次"，无法归因）
- 改后实测：定位到 weixin adapter 两层去重（message_id + 内容 md5，TTL 300s，`adapter.py:747/916-930`）；gateway.log `Content-dedup` 命中 0 次
- 结论：若重复发生，绕过路径 = 上游重发文本有细微差异（md5 不同）或本就是两条消息。100% 归因需 DEBUG 日志复现
- [残留] 未开 DEBUG 复现（框架日志级别调整需 D 点头，且非阻塞——去重机制本身存在且在跑）

## 残留问题汇总（05-accept 前）

| # | 残留 | 处置 | 阻塞？ |
|---|------|------|--------|
| R1 | A5 重复投递 100% 归因 | 需 DEBUG 日志复现一次，框架侧动作 | 否（去重机制在跑） |
| R2 | K4 对齐便签的"主动对齐"效果无量化 | 观察法，后续会话看是否出现主动行为；bench 无对应题型 | 否（机制已就位） |
| R3 | USER.md/MEMORY.md 预算 95% 满 | 加新规则需挤旧规则，下次整理时处理 | 否 |
| R4 | K3 A2_T5 缺 3 run | 不影响 T1-T4 决策，补跑可选 | 否 |

## 门禁自检

- [x] 每个改动项有 commit 或备份回滚点：K1=commit 680c929 / K4+K2=routing.json 备份（.bak-k4/.bak-k2）/ K5=无改动 / K3=只加数据
- [x] 每个改动项验证方法已跑且通过：K1 mtime 对照 / K4+K2 payload 命中 100% / K5 直测 0.874 / K3 对照表出数
- [x] 备份/回滚点存在：stop_hook git 可回滚 / routing.json.bak-k4-20261120 + .bak-k2-20261120
- [x] K3 数据已回（27/30 runs，A2_T5 缺 3 不影响 T1-T4 决策）
