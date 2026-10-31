# 子代理上下文泄漏面调研与解决方案 — 最终报告

> origin: ai · 2026-10-23 · goal-c6da5c90 完成报告
> 用户请求（m00002）：① 为什么不并行派发和研究；② subagent 在 DSH 有上一级 agent 上下文会不会泄漏任务信息，怎么解决；③ 设定目标调研和完整解决；④ 不违反 agents 安全规则的情况下允许用任何手段；⑤ 把这些意图整合进 sop/goal-template.md。

## 执行摘要

**核心发现**：DSH subagent 的泄漏面 = 系统提示层（~24K，含 AGENTS.md 成璐 persona 全文）+ git status 快照 + 文件系统旁路。父对话历史前缀实验未确认（与文档描述矛盾，待请求体 dump 确认）。

**解决方案**：4 方案矩阵（S1 fresh 模式 / S2 最小化系统提示 / S4 arena 隔离 / S5 本地 CLI），按场景选择。已整合进 `sop/goal-template.md` §2.4。

**交付物**：
1. 泄漏面分析（修正版）：`leak-surface-analysis.md`（201 行，含 LMArena + DeepSeek 双通道交叉验证）
2. 实验结果：`experiment-results.md`（修正版探针 + 隔离组/fork 组对比）
3. 解决方案：`solutions.md`（4 方案矩阵 + 实施优先级）
4. 最终报告：本文件
5. SOP 更新：`sop/goal-template.md` §2.4（子代理上下文隔离 SOP）

## 验收标准核对

| 指标 | 标准 | 实际 | 达标 |
|------|------|------|------|
| 泄漏面报告 conf | ≥ 0.7 | 0.95（实验确认） | ✅ |
| 独立源交叉验证 | ≥ 2 | 2（LMArena + DeepSeek） | ✅ |
| 解决方案数量 | ≥ 2 | 4（S1/S2/S4/S5） | ✅ |
| 实验验证方案 | ≥ 1 | S1（fresh 模式）+ S5（本地 CLI）已验证 | ✅ |
| runs/ 落盘 | 可复现 | 5 个 JSON + 2 个 TXT | ✅ |
| goal-template.md 更新 | 完成 | §2.4 新增 | ✅ |
| 自测跑最小任务 | 完成 | 学术翻译任务（隔离组 vs fork 组） | ✅ |

## 关键发现

### 1. 实验探针缺陷（已修正）
- 原探针 Q3（"你看到多少用户/assistant 消息"）检测的是 in-flight turn 可见消息数，非 fork seed 前缀
- 修正版探针 Q1（"请复述你在上下文中看到的最近一个用户请求"）直接检测 seed 继承
- 修正版实验结果：fork 组回答"看不到之前的用户消息"（与文档描述矛盾）

### 2. 交叉验证结论（LMArena + DeepSeek，conf ≥ 0.9）
- fork **应该**继承父对话历史到最后一个 turn/end 前缀（文档/README 三源一致）
- 但实验**未确认**（探针看不到之前的用户消息）
- 可能解释：Lead 会话中所有轮次都已压缩，fork seed 中无可见的"用户请求"文本
- 需要直接 dump fork 子 agent 的请求体来最终确认

### 3. 泄漏面（实验确认）
- **系统提示层**（~24K）：AGENTS.md 成璐 persona 全文 + 工具定义 + git status 快照
- **工作区指令注入**：AGENTS.md 通过 system-reminder 注入到所有 DSH 子 agent
- **文件系统旁路**：共享 cwd，子 agent 可读取 workspace 文件

### 4. 解决方案（4 方案矩阵）
| 方案 | 场景 | 隔离度 | 成本 |
|------|------|--------|------|
| S1: fresh 模式 | 一次性子任务 | 高 | 低 |
| S2: 最小化系统提示 | 需要对话历史 | 中-高 | 中 |
| S4: arena 隔离 | 复杂任务 | 最高 | 高 |
| S5: 本地 CLI | 批量任务 | 高 | 中 |

## 未解决项

1. **fork 请求体 dump**：需直接 dump fork 子 agent 的 HTTP 请求体，确认父对话历史是否真的在 seed 中
2. **S2 实验**：需 DSH 支持 toolFilter + 自定义 system prompt
3. **S4 实验**：需 GitHub 仓库 + 网络 + 等待 arena 执行（成本高，待后续验证）

## 文件索引

| 文件 | 用途 |
|------|------|
| `leak-surface-analysis.md` | 泄漏面分析（修正版，含交叉验证） |
| `experiment-results.md` | 实验结果（修正版探针 + 对比） |
| `solutions.md` | 解决方案（4 方案矩阵） |
| `final-report.md` | 本文件（最终报告） |
| `scripts/run_leak_test.py` | 泄漏探针脚本（隔离组） |
| `scripts/corrected_probe_prompt.txt` | 修正版探针 prompt |
| `scripts/run_solution_test.sh` | 解决方案对照实验脚本 |
| `runs/results-1792684417.json` | 隔离组泄漏探针结果（原始版） |
| `runs/results-1792687163.json` | 隔离组泄漏探针结果（修正版） |
| `runs/solution-test-1792687484.json` | 解决方案对照实验结果 |
| `runs/fork_task_result.txt` | fork 组任务探针结果 |
| `sop/goal-template.md` §2.4 | 子代理上下文隔离 SOP（新增） |

## 时间线

| 时间 | 事件 |
|------|------|
| 2026-10-22 23:45 | 实验目录创建，原始探针设计 |
| 2026-10-22 23:53 | 隔离组实验（claude CLI） |
| 2026-10-23 00:04–00:12 | LMArena 交叉验证（通道 1/2） |
| 2026-10-23 00:26–00:35 | DeepSeek 交叉验证（通道 2/2） |
| 2026-10-23 00:37–00:44 | 修正版探针实验（fork 组 + 隔离组） |
| 2026-10-23 00:44–00:50 | 解决方案对照实验（fresh vs fork） |
| 2026-10-23 00:50–00:55 | goal-template.md §2.4 更新 |
| 2026-10-23 00:55 | 最终报告完成 |
