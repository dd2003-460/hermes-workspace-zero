# Step 03: 决定 subagent 派发时是否给 goal-template

## 目标
回答用户第三个问题：派发 subagent 时是否要把 goal-template 文档给 sub 看。

## 做法
1. 分析 subagent 需要的信息：具体任务 + 输出格式 + 边界（自包含 brief）
2. 对照 §2.4 子代理派发原则（fresh 优先、最小必要上下文）
3. 给出结论：subagent 不需要 goal-template 全文，但任务书里应引用对应 loop 阶段 SOP
4. 如需调整，修改派发模板/任务书强制段

## 验收标准
- 明确结论（给/不给/给什么）+ 理由
- 如需改动，给出具体改法