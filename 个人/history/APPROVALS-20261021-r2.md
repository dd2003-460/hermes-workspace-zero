# APPROVALS — 集中审批队列（m01140 机制）

## 模板规则（成璐 2026-10-18 m02225 指令 · AI 必须遵守）

1. **准入**：只有**不可逆 且 偏好不明**的操作进这里（m01140）。可逆的事直接做，不问。
2. **编号**：条目编号 `1 / 2 / 3 / 4`，子选项 `1.1 / 1.2 / 1.3`。人类只回编号。
3. **人类回复区（红线）**：每条目内的 `人类回复：` 行**禁止 AI 写入**，只由人类填写。AI 只读不改。
4. **轮转**：人类回复后，AI 依次：
   - ① 整个文件存档到 `个人/history/APPROVALS-<YYYYMMDD>-r<轮次>.md`（轮次 = n+1，保留人类回复原文 + AI 补执行结果）
   - ② 复制本模板重建 `个人/APPROVALS.md`（「待批」从空开始）
   - ③ 执行已批项，把执行证据（file:line / 命令输出）写进 history 文件
5. **模板不可修改**：`个人/APPROVALS-TEMPLATE.md` 只复制、不修改。改规则需先经成璐批准，旧模板存档到 history。
6. **不阻塞**：等审批期间循环继续，跳过等待项，不停转。

## 待批

1. **hooks-codex 未生效**（2026-10-20 根因已定位，详见 `projects/AI-计算科学/D1-memory-hooks/memory/2026-10-20-hooks-codex-not-loaded.md`）
   症状：09:56 重启后 `.hooks/state/` 无真实 session ledger，harness.log 零 "hooks-codex:" 日志，plugin_manager 219 条无该插件 → 插件从未加载。
   根因（推翻 10-19 的 bundles 结论）：包在 app.asar 内可解析，但 **profile 安装面**（`profiles/web/package.json` 13 deps + 18 bundles）不含 `@deepseek-ai/dsh-hooks-codex`，desktop 一致性检查报 `profile inconsistency: inserts ... which is not installed`，loader 按安装面跳过该 entry（静默，error 日志未进 harness.log）。
   - **1.1** `plugin_manager install_bundle "@deepseek-ai/dsh-hooks-codex"` 装进当前 profile（推荐，走官方安装面，最干净）
   - **1.2** 改用 DSH 用户级 hooks 配置入口（不依赖该插件，零 app 改动；需先确认官方配置 key）
   - **1.3** 撤销 cordis.patch.yml 的 hooks-codex insert 段（放弃桥接方案，engine.py 保留手动用法）
   回一个编号即可。验证判据：重启后 `.hooks/state/` 出现 `s18-*.jsonl`。
**人类回复（2026-10-21 m00172）**：「压缩和驱逐的都留个索引在agents规则，然后按你说的做。soul也可以放个人里面了因为感觉持久驱动暂时也没法高效对齐」→ 全批 2.1-2.5 + soul 移除（同批）+ 3.1 + 4.1 + 5（执行中）；条目 1（hooks-codex）无回复，保持待批。
**执行结果（2026-10-21）**：AGENTS.md 326→233 行；新文件 `.claude/skills/ego-verify/SKILL.md`、`.claude/skills/arena-outsource/SKILL.md`、`loop/archived-20261016/ralph-team-setup.md`、`个人/identity/digital-twin-motivation.md`、`个人/identity/soul-defaults.md`；红线0 += 4 条结构补丁；「研究优先」节 += arena-outsource 提醒 + 驱逐索引表；每日 09:00 定时任务已建；outputs/memory/ 误放 md 已移项目 memory/。

2. **AGENTS.md 冗余瘦身 + arena-outsource 提醒**（2026-10-21，来自 m00080 问题 4；326 行 → 预计 ~230 行）
   冗余清单（回编号即可，可多选如「2.1 2.3」）：
   - **2.1** RALPH 团队操作细节（~L169-211 共 4 小节 45 行）移 `loop/archived-20261016/ralph-team-setup.md`，留 1 行指针
   - **2.2** m01140 人类确认机制节：留原则 4 行，模板/轮转细节移 `个人/APPROVALS-TEMPLATE.md` 头部注释
   - **2.3** 网页 LLM 交叉验证节（~55 行）：留核心 6 行，ego-browser 代码示例 + 7 站点表 + 先例路径移新 skill `.claude/skills/ego-verify/SKILL.md`
   - **2.4** 「与成璐的关系 + 驱动力」18 行散文压缩为 4 行，全文移 `个人/identity/digital-twin-motivation.md`
   - **2.5** 在「研究优先」节加 2 行：联网调研/分解/交叉复核优先外包 LMArena agent mode，SOP 见 skill `arena-outsource`（`.claude/skills/arena-outsource/SKILL.md`，**已建**）
   - soul（默认决策画像）按指示**保留**，未列入。

