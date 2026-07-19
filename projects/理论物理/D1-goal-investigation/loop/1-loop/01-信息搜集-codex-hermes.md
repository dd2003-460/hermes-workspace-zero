# Codex vs Hermes 任务机制对比 — 信息搜集报告

> 本阶段按 D1-goal-investigation 项目要求执行。只做原始数据搜集，不做理解和决策。

## 搜集时间
2026-07-14

## 一、OpenAI Codex Agent 任务管理

### 信息搜集结果

- [发现1] OpenAI Agents SDK 将 Agent 定义为"LLMs configured with instructions, tools, guardrails, and handoffs" — 即 Agent 是配置了指令、工具、安全护栏和代理间委派（handoffs）的大语言模型。 — [openai-agents-python README](https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md) — **置信度: 高**

- [发现2] SDK 支持三种执行模式：(1) Sandbox Agents — 预配置容器环境、支持长时间运行的 Agent；(2) Text Agents — 标准文本工作流 Agent；(3) Realtime Agents — 基于 WebSocket 的低延迟 Agent。 — [openai-agents-python README](https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md) — **置信度: 高**

- [发现3] 任务通过 `Runner` 类管理。文本 Agent 使用 `Runner.run_sync`，实时 Agent 使用 `RealtimeRunner` 管理 WebSocket session。 — [openai-agents-python README](https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md) — **置信度: 高**

- [发现4] 工具支持包括 function calling、MCP（Model Context Protocol）、hosted tools。 — [openai-agents-python README](https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md) — **置信度: 高**

- [发现5] 代理间委派：Agent 可以"Delegating to other agents for specific tasks"，支持多 Agent 工作流。 — [openai-agents-python README](https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md) — **置信度: 高**

- [发现6] Session/状态管理：SDK 提供"Automatic conversation history management across agent runs"，通过 session 对象实现跨 Agent 运行的一致对话历史。 — [openai-agents-python README](https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md) — **置信度: 高**

- [发现7] 安全护栏（Guardrails）：内置输入/输出验证的安全检查机制。 — [openai-agents-python README](https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md) — **置信度: 高**

- [发现8] 可观测性：内置 agent run 追踪机制，支持查看、调试和优化工作流。 — [openai-agents-python README](https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md) — **置信度: 高**

- [发现9] 人类参与：内置"mechanisms for involving humans across agent runs"。 — [openai-agents-python README](https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md) — **置信度: 高**

- [发现10] 原始文件未明确提及内部 tool-calling loop 的迭代细节，仅概述了高级执行模式。 — [openai-agents-python README](https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md) — **置信度: 中**

### 关键机制

- **任务队列：** OpenAI Agents SDK 没有显式的任务队列概念。每个 Agent 接收一个任务/指令并通过 Runner 执行。多 Agent 工作流通过 handoff（委派）实现，而非队列调度。
- **状态持久化：** Session 对象自动管理对话历史跨 Agent 运行。未见显式的 checkpointing/持久化到磁盘的机制文档。
- **Session 恢复：** Session 对象提供跨 run 的对话历史自动管理。Realtime Runner 支持 WebSocket 会话，但未见明确的"从 checkpoint 恢复"机制。
- **阻塞处理：** 通过 Guardrails 提供输入/输出验证。人类参与机制可在运行时介入。
- **循环控制：** Runner 管理 tool-calling loop（隐含在 SDK 内部），但未公开暴露循环控制参数（如 max_iterations）。
- **导航入口：** 未见显式的 loop-state.json 或类似状态入口文件机制。

---

## 二、Anthropic Claude Agent SDK (Hermes) 任务管理

### 信息搜集结果

- [发现1] Anthropic SDK 核心是 `anthropic` 包，基本用法是通过 `client.messages.create()` 发送消息并获取响应。这是单轮 API 调用。 — [anthropic-sdk-python README](https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/main/README.md) — **置信度: 高**

