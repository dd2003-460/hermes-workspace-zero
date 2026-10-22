# 子代理上下文隔离解决方案

> origin: ai · 2026-10-23 · goal-c6da5c90 阶段 04 解决方案设计
> 前提：实验确认的泄漏面 = 系统提示层（~24K，含 AGENTS.md 成璐 persona 全文）+ git status 快照；
> 父对话历史前缀未确认泄漏（实验与文档矛盾，待请求体 dump 确认）。

## 方案矩阵（隔离度 × 成本 × 能力）

| 方案 | 隔离度 | 成本 | 能力保留 | 适用场景 | 可行性 |
|------|--------|------|---------|---------|--------|
| S1: 强制 fresh 模式 | 高（丢系统提示外的所有） | 低 | 中（子 agent 需自包含 prompt） | 一次性子任务（翻译/提取/格式化） | ✅ 可行（DSH 已支持 context:"fresh"） |
| S2: 最小化系统提示 | 中-高 | 中 | 高（保留必要工具） | 需要工具但隔离对话历史 | ⚠️ 需 DSH 配置支持（toolFilter + 精简 system） |
| S3: 任务白名单注入 | 高 | 中 | 中（只注入任务相关文件） | 需要特定文件但不需要对话历史 | ⚠️ 需 DSH 支持选择性注入 |
| S4: arena 完全隔离 | 最高（独立 harness） | 高（需 GitHub 仓库 + 网络） | 高（arena 有完整执行层） | 复杂任务（调研/核验/代码审查） | ✅ 可行（已有 SOP） |
| S5: 本地无上下文模型 | 高 | 中（需 API key 或本地 CLI） | 中（只喂任务文件） | 批量任务（翻译/提取/生成） | ✅ 可行（claude CLI 已验证） |
| S6: 上下文脱敏 | 中 | 高（需脱敏管道） | 高（保留对话历史但去敏感信息） | 需要对话历史但不能泄漏敏感信息 | ⚠️ 需 DSH 支持（目前无脱敏管道） |

## 推荐方案组合（按场景）

### 场景 A：一次性子任务（翻译/提取/格式化/简单分析）
**推荐**：S1（强制 fresh 模式）+ 自包含 prompt
- 机制：`subagent_fork(context:"fresh", prompt="...")`，prompt 包含目标 + 输出格式 + 边界
- 泄漏面：只有系统提示层（AGENTS.md 成璐 persona），无对话历史
- 成本：低（只需写自包含 prompt）
- 验证：隔离组任务探针准确率 100%（学术翻译正确输出）

### 场景 B：复杂任务（调研/核验/代码审查/多文件协同）
**推荐**：S4（arena 完全隔离）
- 机制：任务书 + 仓库文件 → arena agent（独立进程，独立 harness）
- 泄漏面：只有仓库文件 + 任务书 + 注入的 SOP
- 成本：高（需 GitHub 仓库 + 网络 + 等待 arena 执行）
- 验证：已有 SOP（`.claude/skills/arena-outsource/SKILL.md`）
- 注意：仓库文件本身可能含敏感信息（如 persona-distill 仓库含风格样本），需预脱敏

### 场景 C：批量任务（大量翻译/提取/生成）
**推荐**：S5（本地无上下文模型）
- 机制：本地 claude CLI（-p 一次性），只喂任务文件
- 泄漏面：只有工作目录 git status + CLAUDE.md 注入
- 成本：中（需 API key 或本地 CLI）
- 验证：隔离组实验已确认（claude CLI qwen3.8 不知道 goal/信任体系数值）
- 注意：subagent 无网络（AGENTS.md 网络规则），由 Lead 代查并写入文件

### 场景 D：需要对话历史的子任务（续写/跟进/基于 Lead 决策）
**推荐**：S2（最小化系统提示）+ S6（上下文脱敏，如果 DSH 支持）
- 机制：`subagent_fork(context:"fork")` + 精简 system prompt（不含 persona 全文）
- 泄漏面：对话历史 + 精简系统提示（无 persona）
- 成本：中（需 DSH 配置支持）
- 验证：⏳ 待测（需 DSH 支持 toolFilter + 自定义 system）

## 实施优先级

1. **立即可用**：S1（fresh 模式）— 已有 DSH 支持，只需在任务派发时强制 context:"fresh"
2. **短期可用**：S5（本地 CLI）— 已有 claude CLI，只需封装脚本
3. **中期待 DSH 支持**：S2（toolFilter + 精简 system）— 需 DSH 配置能力
4. **已可用但成本高**：S4（arena）— 已有 SOP，适合复杂任务

## 待验证项

- [ ] fork 子 agent 请求体 dump：确认父对话历史是否真的在 seed 中
- [ ] S1 场景 A 实验：fresh 模式 vs fork 模式，同一任务准确率对比
- [ ] S2 场景 D 实验：精简 system prompt 是否减少泄漏面
- [ ] S4 场景 B 实验：arena 隔离 vs fork，同一复杂任务准确率对比
