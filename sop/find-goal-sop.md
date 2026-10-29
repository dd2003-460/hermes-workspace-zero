# find-goal SOP — 无活跃 goal 时如何寻找并立项

# origin: human (成璐 2026-10-30 指令) + ai (落地)

## 触发
stop_hook pre_verify 判定「无活跃 stage-gate goal」，或 loop-keepalive.py 唤醒时 `.stage-gate/*.json` 全 completed。

## 步骤
1. **扫本地未推送工作**（防与并行 AI 撞车）：
   - `git log --format="%h %ad %s" --date=iso main..HEAD` → 有未推送 commit 的分支 = 有人正在做，跳过
   - `git remote update` 后对每个远端分支查 `git log <branch>..origin/<branch>`
   - 判据：**最近 24h 内有 push/commit 活动的仓库或分支 = 另一个 AI 在做，不碰**；超过 1 天没动的才是候选
2. **按优先级选任务**（P1>P2，见 AGENTS.md 红线 0.5）：
   - P1 实际问题优先（能产生可验证结果）
   - P2 完成度低优先（<50% 优先启动）
   - 来源：projects/*/tasks/、各项目 loop-state.json、WORK_QUEUE.md
3. **按 goal-template 立项**：读 `sop/goal-template.md`，五字段（目标/阶段/SOP索引/验收标准/失败降级）+ create_goal
4. **开工前留痕**：step_notify 记一条「立项 X，理由 Y」

## 硬规则
- 24h 内有活动的仓库/分支一律跳过（并行 AI 保护）
- 找不到可执行任务 → 做维护性工作（聚合 ACTIVE.md、记忆蒸馏），不得空转
- 一次只立一个 goal，complete 后同回合找下一个

## 索引
- 模板：`sop/goal-template.md`
- 总索引：`sop/SOP-INDEX.md`