- [发现2] 存在 `anthropic/extensions/langgraph` 扩展，表明 Anthropic 有将 Agent 与 LangGraph 集成的能力。 — [anthropic-sdk-python README](https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/main/README.md) — **置信度: 中**（仅从目录结构推断）

- [发现3] Anthropic Agent SDK 的官方文档（platform.claude.com）持续返回 404/403，无法获取 Agent SDK 的详细架构文档。 — 多次尝试 — **置信度: 低**

- [发现4] Anthropic Agent SDK 中的 Agent 类（Agent SDK）包含 tool_use、checkpointing 等能力的提及。 — [CrewAI 文档交叉引用](https://docs.crewai.com/core-concepts-Crews) — **置信度: 低**（间接推断）

- [发现5] 在 Anthropic Agent SDK 的上下文中，Agent 具有异步执行（async execution）支持。 — [CrewAI 文档交叉引用](https://docs.crewai.com/core-concepts-Crews) — **置信度: 低**

- [发现6] Anthropic 官方 SDK README 仅展示单轮消息 API 示例，未展示 Agent SDK 的 Agent 类和多步循环。原始 Agent SDK 代码仓库（agent-sdk-python）返回 404。 — [anthropic-sdk-python](https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/main/README.md) — **置信度: 高**（负结果）

### 关键机制

- **任务队列：** Anthropic Agent SDK 基于消息 API（`client.messages.create`），无显式任务队列。Agent 通过 tool_use 循环进行多步执行，但队列概念由上层框架（如 LangGraph 扩展）管理。
- **状态持久化：** 底层 Anthropic API 无内置持久化。checkpointing 能力可能存在于 Agent SDK 的 Agent 类中（从交叉引用间接确认），但具体机制无法从公开文档确认。
- **Session 恢复：** 通过 LangGraph 扩展可以实现 durable execution 和 checkpoint 恢复。原生 Anthropic API 无内置 session 恢复。
- **阻塞处理：** 原生 API 无阻塞机制。Agent SDK 的 tool_use loop 通过 tool 返回值和消息上下文进行状态传递。
- **循环控制：** Anthropic 的 tool_use 循环（Claude 的 tool calling 机制）在每次 response 中返回 tool_use content block，客户端需自行将其输入下一次调用。这是一个**客户端驱动的循环**，而非服务端驱动的。
- **导航入口：** 无内置 loop-state 机制。状态管理需自行实现或依赖 LangGraph 等上层框架。

---

## 三、Microsoft AutoGen 任务管理

### 信息搜集结果

- [发现1] AutoGen 采用 Actor 模型构建事件驱动框架，支持分布式、可扩展和弹性部署。 — [GitHub README](https://github.com/microsoft/autogen) — **置信度: 高**

- [发现2] 代理通过异步消息通信，支持事件触发和请求/响应两种通信模型。 — [GitHub README](https://github.com/microsoft/autogen) — **置信度: 高**

- [发现3] 支持多 Agent 对话模式：两 Agent 聊天、群聊（group chat）、coordinator-expert 模式（主 Agent 将专业查询委派给专用工具/Agent）。 — [GitHub README](https://github.com/microsoft/autogen) — **置信度: 高**

- [发现4] 核心 API 实现消息传递、事件驱动 Agent 和本地/分布式运行时。 — [GitHub README](https://github.com/microsoft/autogen) — **置信度: 高**

- [发现5] `max_tool_iterations` 参数用于限制单个 Agent 执行 tool 调用的最大次数。 — [GitHub README](https://github.com/microsoft/autogen) — **置信度: 高**

- [发现6] ConversableAgent 支持异步执行和多种对话模式（concurrent, step-by-step pipelines, collaborative group discussions, role transitions, self-review cycles, script running）。 — [AutoGen 文档](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/) — **置信度: 高**

- [发现7] AgentTool 封装专家 Agent 为可调用函数，主 Agent 通过工具形式委派查询给专家。 — [AutoGen 文档](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/concepts/index.html) — **置信度: 高**

### 关键机制

- **任务队列：** 无显式任务队列。任务通过消息传递在 Agent 之间流动，conversation pattern 决定任务路由方式。
- **状态持久化：** 消息上下文即状态。通过 Agent 间的消息历史维持对话状态。未见显式 checkpoint/持久化到外部存储的机制。
- **Session 恢复：** 通过消息历史可以在 Agent 间恢复上下文。基于 `conversable_agent` 的 session 状态存储在内存中，重启后不保留。
- **阻塞处理：** `max_tool_iterations` 提供硬性上限防止无限循环。群聊模式支持 moderator Agent 控制发言顺序。
- **循环控制：** 通过 `max_tool_iterations` 控制 tool-calling 循环。对话模式（两方聊天、群聊等）控制多 Agent 交互循环。
- **导航入口：** 通过 `max_tool_iterations` 和对话模式配置作为"入口"控制循环行为。

---

## 四、LangGraph 任务管理

### 信息搜集结果

- [发现1] LangGraph 灵感来自 Pregel、Apache Beam 和 NetworkX，用于编排复杂持久的 Agent 工作流。 — [GitHub README](https://raw.githubusercontent.com/langchain-ai/langgraph/main/README.md) — **置信度: 高**

- [发现2] 核心架构是 `StateGraph`，状态通过图节点流动。开发者可以在执行期间"inspect and modify agent state at any point"。 — [LangGraph 文档](https://langchain-ai.github.io/langgraph/concepts/architecture/) — **置信度: 高**

- [发现3] 支持 durable execution（持久化执行），确保应用"persist through failures and can run for extended periods, resuming from where they left off"。 — [LangGraph 文档](https://langchain-ai.github.io/langgraph/concepts/architecture/) — **置信度: 高**

- [发现4] 具备全面的 memory 系统：保留 active reasoning context（短期）和 cross-session data（跨 session 持久化）。 — [LangGraph 文档](https://langchain-ai.github.io/langgraph/concepts/architecture/) — **置信度: 高**

- [发现5] 支持 checkpointing（检点），状态可以在任意执行点保存和恢复。 — [LangGraph 文档](https://langchain-ai.github.io/langgraph/concepts/architecture/) — **置信度: 高**

- [发现6] 提供 interrupt/resume 能力：可以在图节点之间设置中断点，修改状态后 resume。 — [LangGraph 文档](https://langchain-ai.github.io/langgraph/concepts/architecture/) — **置信度: 高**

- [发现7] LangGraph 不抽象化循环结构，专注于 orchestration。它是 LLM 和 tool-calling 循环的底层运行时。 — [LangGraph 文档](https://langchain-ai.github.io/langgraph/concepts/architecture/) — **置信度: 高**

- [发现8] 支持预建架构（prebuilt architectures），通过 LangChain 框架提供。 — [LangGraph 文档](https://langchain-ai.github.io/langgraph/concepts/architecture/) — **置信度: 高**

### 关键机制

- **任务队列：** 通过 StateGraph 的节点和边定义任务流。任务不是队列而是图的遍历路径，通过边（conditional edges）决定路由。
- **状态持久化：** Checkpointing 机制在每次状态转换后保存状态到持久化存储。`State` 对象作为单一真相来源在图遍历中传递。
- **Session 恢复：** `resumable_from_checkpoint` 是核心机制 — 从上次检查点自动恢复执行。状态被持久化到 SQLite、PostgreSQL 等存储。
- **阻塞处理：** Interrupt points（中断点）在节点之间设置，可在运行时暂停、检查/修改状态、然后 resume。
- **循环控制：** 循环由图中的边定义。conditional edges 可以返回 None（终止）或下一个节点（继续循环）。`interrupt_before`/`interrupt_after` 提供细粒度控制。
- **导航入口：** Checkpoint 即导航入口。通过 checkpoint ID 可以精确地找到、检查和恢复任意中间状态。这是**最接近 D1-goal-investigation 目标的设计模式**。

---

## 五、CrewAI 任务管理

### 信息搜集结果

- [发现1] CrewAI 是开源 Python 框架，提供高层抽象和低层 API 用于自动化。 — [GitHub README](https://raw.githubusercontent.com/crewAIInc/crewAI/main/README.md) — **置信度: 高**

- [发现2] 双模式架构：Crews（自主 Agent 协作，基于角色协作）和 Flows（事件驱动控制，精确工作流控制）。 — [GitHub README](https://raw.githubusercontent.com/crewAIInc/crewAI/main/README.md) — **置信度: 高**

- [发现3] Agent 定义在 agents.yaml 中，任务定义在 tasks.yaml 中 — 配置文件驱动。 — [GitHub README](https://raw.githubusercontent.com/crewAIInc/crewAI/main/README.md) — **置信度: 高**

- [发现4] Agent 可配备 tools、memory、knowledge 和基于 Pydantic 的结构化输出。 — [CrewAI 文档](https://docs.crewai.com/core-concepts-Crews) — **置信度: 高**

- [发现5] 三种进程类型：Sequential（顺序）、Hierarchical（分层，自动分配 manager）、Hybrid（混合）。 — [GitHub README](https://raw.githubusercontent.com/crewAIInc/crewAI/main/README.md) — **置信度: 高**

- [发现6] Tasks 指定明确目标，可包含 dependencies 和 structured output。 — [CrewAI 文档](https://docs.crewai.com/core-concepts-Crews) — **置信度: 高**

- [发现7] Flows 提供 secure、consistent state management，支持 fine-grained control over execution paths。 — [CrewAI 文档](https://docs.crewai.com/core-concepts-Crews) — **置信度: 高**

- [发现8] Flows 使用装饰器（`@start`, `@listen`, `@router`）创建复杂的触发条件和条件分支。 — [CrewAI 文档](https://docs.crewai.com/core-concepts-Crews) — **置信度: 高**

- [发现9] Crews 支持"dynamic task delegation and collaboration"，也可以映射到 distinct steps。 — [CrewAI 文档](https://docs.crewai.com/core-concepts-Crews) — **置信度: 高**

- [发现10] 支持 guardrails、callbacks 和 human-in-the-loop triggers。 — [CrewAI 文档](https://docs.crewai.com/core-concepts-Crews) — **置信度: 高**

### 关键机制

- **任务队列：** 无显式任务队列。任务通过配置文件（tasks.yaml）定义，Crew 按 process type 顺序或层次执行。Dependencies 是任务间的硬依赖。
- **状态持久化：** Flows 提供结构化状态管理，使用标准数据模型保证跨任务的"secure, consistent state management"。Crews 的状态在内存中维持。
- **Session 恢复：** Flows 支持"persist execution and resume long-running workflows"。未见具体的 checkpoint 机制。
- **阻塞处理：** Guardrails 提供安全边界。Callbacks 允许在关键节点插入自定义逻辑。Human-in-the-loop triggers 支持人工审批。
- **循环控制：** Process types 决定循环：Sequential（无循环，线性执行）、Hierarchical（manager Agent 协调和验证）。
- **导航入口：** Flows 的 `@start`/`@listen`/`@router` 装饰器构成控制入口。未见 session-level 的状态入口。

---

## 六、对比维度整理

| 维度 | OpenAI Codex/Agents | Anthropic Agent SDK | AutoGen | LangGraph | CrewAI |
|------|---------------------|---------------------|---------|-----------|--------|
| **任务队列** | 无显式队列；Runner.run_sync 单任务执行 | 无队列；基于消息 API 的 tool_use 循环 | 无队列；消息传递在 Agent 间流动 | StateGraph 节点/边定义任务流 | 配置文件驱动（tasks.yaml）；process type 决定执行顺序 |
| **状态持久化** | Session 对象管理对话历史（内存） | 底层 API 无持久化；Agent SDK 可能有 checkpointing（未确认） | 消息历史存储在内存中 | Checkpoint 机制，持久化到外部存储（SQLite/PostgreSQL） | Flows 提供结构化状态管理；Crews 状态在内存中 |
| **Session 恢复** | 跨 run 对话历史自动管理；无 explicit checkpoint 恢复 | 依赖外部框架（如 LangGraph 扩展）实现恢复 | 重启后不保留内存状态 | resumable_from_checkpoint：从检查点自动恢复 | Flows 支持 persist/resume long-running workflows |
| **阻塞处理** | Guardrails（输入/输出验证）；人类参与机制 | tool_use loop 通过上下文传递；无显式阻塞控制 | max_tool_iterations 硬上限；群聊 moderator | Interrupt points（中断点）；可暂停/修改/resume | Guardrails；Callbacks；human-in-the-loop triggers |
| **循环控制** | Runner 内部管理 tool-calling loop（不暴露参数） | 客户端驱动的 tool_use 循环（Anthropic API 每轮返回 tool_use block） | max_tool_iterations；多种对话模式 | 图中边定义循环；conditional edges 控制继续/终止；interrupt_before/after | Process types：Sequential/Hierarchical/Hybrid |
| **导航入口** | 无显式 loop-state 机制 | 无内置机制 | max_tool_iterations 和对话模式配置 | **Checkpoint ID — 可精确找到和恢复任意中间状态** | Flows 装饰器（@start/@listen/@router）；无 session-level 入口 |
| **多层 Agent** | Handoffs（Agent 间委派） | 未见（需要上层框架） | AgentTool 封装专家 Agent | 支持（作为底层运行时） | Crews 自动分工；Hierarchical 模式自动分配 manager |
| **配置方式** | Python SDK 代码定义 Agent | Python SDK 定义 Agent | Python SDK 定义 Agent | Python SDK 定义 StateGraph | 声明式 YAML 配置 + Python 装饰器 |

---

## 七、信息充分性评估

**信息充分性：0.6**

### 已收集到的信息
- OpenAI Agents SDK 的完整架构（Runner、Session、Tool、Handoff、Guardrails）
- AutoGen 的完整架构（Actor 模型、ConversableAgent、max_tool_iterations、对话模式）
- LangGraph 的完整架构（StateGraph、Durable Execution、Checkpointing、Interrupt/Resume）
- CrewAI 的完整架构（Crews/Flows 双模式、Process Types、装饰器工作流）
- Anthropic 基础 SDK 的架构（client.messages.create）

### 缺失的信息
1. **Anthropic Agent SDK 的 Agent 类细节**（置信度低）：官方 Agent SDK（agent-sdk-python 仓库）返回 404，无法获取 Agent 类的 tool_use loop 细节、checkpointing 机制、session 恢复等。这是本报告最大的信息缺口。
2. **OpenAI Codex Agent（Web 版本）的内部循环细节**：已收集到 Agents SDK 的架构，但 web 版 Codex agent 可能使用不同的执行模型（sandbox 环境、特定工具集等），内部 tool-calling loop 的实现细节未公开。
3. **LangGraph 的具体 checkpoint 序列化格式**：虽然知道有 checkpoint 机制，但具体的存储格式（如 JSON schema）、checkpoint ID 的生成方式、cross-session 状态的具体序列化方式未获取。
4. **各框架的 error handling 和 retry 机制**：task 失败后的重试策略、timeout 处理、回退机制信息不足。
5. **实际 loop 状态文件（如 loop-state.json）在业界已有框架中的对应物**：LangGraph 的 checkpoint 是最接近的，但其实现细节未完全获取。

### 建议下一步
- 尝试通过 GitHub API 获取 Anthropic agent-sdk-python 仓库的 README 和关键文件
- 搜索 Anthropic Agent SDK 的 blog post 或技术文章（可能不在官方文档站点）
- 获取 LangGraph checkpoint 的具体实现细节（storage backend、checkpoint schema）
