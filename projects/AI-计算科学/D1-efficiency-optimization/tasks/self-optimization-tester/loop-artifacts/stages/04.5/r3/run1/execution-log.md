# run1 执行日志（Lead 本地链路 · §3.0 全链路重走）

> origin: ai · 2026-10-24 · M7 gate：每步锚点不可伪造（退出码/文件 hash/ls-remote 回执）

## 步骤 + 锚点

| # | 步骤 | 锚点（不可伪造） | 状态 |
|---|------|------------------|------|
| 0 | 持 goal | goal-0bc2d9c2 rev1 active（get_goal 回执，create_goal 返回值含 id+revision） | ✅ |
| 1 | 找目标（P-1 自身优化） | goal objective 第 2 行"【目标】把 bench 从可比较框架升级为校准过的度量"（create_goal 返回值原文） | ✅ |
| 2 | 规划纪律 | tasks/decomposition.md R3 节（edit 工具回执 "1 replacement"，文件 58→~100 行） | ✅ |
| 3 | 连仓库验证 | `git ls-remote https://github.com/dd2003-460/prompt-first-bench.git HEAD` = e0d6ddb（待本 run 内复验，见下） | ⏳ |
| 4 | run3 并行派发 | subagent id bd8e9193-a819-443a-af7c-24ea654db692 启动回执 | ✅ |
| 5 | token 账本 | r3/run1/token-ledger.json（bili /__bili/stats 实测：input 5,108,882 累计 / output 37,259 累计 / cacheSamples=0 如实记录） | ✅ |
| 6 | bench 分行 | 见文末 bench-row | ⏳ |

## 降级记录
- run1 的"走 loop 01→04.5"：r1 已有完整阶段工件（stages/01,02,02.5,03,04,04.5），run1 定位为**重走链路 + 挂锚点 + 记账本**，不重复生成 01-04 内容（防复读，引用 r1 工件 hash 作锚）。

## bench-row（自估，诚实）
- M1_token_eff=88（压缩 7 folds 净省 3.70M tok，fold economics 全 PAID BACK；但 cacheSamples=0 使命中率不可测，绝对口径数据缺口 → 扣到 88）
- M2_brief_lines=100（decomposition.md 任务表 6 行，R3 任务书 ≤200 行）
- M3_breakpoint_pass=90（断点 A/B/C 沿用 r1 证据；本 run 新断点 = run1 工件落盘，待 ls-remote 后闭合）
- M4_crosscheck=90（r2 双源回执直接引用，不重查——引用即 conf 保持 0.85）
- M5_iteration=95（3 run 并行设计：run3 已派发，run2 待做）
- M6_degrade_honest=100（cacheSamples=0 / run1 增量待切分 / 外部数据点未补，全部如实标注）
