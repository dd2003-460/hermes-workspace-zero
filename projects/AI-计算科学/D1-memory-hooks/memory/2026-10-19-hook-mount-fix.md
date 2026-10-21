# 2026-10-19 hooks-codex 挂载修复（两 bug 根因）

> # origin: ai

## 现象
用户 m00644：「我没看到hook相关插件启动：1.hook管理 2.各种提醒hook 重启之后都没看到」。
harness.log 反复：`warn root: patch: entry "hooks-codex" not found`（每次重启）。

## 根因 1：补丁形式错误（patch: entry not found）
- `cordis-plugin-include/lib/index.js` `applyEntryPatches`：非 insert 的 patch（顶层 `id`）只按 id **修改 base 已有条目**，找不到 → warn "patch: entry %C not found" + 静默跳过。
- dsh-base 无 hooks-codex base 条目 → 原 `- id: hooks-codex` 条目每次都被忽略。
- **新增顶层条目必须用 `insert:` 形式**（无 patch 级 id → `data.push(...insert)` 追加根列表）。同构先例：同文件 `agents-anywhere-bridge-next`。
- 对比：tool-plugin-manager / compaction-basic 条目是合法 modify（dsh-base L16-17 / L341-342 有 base 条目，name 匹配）。

## 根因 2：configPath 相对路径解析错（静默无 hook）
- hooks-codex `lib/index.js:124` `readFileSync(config.configPath, "utf8")` —— 相对路径对 **process.cwd()** 解析。
- DSH 进程 cwd（lsof 实测，PID 2291/7607）= `/Users/a1-6/Library/Application Support/dsh-desktop/launch-root`（空目录），`./workspace/.codex/hooks.json` 在那里不存在。
- `lib/index.js:127-128` 读失败只 `warn "could not load hook config ... no hooks registered"` —— 静默无 hook。
- 注意：hook **命令**本身用 `session.cwd`（workspace）执行（lib L143/159/307 `workdir=opts.agent?.session.header.cwd ?? process.cwd()`），相对命令无问题；只有 configPath 坏了。

## 修复（已落盘）
profile `cordis.patch.yml` L55-60（备份 `/tmp/cordis.patch.yml.bak-20261019_142750`）：
```yaml
- insert:
    - id: hooks-codex
      name: "@deepseek-ai/dsh-hooks-codex"
      config:
        configPath: /Users/a1-6/Desktop/workspace/.codex/hooks.json
        model: qwen3.8-27b-w8a16
```
- 验证：片段 pyyaml parse OK；整文件 pyyaml 在 L249 报 `tag:yaml.org,2002:js` = 既有 JS-YAML 扩展（备份同错，非本次引入）。

## 重启后（10-19 09:56:57）新日志
`[desktop] profile inconsistency: the patch layer inserts @deepseek-ai/dsh-hooks-codex, which is not installed`
- 来源：desktop main（app/out/main/index.js）`inspectProfileConsistency` → `patchLayerInsertedPackages` 扫 patch 层 insert 的 name，不在 **profile node_modules** 即报 finding。
- 性质：**噪音级警告**——异步审计，结果仅 `runtime.note`，不阻断加载。运行时解析的 install scope = app 依赖闭包（dsh-app-boot `collectInstallationScopePackages` BFS，deps+peers；hooks-codex 在 app package.json L122 声明 → 闭包内），node createRequire(app anchor) 解析 OK。
- 用户批准的「1.1 加 dsh.profile.bundles」是错误修法：bundles 要求包声明 `dsh.bundle`（hooks-codex 无，会 throw "declares no dsh.bundle"）。

## 待验证
- 09:56 重启后 hook 是否真正注册：查 harness.log 09:56 之后是否还有 hooks-codex warn；发简单问题看 thinking-budget-frame/overthink-guard-l0 是否注入。
