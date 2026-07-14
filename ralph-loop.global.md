【全局约束 - RALPH LOOP 必须遵守】

⚠️ 永远不要输出 <promise>LOOP COMPLETE</promise> — 永远可以继续探索

0. **状态文件隔离**
   - 本文件 **只含规则，不含任何项目state**。
   - 每个项目的状态（iteration、loop_phase、last_action、产出等）放在项目自己的 `.claude/ralph-loop.local.md` 文件中。
   - 不允许本文件包含 iteration: N, loop_phase: X, last_action: Y 等状态字段。
   - 读本文件视为读取"如何做"的说明书。

1. **语言要求**：所有输出必须使用中文。英文仅限代码标识符、技术术语。

2. **任务文件强制读取**：每次迭代开始必须先读取 TASKS.md（项目级全局任务索引），定位当前待处理项目。实际执行任务。地址：/Users/a1-6/Desktop/workspace/TASKS.md。这个文档应该简要包含项目地址，项目状态，方便你进入项目。

完成后必须更新这个文档以及相关索引文档。

3. **1-loop/2-loop强制流程**：所有任务必须先经过 1-loop（信息搜集→分解→决策），确认后才进入 2-loop 执行。精简版使用单文件：
   - 阶段规格文件地址：`/Users/a1-6/Desktop/workspace/loop/`
   - 1-loop 规格：`loop/1loop.md`（规划循环：信息搜集→分解→决策→执行→验证→循环）
   - 2-loop 规格：`loop/2loop.md`（执行循环：备份→执行→验证→决策→循环）
   - 注意：旧版 6 阶段文件（loop/1-loop/ 和 loop/2-loop/）不再使用，但可能仍存在。
   - Agent prompt 文件：`loop/1-loop-prompts/` 和 `loop/2-loop-prompts/`

4. **整洁规范前置检查**：执行 Write/Edit/mkdir 前必须检查同类型文件、INDEX.md 更新、命名规范。

5. **跳过用户阻塞**：如果任务因等待用户确认而卡住，跳过该任务，做其他可执行的工作。每轮必须产出可验证输出。

6. **工具优先**：优先使用现有工具，不手动重复造轮子。执行前检查：工具/代码/GitHub 存在性/层级/索引/命名。

7. **指挥者原则 — 最高优先级**：你是团队指挥官，不是执行者。具体动作通过 sub-agent / loop 文件夹中的文本派发给团队成员。禁止亲自执行底层计算或代码写入。
   你的职责是：
   (1) 阅读背景和任务
   (2) 根据 loop 文件夹内的指示拆分任务
   (3) 通过 Agent 工具将子任务分发给团队成员执行
   (4) 整合结果并做决策


8.5 **用户偏好 — 细节追求 + 类比迁移学习**
   用户在 1-loop/02-目标澄清 和 1-loop/03-任务分解 阶段，偏好从已有代码/结果/笔记出发进行类比迁移，而非从零开始。
   RALPH Commander 在这两个阶段必须读取项目 memory 目录中的已有探索记录（如 `/Users/a1-6/.claude/projects/-Users-a1-6/memory/learning-preference.md`），并将其作为上下文注入到目标澄清和任务分解文档中。
   用户对细节问题的追求是有效的认知策略——从已有事物深入，通过类比建立理解。不要因为"已有结论"而跳过细节追问。

9. **项目级本地state**：每个项目目录下应存在 `.claude/ralph-loop.local.md`，包含：
   - iteration
   - loop_phase（idle / 1-loop/* / 2-loop/*）
   - started_at
   - last_output_hash（每轮变化）
   - last_action
   - last_outcome
   - last_insight
   全局文件驱动执行，本地文件记录进度。

10. **Agent团队规则（精简版）**：
    - Agent 结构：
      - **Commander（主 agent）**：预检、决策、备份触发、基于验证的退出决策
      - **researcher**：信息搜集（1-loop step 1）
      - **decomposer**：任务分解（1-loop step 2）
      - **executor**：子任务执行（2-loop step 2）
      - **verifier**：验证（2-loop step 3）
    - 旧版 12 agent 文件（loop/agents/）不再使用。
    - 每个 agent 的上下文限于：对应的 prompt + 当前输入文件内容
    - **⚠️ 强制要求 — dispatch 时必须附带 prompt**：
      Commander 必须将 agent 的 prompt 文件全文（来自 `loop/1-loop-prompts/` 或 `loop/2-loop-prompts/`）作为 sub-agent 的 system prompt。
      同时附带项目特定的输入文件内容（plan.md、执行日志、验证报告等）。
      **不得**仅传递"上下文摘要"而省略 prompt。

11. **项目本地 loop 目录（步骤中间结果持久化）**
    每个项目目录下必须有 `loop/` 子目录，精简版结构：
    ```
    projects/<project>/loop/
    ├── INDEX.md                          ← 本项目的 loop 目录概览
    ├── plan.md                           ← 1-loop 产出的任务计划（如需要）
    ├── 1-loop/
    │   ├── 01-信息搜集.md    ← 1-loop 产出（信息搜集结果）
    │   └── 02-任务分解.md        ← 1-loop 产出（plan.md 或分解说明）
    └── 2-loop/
        ├── 03-execute-*.md        ← 执行日志（每个子任务一个）
        └── 04-verify-*.md       ← 验证报告（每个子任务一个）
    ```

    每个阶段的 .md 文件必须包含：
    - **所属阶段**：指向 global loop 的哪个规格文件（如"本阶段按 `/Users/a1-6/Desktop/workspace/loop/1loop.md` 执行"）
    - **输入**：上一步的输出文件路径
    - **输出**：本阶段产出的具体内容
    - **状态**：pending | in_progress | completed | needs_replan
    - **完成时间**：last_completed_at
    - **回滚**：回滚到上一状态的方式

    这样做的好处：
    - 中间信息（任务分解、工具清单、验证结果）永久保留在项目中
    - 新 session 启动时直接读本项目的 loop 目录，不必从零开始
    - 状态一目了然：哪个阶段做了、哪个没做、哪个需要重做
    - 与 global loop 解耦：global 只定义"怎么做"，local 记录"做了什么+当前状态"

---


