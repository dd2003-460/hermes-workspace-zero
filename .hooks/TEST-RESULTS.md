# memory-hooks 验证结果（2026-10-19）

测试脚本: `/tmp/hooks_verify.py`（17 用例，每场景独立 session_id，turn_id 用整数字符串模拟 DSH 生产 `String(lastTurn)`）。
运行: `python3 /tmp/hooks_verify.py`（在 workspace 根目录；每跑一次自动清 state/verify-* 账本）。
结果: **17/17 PASS**。

## 按规则

| 规则 | 结果 | 证据 |
|---|---|---|
| session-orientation (SessionStart, always, inject, cd2) | PASS | 新 session 注入 ac 含 "本 workspace 装有 memory-hooks（.hooks/）：固定引擎在 5 个拦截缝…"，长度 >20 字符 |
| overthink-guard-l0 (UserPromptSubmit, keyword any:[?,？,吗,什么是,…], max_len:120, inject, cd2) | PASS | prompt "这是什么？" → additionalContext 含 "⚡ L0 检测"；max_len 抑制见下 |
| overthink-backstop (Stop, metric tool_calls_this_turn>=8, deny, cd2) | PASS | 同 session 先记 9 次 bash PreToolUse 再 Stop → `{"decision":"deny","reason":"⚠️ 本 turn 已调用 8+ 次工具…"}`；2 次调用 Stop → 无 deny |
| irreversible-op-guard (PreToolUse, keyword 13 项, deny, cd1) | PASS | `rm -rf /tmp/x` → `{"decision":"deny","reason":"🛑 检测到高不可逆命令…"}`；`ls -la` → 无输出 |
| domain-anchor (UserPromptSubmit, lexicon min_hits:2, inject, cd2) | PASS | prompt "帮我算一下这个因子的回测结果，波动率对冲"（因子/回测 2 命中）→ ac 含 "📌 领域锚点命中" |
| thinking-budget-frame (UserPromptSubmit, always, inject, cd8) | PASS | ac 含渲染后的 "🎯 本会话思考预算 512 tokens"（{thinking_budget_tokens} 被 config 替换） |

## 冷却（cooldown）

| 用例 | 结果 | 证据 |
|---|---|---|
| cd=2 跨 turn：t0 触发 → t1 仍冷却 → t2 放行 | PASS | 同 session 连续三个 turn 短疑问句，ac 的 L0 行依次出现 / 不出现 / 出现（账本 turn_order 只含有账本的 turn，冷却吞掉的 turn 无痕，引擎按整数 turn_id 差值补算 gap） |
| cd=1 同 turn 第二次被吞（irreversible-op-guard） | PASS | 同 turn 第二次 `rm -rf` → 无输出（first deny, second null） |
| 同 turn 第二次 Stop 被吞（overthink-backstop, cd2） | PASS | 9 次调用后 Stop#1 deny，Stop#2 同 turn 空输出 |

## max_len

| 用例 | 结果 | 证据 |
|---|---|---|
| 150 字符 + "？" 的长 prompt 不触发 l0 关键词谓词 | PASS | ac 无 "⚡ L0 检测" 行（thinking-budget-frame 的 always 谓词无 max_len，仍会注入，属预期；测试只断言 L0 行） |

## 异常输入

| 用例 | 结果 | 证据 |
|---|---|---|
| 空 stdin | PASS | exit 0，无输出，stderr 空 |
| 坏 JSON stdin（`{not json`） | PASS | exit 0，无输出 |
| 未知 seam（`NoSuchSeam`） | PASS | exit 0 不崩溃 |
| HOOK_DEBUG=1 stderr 诊断 | PASS | stderr 含 `[overthink-guard-l0] FIRED via keyword` / `[thinking-budget-frame] FIRED via always` 及 lexicon 命中计数 |

## 本次修复的 bug（engine.py，改后快照 /tmp/engine.py.bak-20261019_021319；修前快照 /tmp/engine.py.bak-20261019_010319 已丢失）

1. **cooldown 同 turn 绕过 + 跨 turn 语义错**（cooled_down）：
   - 根因：fire 入账在 main() 里发生在 cooled_down 之后，进程看到的是"入账前"账本；且被冷却吞掉的 turn 不产生任何账本行，turn_order 只含"有账可记"的 turn，用 `len(turn_order)` 或 `index` 无法区分 1-gap 与 2-gap（t2 时 order 仍只有 [t0]）。
   - 修法：新增 `_turn_gap(a,b)=max(0,int(b)-int(a))`（非整数退化 1）；cur 取"已入账则 index，未入账则 `_turn_gap(order[i], turn_id)`"；另加 `last_fire_turn == turn_id → True` 兜住同 turn 第二次（入账前 cur-i 恒 0，N=1 会漏）。turn_id 缺失（SessionStart）不冷却，否则 None 永不入账会让新会话被旧账本误判冷却中。
2. **turn_id=None 时 len(turn_order) 对非空账本总 ≥ i → 新会话误判永远冷却**（同一条修法的分支）。
3. rules.json 配套（改前备份 /tmp/rules.json.bak-20261019_021319）：overthink-guard-l0 cooldown 1→2（让"连续两 turn 第二次被吞"可测）；session-orientation 加 cooldown_turns:2。

## 已知限制（DSH 端，非引擎 bug）

- **DSH 挂载（2026-10-19 已闭环）**：lead 已在活跃 web profile 的 `~/Library/Application Support/dsh-desktop/harness/profiles/web/cordis.patch.yml` 写入 `@deepseek-ai/dsh-hooks-codex` 条目（config: configPath `./workspace/.codex/hooks.json`，model `qwen3.8-27b-w8a16`），**待用户重启 DSH 后生效**。此前排查的 `~/.dsh/profiles/desktop/` 是旧 CLI profile，非活跃。
- 桥接语义（dsh-hooks-codex v0.2.0-rc.2）：PreToolUse 忽略 additionalContext（仅阻塞生效）；非 shell 工具 tool_input 缩为 {command}（其他工具 command=""）；Stop 的 last_assistant_message 恒 null、无条件 deny 会死循环（deny→steer 强制再走一步）；SessionStart detached 执行可能错过首请求；turn_id 为内部整数序号。
