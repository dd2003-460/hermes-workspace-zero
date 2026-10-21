# 2026-10-20 hooks-codex 未加载诊断（根因定位 + 修复方案）

> 用户问题 (m00002)：「很多工作会莫名其妙停止，是不是 hook 的问题？帮我修复」
> 结论：**是配置问题，不是引擎问题。hooks-codex 桥插件从未加载成功，engine.py 从未被拉起。**

## 诊断证据链（本次验证）

1. **引擎本身 OK**：手动 `python3 .hooks/engine.py SessionStart` + stdin JSON → 正确输出 `{"additionalContext":"本 workspace 装有 memory-hooks..."}`，exit=0。
2. **引擎从未被桥接拉起**：`.hooks/state/` 只有我手动测试产生的 `test.jsonl` / `test-manual.jsonl`（session 名 `test-manual` / `test`），**无任何真实 session（如 `s18-*`）的 ledger** → 09:56 重启后 hooks-codex 一次都没调用过 engine。
3. **包在 app.asar 内**（解包验证）：`@deepseek-ai/dsh-hooks-codex` v0.2.0-rc.2 存在于 `/Applications/DSH Desktop.app/Contents/Resources/app.asar` 的 `node_modules/@deepseek-ai/dsh-hooks-codex/`（lib/index.js + package.json）。`@yarnpkg/asar` 404，正确包名是 `@electron/asar`。
4. **插件源码逻辑确认**（asar 内 index.js）：
   - `agent/created` → `runPoint("SessionStart")`，成功时 `agent.inject(context)`；失败走 `ctx.logger.warn("hooks-codex: SessionStart hook failed: ...")`。
   - `agent/pre-step` → UserPromptSubmit；`tools/pre-execute` → PreToolUse（可 deny）；`tools/post-execute` → PostToolUse（可 deny + prepend context）；`agent/turn-stopping` → Stop（deny 时 `agent.steer` 强制再走一步，reason 默认 "continue: blocked by Stop hook"）。
   - 事件发射点全存在：dsh-agent/lib/index.js:579（agent/created）、dsh-agent-loop/lib/index.js:911（agent/pre-step）、:999（agent/turn-stopping）、dsh-tools（tools/*）。→ **缝都是活的，只等插件挂上**。
   - 插件加载失败路径：cordis-plugin-loader/lib/index.js `_init()` L494-510，`import(name)` 失败 → `ctx.logger.error(error)` 后 return，**静默不阻断**其他插件。
5. **harness.log（09:56:57 重启段）三条关键日志**：
   - `warn root: patch: entry "hooks-codex" not found` **不再出现**（最后 06:03）→ 昨天的 insert 格式修复已生效。
   - 09:56:57.763 `[desktop] profile inconsistency: the patch layer inserts @deepseek-ai/dsh-hooks-codex, which is not installed`（+ 同批 3 条 dsh-agent-preset 同款）。
   - **无任何 "hooks-codex:" 前缀日志**（成功/失败都没有），`"apply plugin"` 零命中 → 插件 import 失败后 error 分支的日志级别/去向没进 harness.log，且插件从未注册。
6. **plugin_manager list_plugins（219 条）翻遍 offset 0–125：无 hooks-codex 条目**（全是 include:* 核心 dsh-* 组件）→ 插件 fiber 根本没创建，apply() 从未被调用。
7. **根因**：`~/Library/Application Support/dsh-desktop/harness/profiles/web/package.json` 只有 13 个 deps（**无 @deepseek-ai/dsh-hooks-codex**），`dsh.profile.bundles` 18 项也无它。desktop 的 profile 一致性检查（`profile inconsistency ... not installed`）按 **profile 安装面**判定；插件包既不在 profile 依赖也不在 bundles 列表 → 该 entry 被判定"未安装"，**loader 跳过它**（不 import），静默失败。包虽然在 asar 可解析，但 loader 的 enabled 判定走安装面，不走裸 import。

## 修复方案（L2 级，涉及 app 安装面，待成璐拍板）

**方案 A（推荐，app 级）**：`plugin_manager install_bundle "@deepseek-ai/dsh-hooks-codex"` —— 把包装进当前 profile 安装面（node_modules + package.json deps），一致性检查即过，entry 生效。需确认 install 目标 profile 是 web，且重启后验证。

**方案 B（零改动，用户级，立即生效）**：DSH 本身支持用户级 hooks 配置（与 hooks-codex 插件同一协议，直接读 `.codex/hooks.json` 或等效的用户 hooks 配置文件），不依赖该插件加载。需查 DSH 官方用户 hooks 配置入口（文档/配置 key）。

**方案 C（不推荐，破坏性）**：手动往 profile node_modules 塞包 + 改 package.json —— 升级时会被清理，且绕过一致性管理。

**验证判据（无论走哪个方案）**：重启后 `.hooks/state/` 出现 `s18-*.jsonl` 真实 session ledger，且 harness.log 无 `profile inconsistency` 报 hooks-codex。

## 待办

- [ ] 成璐选 A/B/C（写入 个人/APPROVALS.md 或直接回话）
- [ ] 修复后重启验证判据
- [ ] 若 A：确认 install 后 `plugin_manager list_plugins` 出现 hooks-codex 且 fiberPhase=active

# origin: ai
