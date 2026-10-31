# Step 03：断点 A 部署——loop/SOP/任务书进仓库并 push（含 git 远端验证）

## 目标
按 `agents/arena-loop-pipeline.md` §1 断点 A 硬门禁，把 1-loop 六阶段文件 + SOP 部署进目标仓库并 push，使 arena agent 能读到仓库内的 loop 与任务书；顺带解决 git 远端访问异常。

## 现状（一手核实，含已执行事实）
- repo = `projects/健康长寿/D1-longevity-orthogonal/repo/`，remote = https://github.com/dd2003-460/longevity-orthogonal-contribution.git。
- **断点 A 部署已完成（本步骤上一轮已执行成功）**：repo/loop/prompt-first/（7 阶段文件 + examples）、repo/sop/arena-loop-pipeline.md、repo/tasks/stage2-arena-task.md、repo/tasks/deploy-verify-20261028.md 均已在远端 main（两次 push：8dd7945→bb93d75，远端 HEAD ≠ 5d64174）。
- `git ls-remote` 曾报 `fatal: 'HEAD' does not appear to be git repository`，根因=用法错误（须传 URL：`git ls-remote <url> HEAD`），重验已通过。
- 任务书内容 = 阶段02 调研任务（unknown 字段 6 项 research_queue，见 state.json）+ 后续阶段推进指令；顶部必须含 arena-loop-pipeline §2 强制段。

## 涉及文件
- 读：`workspace/loop/prompt-first/01..04.5*.md`（7 个阶段文件）、`workspace/agents/arena-loop-pipeline.md`
- 写（repo 内）：`loop/prompt-first/`（rsync）、`sop/arena-loop-pipeline.md`、`tasks/stage2-arena-task.md`（任务书，≤50 行，含【执行前必读】强制段）
- 验证落盘：`tasks/` 内验证文件记录 commit hash + `git ls-remote` 输出（断点 A 硬门禁要求）

## 做法
2-loop：
1. **备份**：repo 干净无需备份；先 `git status` 确认。**幂等**：`ls repo/loop/prompt-first/ repo/sop/ repo/tasks/` 若 7 文件 + sop + 任务书 + 验证文件齐全（= 已部署），跳过部署命令，直接进 review/verify；仅缺失项才补 rsync/cp + commit + push。
2. **执行**：
   ```bash
   git -C repo ls-remote https://github.com/dd2003-460/longevity-orthogonal-contribution.git HEAD   # 先验远端
   mkdir -p repo/loop repo/sop repo/tasks
   rsync -av --delete workspace/loop/prompt-first/ repo/loop/prompt-first/
   cp workspace/agents/arena-loop-pipeline.md repo/sop/
   # 写 tasks/stage2-arena-task.md（任务书：背景=阶段2无token跑可覆盖子集；任务=01收口+02调研6项+02.5交叉验证+03行动分解；产出落 loop-artifacts/stages/<N>/；完成后 commit+push 含全部 loop-artifacts；故障报 Lead）
   git -C repo add -A && git -C repo commit -m "deploy: loop/prompt-first + sop + stage2 任务书 (workspace 20261028)"
   git -C repo push && git -C repo ls-remote origin HEAD
   ```
3. **review/verify**（断点 A 硬门禁）：`ls repo/loop/prompt-first/*.md` 应有 7 个文件；`sop/arena-loop-pipeline.md` 存在；push 后 commit hash + ls-remote 输出写入 `tasks/deploy-verify-20261028.md`（该文件也 commit+push）。
4. **提交**：完成即留痕。若 ls-remote 持续失败（凭据）：记 `knowledge/efficiency-bottlenecks.md`，降级走 GitHub REST API 通道（arena-loop-pipeline §3.3），不阻塞。

## 验收标准
- `repo/loop/prompt-first/` 7 个阶段文件 + `sop/arena-loop-pipeline.md` + `tasks/stage2-arena-task.md` 在远端 main 可见（`git ls-remote` 新 hash ≠ 5d64174）。
- 验证文件含 commit hash + ls-remote 原文输出。