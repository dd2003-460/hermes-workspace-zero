# Step 04：移除 ralph-runtime / field-apply 字眼（sop + 索引 + prompt-first + skill，同步 repo 并 push）

## 目标
落实用户指令（m00553 verbatim）：「ralph field-apply 这是废弃的，把 ralph-runtime 从 sop 和索引里面移除，prompt-first 有任何这些字眼都移除」。
目标态：prompt-first 流程完全自包含、环境无关——不出现 field-apply、ralph-runtime（源码目录/内部实现）及任何 ralph CLI 依赖字样；sop 与索引不再指向 ralph-runtime；repo 内已部署副本同步一致并 push。

## 设计决策（执行前读一遍）
1. **清理范围 = 用户点名的三类**：prompt-first 文件、sop（arena-loop-pipeline 全部副本 + ego-verify skill）、索引（loop/README.md）。
2. **prompt-first 文件里所有 ralph 字样全部移除**（含 `ralph prompt-first review/web-llm` CLI 调用描述与 `<!-- ralph-review` 机器标记）——本流程不再依赖 ralph CLI，标记改名无解析风险（该项目从未 init prompt-first 游标，无存量解析）。
3. **机器标记改名**：`<!-- ralph-review` → `<!-- stage-review`（结束符 `-->` 不变）。
4. **不动（用户未点名，且各有理由）**：
   - `loop/ralph_runtime/` 源码本体（用户未要求删本体）；`loop/archived-20261016/` 归档；各 D1 项目历史 loop-artifacts 工件；`scripts/ralph-sync.sh`。
   - **AGENTS.md 严禁修改（红线）**——其正文含 "ralph field-apply" 提交顺序句与 `kind: "ralph_web_llm_cross_check"` 门禁值，作为**遗留项**记入 loop-state.json，不私改。
   - **回执 JSON 的 `kind: "ralph_web_llm_cross_check"` 值保留**——它是 AGENTS.md 门禁契约（AGENTS.md 不可改），不属于"sop/索引/prompt-first 字眼"清理范围；ego-verify skill 中该行保留，标题与 field-apply 句照改。
5. **`.claude/skills/ralph-stage-executor/` 整目录删除**——该 skill 全篇 field-centric（field-status/field-init/field-apply），field-apply 已废弃则 skill 失效；workspace 是 git 仓，删除可恢复（回滚点=git）。
6. repo push 为对外动作，走 Step 03 已验证过的同一远端（凭据无问题），push 后写验证文件；本步骤整体在 submit_plan 批准时用户已见全部清理清单。

## 精确改动清单（侦察已核实到行号）

### A. `loop/prompt-first/00-common-review.md`（3 处 ralph）
- L10 原：「Stop Hook 会自动运行 `ralph prompt-first review .`，Commander 不必主动启动 Reviewer」→ 改：「审阅流程（独立审阅者，如 subagent 按本文件通用审阅标准执行）会自动审阅当前工件，主阶段不必主动启动 Reviewer」
- L14 原：「不得手写 `ralph-review` 路由块…这些内容只由 runtime 写入」→ 改：「不得手写 `stage-review` 路由块…这些内容只由审阅流程写入」
- L58 回执格式块内 `<!-- ralph-review` → `<!-- stage-review`
- 验收：`grep -n "ralph\|runtime" 00-common-review.md` 空。

