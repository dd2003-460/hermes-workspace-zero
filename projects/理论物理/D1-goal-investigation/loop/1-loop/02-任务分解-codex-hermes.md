# Codex vs Hermes 任务机制对比 — 分解分析

> 本阶段执行 D1-goal-investigation 项目要求。基于信息搜集报告进行理解、决策和评估。

## 分析时间
2026-07-14

## 一、信息充分性重新评估

**分析前置信度**: 0.6（信息搜集结论）

### GitHub API 补充验证（2026-07-14）

通过 GitHub API 确认：
- `anthropics/agent-sdk-python` — **404**（仓库不存在）
- `anthropics/anthropic-sdk-python` — 存在，description 为空，未归档
- GitHub 搜索 `"anthropic" "agent-sdk"` — **无官方结果**，只有第三方项目

**结论**: Anthropic **没有公开** agent-sdk-python 仓库。Anthropic Agent SDK 要么：
1. 不存在（仅作为 platform.claude.com 的内部服务）
2. 已整合进其他项目（如 claude-code）
3. 未在 GitHub 开源

### 已获取的补充信息
- 五条主流 Agent 框架的完整任务管理机制
- LangGraph checkpoint 机制与 D1 loop-state.json 的模式匹配
- **Anthropic Agent SDK 开源状态确认**（不存在于 GitHub）

### 信息缺口影响评估

| 缺口 | 对 D1 决策的影响 | 可接受程度 |
|------|-----------------|-----------|
| Anthropic Agent SDK 内部细节 | 低 — SDK 文档 404 不影响 D1 自主设计 | 可接受：D1 不需要依赖该 SDK |
| OpenAI Codex Web 版内部 loop | 低 — 仅影响对比完整性，不影响 D1 | 可接受 |
| LangGraph checkpoint 序列化格式 | 中 — 如果计划集成 LangGraph 需要 | 可后续补充 |
| 各框架 error handling/retry | 中低 — 非核心对比维度 | 可后续补充 |

**分析后置信度**: 0.75（主要因 Anthropic Agent SDK 缺口无法消除）

---

## 二、核心洞察

### 洞察 1: LangGraph Checkpoint ID = D1 loop-state.json 的工业级实现

**这是本次研究最重要的发现。**

LangGraph 的设计模式与 D1-goal-investigation 的 loop-state.json + ACTIVE.md 方案高度一致：

| D1 方案 | LangGraph | 模式等价性 |
|---------|-----------|-----------|
| `loop-state.json` — 每个项目存储循环状态 | Checkpoint — 每个图节点保存状态 | **相同**：持久化中间状态 |
| `ACTIVE.md` — 所有项目的索引面板 | Checkpoint ID 索引 — 所有图执行记录的入口 | **相同**：导航入口的导航入口 |
| `ralph-sync.sh` — 同步全局状态到项目 | `resumable_from_checkpoint` — 从检查点恢复 | **相同**：跨会话状态恢复 |
| 端到端导航链：INDEX → ACTIVE → loop-state.json | LangGraph 导航：checkpoint ID → 任意中间状态 | **相似**：精确导航到执行点 |

**结论**: D1 自主设计的 loop-state.json 不是重复造轮子，而是与 LangGraph 的 durable execution 模式**同构**。这意味着：
1. 我们的设计被工业级框架验证
2. 未来可以无缝集成 LangGraph 的 checkpoint 机制
3. 当前方案的复杂度是合理的（不需要过度简化）

### 洞察 2: 客户端驱动 vs 服务端驱动的循环控制

两个关键区别暴露了现有框架的不足：

- **Anthropic API**: tool_use 循环是**客户端驱动**的 — 每轮返回 tool_use block，客户端自行决定下一轮调用
- **LangGraph**: 循环由**图中边定义** — 服务端控制遍历路径

**D1 采用客户端驱动**（每次 session 中 AI 自主决定下一步）。这解释了为什么 D1 需要 loop-state.json — 客户端驱动的循环无法依赖服务端 checkpoint，必须自行持久化状态。

**结论**: loop-state.json 的存在不是因为设计缺陷，而是因为 D1 选择了客户端驱动的架构。

### 洞察 3: 配置文件驱动 vs 代码定义的 tradeoff

| 方式 | 代表框架 | 优点 | 缺点 |
|------|---------|------|------|
| 配置文件驱动 | CrewAI (tasks.yaml) | 声明式、可编辑、非程序员友好 | 动态性差、跨任务依赖难表达 |
| 代码定义 | OpenAI/AutoGen/LangGraph | 动态、可编程、表达能力强 | 需要编程能力 |
| **JSON 状态文件 (D1)** | loop-state.json | **人类可读 + 机器可编辑 + 脚本可自动化** | **需要约定规范** |

**结论**: D1 的 JSON 状态文件方式是配置文件驱动和代码定义之间的**折中选择**。它需要规范（如 loop-state.json schema）来保证一致性。

---

## 三、决策

基于以上分析，做出以下决策：

### 决策 1: 保持 loop-state.json 作为核心导航机制
**理由**: 工业级验证通过（LangGraph 同构），且适配 D1 的客户端驱动架构。

### 决策 2: 不引入外部 Agent 框架
**理由**: D1 的研究目标是理解 Agent 行为的底层机制，而不是构建一个生产级 Agent。引入 LangGraph/CrewAI 等会混淆研究焦点。

### 决策 3: 补充 Anthropic Agent SDK 信息缺口
**行动**: 通过 GitHub API 尝试获取 `agent-sdk-python` 仓库的 README（如果存在）。如果 404 确认，则在报告中标注"Anthropic Agent SDK 可能已废弃或整合进其他项目"。

### 决策 4: 创建 loop-state.json schema 文档
**理由**: 当前 loop-state.json 结构未形式化定义。参考 LangGraph 的 StateGraph 设计模式，应定义 schema 以保证脚本（aggregate-active.sh, ralph-sync.sh）的正确性。

---

## 四、下一步行动建议

1. **验证 ralph-sync.sh stop-hook 集成**（导航链最后一步未验证）
2. **创建 loop-state.json schema 文档**
3. **补充 Anthropic Agent SDK 信息**（如 GitHub API 可访问）
4. **将本次对比结论写入 notes/ 目录**（作为长期知识资产）

---

## 置信度总结

| 维度 | 置信度 | 备注 |
|------|-------|------|
| 整体研究充分性 | 0.75 | Anthropic Agent SDK 缺口拉低 |
| D1 设计合理性 | 0.9 | LangGraph 验证通过 |
| 决策 1-2 确定性 | 0.9 | 结论清晰 |
| 决策 3 可行性 | 0.6 | GitHub API 可能返回 404 |
| 决策 4 优先级 | 0.7 | 非阻塞，但有益于长期维护 |
