# Arena Loop 外包链路（SOP）

> origin: ai · 2026-10-22 · 成璐指令"链路核查 + 强调 arena 首选 + loop 全程必需"
> 适用：所有外包 arena 执行的任务（调研/核验/执行类）。本文件定义**链路**；单环节细节见 `agents/arena-outsource.md`（仓库/降级）与 `agents/loop-executor.md`（loop 阶段）。

## 0. 优先级（硬规则 · 成璐指令）

1. **Arena 外包 SOP = 必须首选通道**：调研/核验/执行类任务，默认走 arena（LMArena agent mode）。不自己 AI 琢磨。
2. **Loop 全程必需 · 双场景**：无论 arena agent 在仓库里执行，**还是** arena 通道失败回退本地 Lead 自答，**loop 6 阶段（01→04.5）一个不少**。
   - 回退降级的是**执行通道**（arena → 本地），不是流程。
   - 本地自答时 loop 工件仍落盘 `loop-artifacts/`，conf 标记 0.2。
3. 两者关系：**loop 是流程骨架（永远在），arena 是默认执行通道（首选，可降级）**。

## 1. 链路总览（6 步 + 每步断点 + 验证门禁）

| # | 步骤 | 断点 | 门禁（不过不进下一步） |
|---|------|------|----------------------|
| 1 | AI 启动 | — | goal 按 `agents/goal-template.md` §3 模板创建：含 SOP 索引（本文件）+ 验收标准 |
| 2 | 注入 agents 原则 | — | 会话已加载 AGENTS.md/CLAUDE.md；goal 描述引用 goal-template §1 质量原则 |
| 3 | 阅读 arena 外包 SOP | — | 已读 `agents/arena-outsource.md` + 本文件；能说出当前任务对应仓库 |
| 4 | 复制 loop 到目标仓库 + push | **断点 A**：workspace 未 commit/push 时，arena 拉到的是旧版 loop | `git pull` 后 `ls loop/prompt-first/*.md` 在目标仓库可见（7 个文件） |
| 5 | 发任务书 | **断点 B**：任务书未 commit/push 时 arena 读不到 | `git log -1 -- tasks/<id>.md` 有提交；arena 会话 `cat tasks/<id>.md` 成功 |
| 6 | arena agent 读 loop + 执行 | **断点 C**：arena agent 不知道要读 loop / 不知道 loop 在哪 | 任务书顶部强制段已写入（§2）；arena 首条消息引用了 loop 阶段路径 |

**回退分支**（步骤 6 故障）：arena 403/沙箱拦截 → 按 `arena-outsource.md` §5 降级本地自答，**loop 工件照常落盘**（conf-0.2），故障记 `knowledge/efficiency-bottlenecks.md`。回退不豁免 loop。

## 2. 任务书强制段（防断点 C · 必须写入 tasks/<id>.md 顶部）

```markdown
【执行前必读】
1. 本任务必须走 1-loop：先读 loop/prompt-first/00-common-review.md + 01..04.5（仓库内）。
2. 每阶段产出落盘 loop-artifacts/stages/<N>/，阶段判定 pass 才进下一阶段。
3. 完成后 commit + push（含全部 loop-artifacts/）。
4. 通道故障（403/沙箱）→ 报告 Lead，由 Lead 降级本地执行，不得静默跳过 loop。
```

## 3. 维护

- 新增仓库 → 更新 `agents/arena-outsource.md` §1 映射表
- 新增链路断点（实际断裂案例）→ 更新 §1 表格 + 记 qanda-ledger
- 本文件变更 → commit + push
