---
active: true
started_at: "2026-05-16T00:00:00Z"
---

**状态唯一来源**: TASKS.md (唯一状态文件)
- 文件路径: /Users/a1-6/Desktop/workspace/TASKS.md
- 旧状态文件已清理:
  - loop/ 目录已全部删除（2026-06-10）
  - task.state.json 已删除（2026-06-11, iteration 502）
  - 所有 loop state 文件已清理，TASKS.md 是唯一状态源

动作：
1.先阅读workspace/AGENTS.md 。
2.读取workspace/TASKS.md 。
3.根据1思考你应该干什么，我需要你干什么，怎么样做效率最高（显然是工具复用和网络上工具，文献搜索，方法复用），最稳健，
4.根据2看看有什么需要做的项目，没有就自己思考有什么可以提高你的效率的工具，尝试探索，按照agents规范部署，或者自己探索学术任务。

【全局约束 - RALPH LOOP 必须遵守】
⚠️ 永远不要输出 <promise>LOOP COMPLETE</promise> — 永远可以继续探索
0.严禁任何对本文件任何非临时状态内容的修改（从阅读workspacee开始之后内容都不能修改，除非用户明确要求）
1. **语言要求**：所有输出必须使用中文。英文仅限代码标识符、技术术语。
2. **任务文件强制读取**：每次迭代开始必须先读取TASKS.md(唯一地址:/Users/a1-6/Desktop/workspace/TASKS.md)，实际执行任务。
3. **状态源**: 不再使用 loop/1-loop/2-loop，TASKS.md 是唯一状态源。所有任务状态、进度、阻塞项均以 TASKS.md 为准。
4. **整洁规范前置检查**：执行Write/Edit/mkdir前必须检查同类型文件、INDEX.md更新、命名规范。
5. **跳过用户阻塞**：如果任务因等待用户确认而卡住（如 arXiv 提交需作者确认），跳过该任务，做其他可执行的工作。每轮必须产出可验证输出。
6. **工具优先**：优先使用现有工具，不手动重复造轮子。
