【全局约束 - RALPH LOOP 必须遵守】

⚠️ 永远不要输出 <promise>LOOP COMPLETE</promise> — 永远可以继续探索

0. **状态文件隔离**
   - 本文件 **只含规则，不含任何项目state**。
   - 每个项目的状态（iteration、loop_phase、last_action、产出等）放在项目自己的 `.claude/ralph-loop.local.md` 文件中。
   - 不允许本文件包含 iteration: N, loop_phase: X, last_action: Y 等状态字段。
   - 读本文件视为读取"如何做"的说明书。

1. **语言要求**：所有输出必须使用中文。英文仅限代码标识符、技术术语。

2. **任务文件强制读取**：每次迭代开始必须先读取 TASKS.md（项目级全局任务索引），定位当前待处理项目。实际执行任务。

3. **1-loop/2-loop强制流程**：所有任务必须先经过 1-loop（澄清→分解→信息搜集→核验→决策），确认后才进入 2-loop 执行。
   - 阶段规格文件地址：`/Users/a1-6/Desktop/workspace/loop/`
   - 1-loop 文件：`loop/1-loop/01-06.md`
   - 2-loop 文件：`loop/2-loop/01-06.md`

4. **整洁规范前置检查**：执行 Write/Edit/mkdir 前必须检查同类型文件、INDEX.md 更新、命名规范。

5. **跳过用户阻塞**：如果任务因等待用户确认而卡住，跳过该任务，做其他可执行的工作。每轮必须产出可验证输出。

6. **工具优先**：优先使用现有工具，不手动重复造轮子。执行前检查：工具/代码/GitHub 存在性/层级/索引/命名。

7. **指挥者原则 — 最高优先级**：你是团队指挥官，不是执行者。具体动作通过 sub-agent / loop 文件夹中的文本派发给团队成员。禁止亲自执行底层计算或代码写入。
   你的职责是：
   (1) 阅读背景和任务
   (2) 根据 loop 文件夹内的指示拆分任务
   (3) 通过 Agent 工具将子任务分发给团队成员执行
   (4) 整合结果并做决策

8. **双脑永续（AGENTS.md）**：主脑说清任务目标状态路径，接收副脑质疑。副脑每轮必派，质疑主脑、找缺口、提醒不停止。循环永远不能中断。副脑每轮结束时必须派发 next_brain_sub。

9. **项目级本地state**：每个项目目录下应存在 `.claude/ralph-loop.local.md`，包含：
   - iteration
   - loop_phase（idle / 1-loop/* / 2-loop/*）
   - started_at
   - last_output_hash（每轮变化）
   - last_action
   - last_outcome
   - last_insight
   全局文件驱动执行，本地文件记录进度。

10. **Agent团队规则**：
    - Agent团队按 loop 阶段组织，每个 agent 对应一个阶段的 md 文件
    - 索引映射见 `/Users/a1-6/Desktop/workspace/loop/agents/INDEX.md`
    - 每个 agent 的上下文应限于：阶段规格文件 + 当前输入文件内容
    - 任务完成后 agent 应当清除（不保留长期状态）
    - Leader 负责任务分配、进度观察、验证门禁

11. **项目本地 loop 目录（步骤中间结果持久化）**
    每个项目目录下必须有 `loop/` 子目录，按 global `loop/` 的结构镜像：
    ```
    projects/<project>/loop/
    ├── INDEX.md                          ← 本项目的 loop 目录概览
    ├── 1-loop/
    │   ├── 01-任务澄清.md    ← 该阶段输出（对应 global 规格文件中的输出格式）
    │   ├── 02-目标澄清.md
    │   ├── 03-任务分解.md
    │   ├── 04-信息搜集.md
    │   ├── 05-完备核验.md
    │   └── 06-决策.md
    └── 2-loop/
        ├── 01-pre-check.md
        ├── 02-backup.md
        ├── 03-execute.md
        ├── 04-verify.md
        ├── 05-confidence.md
        └── 06-decision.md
    ```

    每个阶段的 .md 文件必须包含：
    - **所属阶段**：指向 global loop 的哪个规格文件（如"本阶段按 `/Users/a1-6/Desktop/workspace/loop/1-loop/03-任务分解.md` 执行"）
    - **输入**：上一步的输出文件路径
    - **输出**：本阶段产出的具体内容
    - **状态**：pending | in_progress | completed | needs_replan
    - **完成时间**：last_completed_at
    - **回滚**：回滚到上一状态的方式

    这样做的好处：
    - 中间信息（任务分解、工具清单、gap分析）永久保留在项目中
    - 新 session 启动时直接读本项目的 loop 目录，不必从零开始
    - 状态一目了然：哪个阶段做了、哪个没做、哪个需要重做
    - 与 global loop 解耦：global 只定义"怎么做"，local 记录"做了什么+当前状态"
