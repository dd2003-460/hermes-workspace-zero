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
    - **2.3** 2.1 + 新建 `sop/arena-researcher.md` 专职规格（拆分纪律+失败协议+交付格式）
    回一个编号即可。
    人类回复：

## 已批

- 2026-10-21 r2 轮：条目 2-5（AGENTS.md 瘦身/结构标准补丁/定时任务/outputs 归位）已批准并执行，存档 `个人/history/APPROVALS-20261021-r2.md`。

## 2026-10-25 根级杂物处置清单（外包高手会话）

> 只读核对 + 本清单；本轮零移动零删除。2026-10-25 04:30 逐项复核（git status / check-ignore / ls / diff）。
> 关键复核结论：**tmp/pfb-b8/ 不是纯重复落盘**——含根级 pfb/ 没有的 batch-8 E13-E16 交付物（4 个 mp4 + build_audio/check_overlap 脚本）；.hermes/、.codex/、decomposition-tree-27b-cost.md、ralph-loop.global.md.bak-decomp-20261016、package.json 均为 **git 跟踪文件**，不是未跟踪残留。

| 路径 | 类型 | 处置建议 | 可逆性 | 依据 |
| --- | --- | --- | --- | --- |
| `.DS_Store` | 系统缓存 | 保留 | 可再生 | 10/23，18K，已被 .gitignore:1 覆盖 |
| `s18-1-kolmogorov-router.aux` | 陈旧残留（LaTeX 构建产物） | 删除（待批 3.1） | 不可逆（未跟踪） | 6/13 16:26，gitignore `*.aux` |
| `s18-1-kolmogorov-router.log` | 陈旧残留（LaTeX 构建产物） | 删除（待批 3.1） | 不可逆（未跟踪） | 6/13 16:26，gitignore `*.log` |
| `s18-1-kolmogorov-router.out` | 陈旧残留（LaTeX 构建产物） | 删除（待批 3.1） | 不可逆（未跟踪） | 6/13 16:26，gitignore `*.out` |
| `texput.log` | 陈旧残留（tex 报错日志） | 删除（待批 3.1） | 不可逆（未跟踪） | 6/13 15:00，761B，gitignore `*.log` |
| `decomposition-tree-27b-cost.md` | 跟踪文档（落点待确认） | 保留/待确认（是否移入项目由成璐定；git mv 可逆，本轮不动） | 可逆 | 10/20 11:52，**git tracked**，9.6K「27B 本地推理成本分解树」 |
| `ralph-loop.global.md.bak-decomp-20261016` | 备份（**git tracked**） | 删除（待批 9） | 可逆（git 历史可恢复） | 10/16 00:46，411B，tracked；主文件 ralph-loop.global.md 存在 |
| `package.json` | 跟踪 npm manifest | 保留 | — | 7/2，tracked；deps fetcher-mcp + playwright |
| `package-lock.json` | 跟踪 npm manifest | 保留 | — | 7/2，tracked |
| `node_modules/` | 保留-工作产物 | 保留 | — | 66M，gitignore `**/node_modules/`；playwright 被 tools/web-llm-review.js、tools/browser-review.js、loop/ralph_runtime/ralph_runtime/web_llm_browser_runner.mjs 引用 |
| `.pytest_cache/` | 工具缓存 | 保留（工作产物）+ 建议补 .gitignore（可逆，无需审批可直接做） | — | 7/15，untracked 且**未被** gitignore 覆盖 |
| `__pycache__/`（tools/、.hooks/、scripts/ 共 3 处） | 工具缓存 | 保留（工作产物） | — | gitignore `__pycache__/` 已覆盖 |
| `.hermes/skills/web-llm-cross-verify/SKILL.md` | 跟踪内容（非杂物） | 保留 | — | 8/9，**git tracked**（.claude/skills 下无同名文件，勿当重复） |
| `.codex/hooks.json` | 跟踪内容（非杂物） | 保留 | — | 10/18，**git tracked**，711B |
| `.board-task-change-freshness/` | 陈旧残留（空目录） | 删除（待批 8） | 实质可逆（空目录可重建） | 7/1，0 字节，git 不跟踪空目录 |
| `tmp/pfb-b8/` | 重复克隆 + **唯一交付物** | 待确认，保留（处置见待批 4） | 删除不可逆（唯一交付物） | 10/24 13:34，131M，独立 git clone；vs 根级 pfb/：独有 outputs/E13-E16 mp4×4、scripts/build_audio_E13-E16.js、src/check_overlap_E13_arena.js |
| `tmp/reorg-backup-20261016.tar.gz` | 备份（回滚点） | 删除（待批 5） | 不可逆 | 10/16，772K |
| `tmp/compress-b35.txt` | 工具残留（会话片段） | 删除（待批 7） | 不可逆（untracked） | 10/23，121B |
| `tmp/compress-b38.txt` | 工具残留（会话片段） | 删除（待批 7） | 不可逆（untracked） | 10/23，23KB |
| `tmp/dsh-checkout/` | 陈旧 checkout | 删除（待批 6） | 不可逆（untracked） | 10/18，551M（node_modules 550M + out/ 构建产物 1M）；.dsh-cli-wrapper.sh 实际引用 app.asar 路径，不依赖此目录 |
| `tmp/fix-image-limit/` | 工作产物（e2e 测试脚本） | 保留 | — | 10/19，含 proxy-before/proxy-REVERTED 修复前记录（红线0：探索过程不删） |
| `tmp/arena-agent-result.md` | 工作产物（arena 探索记录） | 保留 | — | 10/20，14K |
| `tmp/arena-audit-report.md` | 工作产物（arena 探索记录） | 保留 | — | 10/20，28K |
| `tmp/arena-audit-report.patch` | 工作产物（arena 探索记录） | 保留 | — | 10/20，28K |
| `sop/acp-rules.json`、`sop/goal-template-addon-acp-rule.md` | 已收口（addon 2026-10-29 确认合并后删除） | 保留记录 | — | acp-rules.json 仍活；addon 文件已删（r58） |
| `ego/arena-b8-*`（check/submit/submit2.mjs + arena-b8-20261024/ + arena-cleanup-20261024/）、`pfb/` | 在途（归属待确认） | 保留 | — | 10/24，batch-8 E13-E16 arena 提交工作；pfb/ 为 prompt-first-bench clone（79M，10/24 20:07 更新） |

