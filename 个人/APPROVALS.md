# APPROVALS — 集中审批队列（m01140 机制）

## 模板规则（成璐 2026-10-18 m02225 指令 · AI 必须遵守）

1. **准入**：只有**不可逆 且 偏好不明**的操作进这里（m01140）。可逆的事直接做，不问。
2. **编号**：条目编号 `1 / 2 / 3 / 4`，子选项 `1.1 / 1.2 / 1.3`。人类只回编号。
3. **人类回复区（红线）**：每条目内的 `人类回复：` 行**禁止 AI 写入**，只由人类填写。AI 只读不改。
4. **轮转**：人类回复后，AI 依次：
   - ① 整个文件存档到 `个人/history/APPROVALS-<YYYYMMDD>-r<轮次>.md`（轮次 = n+1，保留人类回复原文 + AI 补执行结果）
   - ② 复制本模板重建 `个人/APPROVALS.md`（「待批」从空开始）
   - ③ 执行已批项，把执行证据（file:line / 命令输出）写进 history 文件
5. **模板不可修改**：本文件（`个人/APPROVALS-TEMPLATE.md`）只复制、不修改。改规则需先经成璐批准，旧模板存档到 history。
6. **不阻塞**：等审批期间循环继续，跳过等待项，不停转。

## 待批

1. **hooks-codex 未生效**（2026-10-20 根因已定位，详见 `projects/AI-计算科学/D1-memory-hooks/memory/2026-10-20-hooks-codex-not-loaded.md`）
    症状：09:56 重启后 `.hooks/state/` 无真实 session ledger，harness.log 零 "hooks-codex:" 日志，plugin_manager 219 条无该插件 → 插件从未加载。
    根因（推翻 10-19 的 bundles 结论）：包在 app.asar 内可解析，但 **profile 安装面**（`profiles/web/package.json` 13 deps + 18 bundles）不含 `@deepseek-ai/dsh-hooks-codex`，desktop 一致性检查报 `profile inconsistency: inserts ... which is not installed`，loader 按安装面跳过该 entry（静默，error 日志未进 harness.log）。
    - **1.1** `plugin_manager install_bundle "@deepseek-ai/dsh-hooks-codex"` 装进当前 profile（推荐，走官方安装面，最干净）
    - **1.2** 改用 DSH 用户级 hooks 配置入口（不依赖该插件，零 app 改动；需先确认官方配置 key）
    - **1.3** 撤销 cordis.patch.yml 的 hooks-codex insert 段（放弃桥接方案，engine.py 保留手动用法）
    回一个编号即可。验证判据：重启后 `.hooks/state/` 出现 `s18-*.jsonl`。
    人类回复：

2. **subagent 细粒度拆分规范写入位置**（2026-10-21 成璐 m00656 指令：调研类大任务优先拆子领域，1 subagent 领 1 子领域走 arena；短任务多并行优于单长任务）
    背景：本会话 3 个 teammate 长任务（20–90min）挂 2 次 + 1 次 arena 回复未落页；`acp_cache` 实测 provider 不回报 cache tokens（245 req / 11.72M input unmeasured）→ fork 上下文是否命中缓存本侧无法验证，细粒度拆分当前收益=鲁棒性+并行，非已验证的缓存省钱。
    - **2.1** 只写 arena-outsource skill（SOP 层，首版已落盘：拆分优先+失败协议；不动红线文件；subagent 派发时自带）（推荐）
    - **2.2** 追加进 AGENTS.md「工作纪律」（红线文件，需成璐明确指令才改）
    - **2.3** 2.1 + 新建 `agents/arena-researcher.md` 专职规格（拆分纪律+失败协议+交付格式）
    回一个编号即可。
    人类回复：

## 已批

- 2026-10-21 r2 轮：条目 2-5（AGENTS.md 瘦身/结构标准补丁/定时任务/outputs 归位）已批准并执行，存档 `个人/history/APPROVALS-20261021-r2.md`。
