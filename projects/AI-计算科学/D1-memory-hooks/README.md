# D1-memory-hooks — memory-hooks 智能提醒引擎

> # origin: ai（2026-10-19，任务归目录，红线 0）

本 workspace 的 hook 提醒系统：固定引擎 + 模型可写数据，经 `dsh-hooks-codex` 桥接入 DSH 的 5 个拦截缝。

## 架构（四层）

| 层 | 位置 | 职责 | 改动生效方式 |
|---|---|---|---|
| 桥 | `@deepseek-ai/dsh-hooks-codex`（app 内置） | 5 缝事件 → 拉起 `python3 .hooks/engine.py <Seam>`（stdin payload / stdout JSON 决策） | 重启 DSH |
| 接线 | `.codex/hooks.json` | seam → command 映射（相对命令，cwd=session.cwd=workspace） | 重启 DSH |
| 挂载 | profile `cordis.patch.yml`（`~/.…/harness/profiles/web/`） | `insert:` 条目挂 hooks-codex，`configPath` 绝对路径 | 重启 DSH |
| 引擎 | `.hooks/engine.py`（固定解释器，不改） | 每次事件实时读 rules.json/anchors.json → 评估谓词 → 输出 `additionalContext`/`deny` | 每次事件 |
| 数据 | `.hooks/rules.json` + `anchors.json` | 规则/词表，**模型可写** | **即时，无需重启** |

## 开关三层（2026-10-19 确认）

1. **规则级**（日常用）：`rules.json` 每条 `enabled: true/false` → 即时生效。
2. **插件级总闸**：`cordis.patch.yml` hooks-codex 条目加 `disabled: true` → 重启 DSH 生效（5 缝全断）。
3. **运行时**：`plugin_manager` 工具改条目 `disabled` 字段（DSH 运行时切换，不需重启）。

## 已知状态（2026-10-19）

- 挂载修复已落盘（insert 形式 + 绝对 configPath，见 `memory/2026-10-19-hook-mount-fix.md`）。
- 重启后 `harness.log` 出现 `profile inconsistency: the patch layer inserts @deepseek-ai/dsh-hooks-codex, which is not installed` —— **噪音警告**（desktop main 的异步审计 `inspectProfileConsistency`，结果仅 `runtime.note`，不影响插件加载；包在 app 依赖闭包内，install scope 可解析）。
- 待验证：09:56 重启后 hook 是否真正注册（thinking-budget-frame 是否注入）。
