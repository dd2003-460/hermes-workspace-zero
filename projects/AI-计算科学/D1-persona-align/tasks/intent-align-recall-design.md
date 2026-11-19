# intent-align-recall 改动设计 (r1)

> origin: ai | 2026-11-20 | 02-design 产出 | 基于 diagnosis.md 的 K1-K5

## 改动项表

### K1 INBOX 死链处置 — 删写入路径（方案 b）
- **问题**：auto_continue_hook.py 未注册，INBOX.md 写入后无人消费（死链）；且 INBOX 内容与 continue message 重复（同一 msg 两条路注入，continue message 已在当前回合生效）
- **改动**：stop_hook.py 行 997 `_write_inbox(msg)` 调用注释掉（保留函数体便于回滚），加注释说明：设计意图已废弃（消费端未注册），continue message 单路径足够
- **连带**：行 853 的 INBOX dedup 检查（`if INBOX_FILE.exists() and msg in ...`）一并注释——不写了就不需要 dedup
- **回滚**：git revert（commit 留痕）
- **验证**：改后跑一轮 stop_hook（模拟 pre_verify payload），确认 INBOX.md 不再被更新（mtime 不变）+ continue message 仍正常返回

### K3 bench A1/A2 臂补齐（先于 K2，K2 依赖其数据）
- **问题**：便签 vs 全文效力差没有数据（A1/A2 臂 0 runs）
- **改动**：无代码改动，跑 `runner.py run --arms A1,A2 --n 3`（5 题 × 2 臂 × 3 run = 30 runs，8787 本地）
- **回滚**：无（只加数据）
- **验证**：results/ 新增 30 个 json + `score` 输出 A1/A2 mean 与 A0 基线（T1=4.0/T2=7.0/T3=10.0）对照

### K4 换位思考便签（D 提议 D4）
- **问题**：没有"主动做 D 想要的事"的机制；随机轮询全文 = 命中间隔规则缺席
- **改动**：routing.json 加一条常驻便签「自问·对齐」：
  `你知道 D 现在想要什么吗？做到哪了？接下来最该做什么？（对照 USER.md 偏好 + 当前 goal，不确定就查 qanda-ledger）`
  约 70 chars，常驻（不占随机轮询）
- **回滚**：routing.json 备份（.bak-<日期>）
- **验证**：注入审计 JSONL 确认每轮命中 + 观察后续会话是否出现"主动对齐"行为（定性，无量化）

### K5 中文思考残留验证（proxy tail 停用后）
- **问题**：[残留] tail 停用防了乌龙，但原需求"中文思考"是否保持未知
- **改动**：无（纯验证）。8787 直测：发一条带 reasoning_effort=medium 的请求，看 thinking 块语言
- **回滚**：无
- **验证**：thinking 块中文比例（人工判 1-2 条即可，低置信但够决策：若全英文且 D 在意 → 重新设计注入位置；若 D 不 care → 关闭此残留）

### K2 高频规则便签化（依赖 K3 数据，本轮只设计不执行）
- **触发条件**：K3 数据显示 A1（便签）≥ A0 且接近 A2（全文）→ 便签化安全；A1 < A0 → 便签丢细节，维持随机轮询
- **候选改动**：autonomy/source-trace 从随机轮询（4-6/5-8 轮）改常驻便签（routing.json interval 字段）
- **回滚**：routing.json 备份
- **验证**：bench A1 臂数据（K3 产出）
- **本轮状态**：设计完成，执行等 K3 数据

## 验证矩阵（04-verify 用）

| 改动 | 改前基线 | 改后实测 | 判定 |
|------|---------|---------|------|
| K1 | INBOX.md mtime=11-19 21:17（死链残留） | 改后 stop_hook 触发后 mtime 不变 + continue message 正常 | mtime 不变=PASS |
| K3 | A0: T1=4.0 T2=7.0 T3=10.0 (n=8) | A1/A2 各 3 runs × 5 题 | 出对照表，K2 决策依据 |
| K4 | 无对齐便签（0 命中） | 审计 JSONL 每轮含「自问·对齐」 | 100% 命中=PASS |
| K5 | proxy tail 停用前：3/3 中文（注释实测） | 直测 thinking 语言 | 记录比例，D 定夺 |

## 正交性自检

- K1（删死链）/ K3（补数据）/ K4（加便签）/ K5（验证残留）/ K2（等数据决策）
- K1 动 stop_hook 写入路径，K4 动 routing.json，K3/K5 无代码改动，K2 未执行——无文件重叠 ✓
- K3 先于 K2（数据依赖），K1/K4/K5 可并行 ✓

## 执行顺序（03-exec）

1. K1（1 分钟，先清死链）
2. K5（2 分钟，直测）
3. K4（5 分钟，routing.json + 审计验证）
4. K3（后台跑 30 runs，约 10-30 分钟，期间做 04-verify 的 K1/K4/K5 对照）
5. K2 决策（看 K3 数据）