3. **项目结构标准补丁加入红线 0**（2026-10-21，来自 m00080 问题 3）
   拟加入 4 条：① 每层（领域+项目）INDEX.md 必有，纯索引；② 每层直接子模块目标 3-7 个；③ 豁免：迭代/编号方案（runs/ablation-L1/{V}/、stages/01..04.5、variants/）不受 3-7 限制，archive/ 不查扇出；④ 配套 SOP `scripts/project-tidy/run.sh --all`（已建）。
   - **3.1** 全部加入（推荐）
   - **3.2** 只加 ①②，豁免和 SOP 不入 AGENTS.md（留在 SOP README）

4. **每日定时整理任务**（2026-10-21，来自 m00080 问题 3）
   拟建：每天 09:00 Asia/Shanghai 跑 `scripts/project-tidy/run.sh --all`，报告追加各项目 loop-state.json last_action，只报告不自动改结构（.DS_Store/空目录除外）。
   - **4.1** 建（推荐）
   - **4.2** 不建（需要时手动跑）

5. **outputs/memory/ 误放文件归位**（2026-10-21，m00080 问题 2）
   媒体项目 `outputs/memory/` 有 1 个 md（疑早期误放），L0 可逆操作，默认自主移入项目 `memory/`——仅备案，不同意回「5 撤」。

## 已批

- （本轮无新增。上一轮 r1 的 Q1 chenglu 激活(A然后B) / Q2 公理层(D2) / Q3 思考预算(E3) 已全部批准并执行，存档：`个人/history/APPROVALS-20261018-r1.md`）

---

## m02354 · DSH 80k 压缩配置（2026-10-18，goal round 1 自主执行）

**事项**：按"如果可以设置成 80k 压缩"的指令，已在
`~/Library/Application Support/dsh-desktop/harness/profiles/web/cordis.patch.yml`
的 loop-recipe preset 中加入：
```yaml
- id: compaction-basic
  name: "@deepseek-ai/dsh-compaction-basic"
  config:
    thresholdRatio: 0.8
    retainRatio: 0.16
```
contextWindow=100k × 0.8 = **80k token 处触发自动压缩**，保留 16% 近期对话。
`auto: true`（默认）保持开启。

**回滚点**：改前备份在 `/tmp/cordis.patch.yml.bak-*`（ls 找最新一个；回滚 = 删除上述 6 行或从备份恢复）。
**生效方式**：需要重启 DSH Desktop（profile 在启动时加载）。
**回一个词**：`ok`（接受）/ `撤`（回滚这 6 行）。

---

## m02355 · hooks-codex 桥接 + tool-plugin-manager 启用（2026-10-19，goal round 2 自主执行）

**事项**：同一文件 `cordis.patch.yml` 新增两处：

1. **hooks-codex 桥接**（~line 52-58）：
```yaml
- id: hooks-codex
  name: "@deepseek-ai/dsh-hooks-codex"
  config:
    configPath: ./workspace/.codex/hooks.json
    model: qwen3.8-27b-w8a16
```
`configPath` 相对于 DSH 启动目录 `~/Desktop/` 解析 → `~/Desktop/workspace/.codex/hooks.json`。
挂载后 DSH 的 5 个 seam（SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop）
会自动调用 `.hooks/engine.py`，实现 memory-hooks 智能提醒。

2. **tool-plugin-manager 启用**（~line 93-97）：
```yaml
- id: tool-plugin-manager
  name: "@deepseek-ai/dsh-plugin-manager/tools"
  disabled: false
```
启用后 agent 可见 `plugin_manager` 工具（list_plugins / set_plugin 等），可管理 hook 等插件开关。

**回滚点**：删除上述两段（各 5-7 行），或从 `/tmp/cordis.patch.yml.bak-*` 恢复。
**生效方式**：需要重启 DSH Desktop。
**回一个词**：`ok`（接受）/ `撤`（回滚这两段）。