### 待用户批准（不可逆/删除类；回复编号即可，可多选）

3. **6/13 tex 残留 4 文件**：`s18-1-kolmogorov-router.{aux,log,out}` + `texput.log`（合计约 23K，全部已 gitignore，纯构建产物无内容价值）
   - **3.1** 删除全部 4 文件
   人类回复：

4. **`tmp/pfb-b8/`（131M）处置**——含 pfb/ 没有的 batch-8 E13-E16 交付物（mp4×4 + 脚本），其 .git 有 origin/arena/* 远端 ref，交付物是否已推送未验证
   - **4.1** 先验证 E13-E16 交付物已推远端（`git -C tmp/pfb-b8 log origin/arena/*` 核对），确认后整目录删除
   - **4.2** 不删，保留至 batch-8 收尾
   人类回复：

5. **`tmp/reorg-backup-20261016.tar.gz`（772K，10/16 重组回滚点）**
   - **5.1** 删除（重组已稳定 9 天）
   - **5.2** 保留
   人类回复：

6. **`tmp/dsh-checkout/`（551M，10/18 DSH checkout 残留）**——.dsh-cli-wrapper.sh 不引用此目录
   - **6.1** 整目录删除
   - **6.2** 保留
   人类回复：

7. **`tmp/compress-b35.txt` + `tmp/compress-b38.txt`（10/23 会话压缩片段，共 23KB）**
   - **7.1** 删除
   - **7.2** 保留
   人类回复：

8. **`.board-task-change-freshness/`（空目录，7/1）**
   - **8.1** rmdir（空目录，实质可逆）
   - **8.2** 保留
   人类回复：

9. **`ralph-loop.global.md.bak-decomp-20261016`（tracked 备份文件，411B）**
   - **9.1** git rm（内容可从 git 历史 054a5e4d 之前的提交恢复）
   - **9.2** 保留
   人类回复：

**附：.gitignore 覆盖核查（只读）**：`.DS_Store` ✅（L1）/ `__pycache__/` ✅ / `node_modules` ✅（`**/node_modules/`）/ `tmp/` ✅ / `*.log|*.aux|*.out` ✅；**未覆盖**：`.pytest_cache/`（建议补，可逆无需审批）、`.board-task-change-freshness/`（空目录 git 不跟踪，无实际影响）；.hermes/.codex 已被跟踪，覆盖与否无意义。