### B. `loop/prompt-first/02-information-research.md`（2 处 ralph）
- L6 原：「必须先运行 `ralph prompt-first web-llm . "…" --context "…"，把真实回执写入阶段工件；网页 LLM 只提供线索…必须直接调用已安装的 `ralph` 可执行文件；不要使用 `npx`、`npm`、管道或 `head` 包装它。若命令以未授权/未配置状态快速失败…」→ 改：「必须先用网页 LLM 交叉询问（通道=ego-browser，SOP=`.claude/skills/ego-verify/SKILL.md`；问题围绕阶段 01 空缺条件，只要求可复核来源线索），把真实回执写入阶段工件；网页 LLM 只提供线索，不是事实来源。若通道以未授权/未配置状态快速失败，记录完整失败原因后继续公开网页资料搜集，不得等待或循环重试。」
- L21 速查表行 `ralph prompt-first web-llm | 快速核验事实、获取线索 | ralph prompt-first web-llm . "问题" --context "阶段 02"` → 改：`网页 LLM 交叉询问 | 快速核验事实、获取线索 | ego-browser + ego-verify skill（围绕阶段 01 空缺提问）`
- 验收：`grep -n "ralph" 02-information-research.md` 空。

### C. 其余 5 个阶段文件 + examples/（侦察确认 0 处 ralph）
- 不改；验收时全目录 grep 复核为空。

### D. `loop/README.md`（索引，4 处 runtime/ralph_runtime）
- L2-6 指针块：删除「想看状态机/Prompt/DAG/Hook 读 `ralph_runtime/README.md`；想看字段门禁设计读 `ralph-dynamic-fields-design.md`；想看错误码对照读 `ralph-feedback-prompts.md`」→ 改为指向现行流程：「现行主流程 = `prompt-first/` 六阶段 Markdown 流程（01 → 04.5）」。
- L18 原：「Runtime 入口命令：`ralph`（已装在全局 venv，改 `loop/ralph_runtime/` 后即时生效）。」→ 整行删除。
- 验收：`grep -n "ralph_runtime\|ralph-runtime" loop/README.md` 空。

### E. `agents/arena-loop-pipeline.md`（sop 正本，1 处）
- L103 原：「（含 ralph_runtime/、archived 等与 arena 无关的内容）」→ 改：「（含 archived 等与 arena 无关的内容）」。

### F. arena-loop-pipeline 的 5 个副本（只改同一句，不整文件覆盖——pfb/tmp 副本与正本有其他内容差异）
- `projects/健康长寿/D1-longevity-orthogonal/repo/sop/arena-loop-pipeline.md`（与正本 SAME，改 L103）
- `pfb/sop/arena-loop-pipeline.md`（L100 同款句）
- `tmp/pfb-b8/sop/arena-loop-pipeline.md`（L100 同款句）
- `projects/decomp/sop/arena-loop-pipeline.md`（与正本 SAME，改 L103）
- `market-alpha/sop/arena-loop-pipeline.md`（与正本 SAME，改 L103）

### G. `.claude/skills/ego-verify/SKILL.md`（sop 性质，3 处 ralph）
- L40 标题「## 回执与门禁（ralph 02.5 / 04.5）」→「## 回执与门禁（02.5 / 04.5）」
- L48 原：「字段 `evidence_refs` 引用成功回执路径；提交顺序：`fields.json` → `ralph field-apply` → `advance.json` → `ralph apply`。」→ 改：「字段 `evidence_refs` 引用成功回执路径；回执过门禁后，按项目收口路径更新阶段状态文件（无 CLI 依赖，field-apply 已废弃）。」
- L43 `kind: "ralph_web_llm_cross_check"` **保留**（AGENTS.md 门禁契约，见设计决策 4）。
- 验收：该文件 grep ralph 仅剩 kind 行 1 处。

### H. 删除 `.claude/skills/ralph-stage-executor/`（整目录）
- 删除前 `git status` 确认该目录在 git 跟踪内（可恢复）；`rm -rf .claude/skills/ralph-stage-executor`。

### I. repo 同步（对外 push，回滚点=git 新 commit）
```bash
rsync -av --delete workspace/loop/prompt-first/ repo/loop/prompt-first/
cp agents/arena-loop-pipeline.md repo/sop/arena-loop-pipeline.md   # 仅当两文件除本句外完全一致；否则只改 repo 副本 L103 那句
git -C repo add -A && git -C repo commit -m "clean: remove ralph-runtime/field-apply references (m00553)" && git -C repo push
git -C repo ls-remote origin HEAD   # 新 hash ≠ bb93d75
```
- 验证文件：`repo/tasks/clean-verify-20261029.md`（commit hash + ls-remote 原文），该文件也 commit+push。

## 涉及文件（汇总）
- 改：`loop/prompt-first/00-common-review.md`、`loop/prompt-first/02-information-research.md`、`loop/README.md`、`agents/arena-loop-pipeline.md`、F 节 5 副本、`.claude/skills/ego-verify/SKILL.md`
- 删：`.claude/skills/ralph-stage-executor/`
- repo 内改+push：`repo/loop/prompt-first/`（2 文件）、`repo/sop/arena-loop-pipeline.md`、新增 `repo/tasks/clean-verify-20261029.md`
- 回写：`projects/健康长寿/D1-longevity-orthogonal/loop-state.json`（legacy 节追加 `ralph_runtime_cleanup` 记录 + AGENTS.md 遗留项说明；不动已有键）

## 做法
2-loop：
1. **备份**：改前 `git status` 留基线（workspace 是 git 仓，全部改动可 diff/回滚）；`cp -r loop/prompt-first /tmp/prompt-first-bak-$(date +%H%M)`。
2. **执行**：按 A→H 顺序逐文件 edit（用 edit 工具做定点替换，不整文件重写）；H 删除前先 git 确认跟踪状态。
3. **review/verify**（全部机器可查）：
   ```bash
   grep -rn "ralph\|runtime" loop/prompt-first/          # 必须空
   grep -n "ralph_runtime\|ralph-runtime" loop/README.md agents/arena-loop-pipeline.md  # 必须空
   grep -rn "ralph" agents/arena-loop-pipeline.md pfb/sop/arena-loop-pipeline.md tmp/pfb-b8/sop/arena-loop-pipeline.md projects/decomp/sop/arena-loop-pipeline.md market-alpha/sop/arena-loop-pipeline.md  # 必须空
   grep -rn "field-apply" .claude/skills/ loop/prompt-first/  # 必须空
   grep -c "ralph" .claude/skills/ego-verify/SKILL.md     # 必须 =1（仅 kind 行）
   ls .claude/skills/ | grep ralph-stage-executor          # 必须空
   ```
4. **提交**：I 节 repo 同步 + push + 验证文件；workspace 改动随 Step 10 统一 commit（workspace 仓）留痕，loop-state.json 回写本步记录。

## 验收标准
- 上述 6 条 grep/ls 验收命令全部满足（机器可查）。
- repo 远端 main 新 HEAD ≠ bb93d75，`clean-verify` 文件含 commit hash + ls-remote 原文。
- loop-state.json `python3 -c "import json;json.load(open(...))"` exit=0 且含 `ralph_runtime_cleanup` 记录（含 AGENTS.md 遗留项说明）。
- 未触碰清单（D 决策 4）零改动：`git status` 确认 loop/ralph_runtime/、loop/archived-20261016/、AGENTS.md、scripts/ralph-sync.sh、各项目历史 loop-artifacts 无变更。