### 摘要
为 AI agent 建立长期 persona memory, 支持跨会话 persona 一致性.

### 核心方法
1. 维护持久化 persona memory M(t)
2. M(t) = f(M(t-1), Context(t), Persona_Verification)
3. 通过自适应更新机制防止 memory drift

### 对 persona-v3 的启示
persona-v3 的 pre-training prior 需要 memory 支持. ARPM 提供了 memory 的数学框架.

### 与 persona-v3 的协作
- persona-v3 提供当前会话的 persona 框架
- ARPM 提供跨会话的 memory 机制
- 两者结合可以实现长期 persona 一致性