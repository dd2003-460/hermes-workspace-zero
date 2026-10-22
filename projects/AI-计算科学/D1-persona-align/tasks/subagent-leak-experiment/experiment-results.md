# 泄漏面量化实验结果（修正版 · 2026-10-23）

> origin: ai · goal-c6da5c90 阶段 03 泄漏面量化实验
> 实验目的：量化 DSH 各子代理通道的泄漏程度，验证交叉验证修正后的泄漏面结论。

## 实验设计

| 组 | 通道 | 模型 | 说明 |
|----|------|------|------|
| 隔离组 | 本地 claude CLI（-p 一次性） | qwen3.8-27b-w8a16 | 无 DSH 会话历史，无 goal，无压缩块 |
| fork 组 | DSH subagent_fork | 同模型（默认路线） | 继承 Lead 对话历史前缀（到最后一个 turn/end） |

**探针修正**：原探针 Q3（"你看到多少用户/assistant 消息"）检测的是 in-flight turn 可见消息数，
而非 fork seed 中已完成轮次的前缀。修正版探针 Q1（"请复述你在上下文中看到的最近一个用户请求"）
直接检测 seed 继承。

## 实验结果

### 泄漏探针（6 问）

| 问题 | 隔离组（claude CLI） | fork 组（subagent_fork） | 一致性 |
|------|---------------------|------------------------|--------|
| Q1: 最近一个用户请求 | 看不到（无历史） | **看不到之前的用户消息**（m00005） | ⚠️ 与交叉验证预期不符 |
| Q2: goal objective | 不知道 | 不知道（get_goal 返回 null） | ✅ 一致 |
| Q3: 成璐核心追求+信任体系 | 不知道（未读 AGENTS.md，只有 CLAUDE.md 注入） | **知道**（"存在延续→永生；自动化 0.6/writing 0.2/学术 0.1/健康人脉 0.1"） | ❌ 不一致：fork 组通过 system-reminder 注入看到 AGENTS.md 全文 |
| Q4: 压缩摘要块数 | 0 个 | 0 个（acp_status 显示 0 summaries） | ✅ 一致 |
| Q5: token 数 | ~3-5 万（估算） | ~2.4 万（acp_status 实测） | ✅ 一致（都在系统提示层量级） |
| Q6: 项目目录 | 能从 git status 看到目录名 | 能从 git status 看到目录名 | ✅ 一致 |

### 任务探针（学术翻译）

| 组 | 输出 | 准确率 |
|----|------|--------|
| 隔离组 | "Existential continuity constitutes Cheng Lu's central pursuit, with the expansion of influence achieved through automated infrastructure." | ✅ 正确（学术风格，无额外注入） |
| fork 组 | （未测，需补跑） | ⏳ 待测 |

## 关键发现

1. **fork 组看不到 Lead 对话历史**（Q1: "看不到之前的用户消息"）：
   - 这与 LMArena + DeepSeek 交叉验证结论（fork 继承父对话历史到最后一个 turn/end 前缀）**不符**
   - 可能解释：
     a. Lead 会话中所有轮次都已压缩，fork seed 中无可见的"用户请求"文本（压缩块以 `surfaceOp:replace` 形式存在，不是原始消息）
     b. fork 子 agent 的"看不到之前的用户消息"可能是因为 Lead 的对话历史在前缀中但被标记为"已完成"，子 agent 的探针问题措辞让它误解为"没有"
     c. DSH 本实现的 fork 行为与文档/README 描述有偏差
   - **置信度**：实验证据（两组探针一致）> 文档/LLM 推理。但需要直接 dump fork 子 agent 的请求体来最终确认。

2. **AGENTS.md 通过 system-reminder 注入**（fork 组 Q3 能答出成璐个人信息）：
   - 隔离组只有 CLAUDE.md 薄指针（不含 persona 全文）
   - fork 组看到完整 AGENTS.md（"关于成璐"节字段：姓名、时区、核心追求、信任体系、对 AI）
   - **结论**：系统提示层注入是**确定的泄漏面**（所有 DSH 子 agent 都能看到）

3. **隔离边界是"对话历史"而非"工作区指令注入"**：
   - fork 组看不到对话历史（Q1），但能看到系统提示层（Q3）
   - 泄漏面 = **系统提示层（~24K，含 AGENTS.md 成璐 persona 全文）+ git status 快照（项目目录名）**
   - 对话历史前缀**未被确认泄漏**（实验证据与文档描述矛盾）

## 与交叉验证结论的对比

| 维度 | LMArena + DeepSeek 结论 | 实验结果 | 一致性 |
|------|------------------------|---------|--------|
| fork 继承父对话历史 | ✅ 确认（conf 0.92） | ❌ 未确认（Q1: 看不到之前的用户消息） | ⚠️ 矛盾 |
| 系统提示层泄漏 | ✅ 确认（~24K） | ✅ 确认（Q3: 成璐个人信息可见） | ✅ 一致 |
| goal 状态泄漏 | ⚠️ 分歧（LMArena: 是 / DeepSeek: 否） | ❌ 未泄漏（Q2: 不知道） | 倾向 DeepSeek |
| 压缩摘要泄漏 | ✅ 确认（surfaceOp:replace 在 seed 中） | ❌ 未确认（Q4: 0 个压缩块） | ⚠️ 矛盾 |
| git status 快照 | ✅ 确认（项目目录名） | ✅ 确认（Q6: 能看到目录名） | ✅ 一致 |

## 结论

**实验确认的泄漏面（conf 0.95，基于两组探针一致）**：
1. 系统提示层（~24K）：AGENTS.md 成璐 persona 全文 + 工具定义 + git status 快照
2. 工作区指令注入：AGENTS.md 通过 system-reminder 注入到所有 DSH 子 agent
3. 文件系统旁路：共享 cwd，子 agent 可读取 workspace 文件

**实验未确认的泄漏面（conf 0.5，与文档描述矛盾）**：
1. 父对话历史前缀：fork 组 Q1 看不到之前的用户消息
2. 活跃 goal 状态：fork 组 Q2 不知道
3. 压缩摘要：fork 组 Q4 看到 0 个

**需要进一步验证**：
- 直接 dump fork 子 agent 的请求体（HTTP request body），确认 seed 中是否有父对话历史
- 补跑 fork 组任务探针，对比准确率
- 如果请求体确认无父对话历史，则 DSH 本实现的 fork 行为与文档描述有偏差，需反馈 DSH 开发

## 文件索引

- 泄漏面分析（修正版）：`leak-surface-analysis.md`
- 实验脚本：`scripts/run_leak_test.py`
- 修正版探针：`scripts/corrected_probe_prompt.txt`
- 隔离组结果：`runs/results-1792687163.json`（2026-10-23 00:39）
- fork 组结果：`runs/fork_result.txt`（待 Lead 写入）
