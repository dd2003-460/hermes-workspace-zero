# TASKS — D1-goal-investigation 任务板

> 最后更新: 2026-06-12 (ralph-loop iteration 1)

## 新任务（2026-06-12）

### 1. Agent Goal 机制对比研究 — ✅ 已完成
- [x] Claude Code: Stop hook 退出条件分析（notes/01-agent-goal-mechanisms.md）
- [x] Codex: 用户驱动终止 vs 自主完成检测
- [x] Hermes: Gateway Hook（observer）vs Plugin/Shell Hook（injectable）
- [x] 分析"非完成即停止"的共同根因
- [x] 设计改进方向：如何突破"不完整就停"的局限
- [x] **统一研究 memo**: researches/03-agent-stop-mechanism-synthesis.md

### 2. Prompt 激发 AI 提问风格研究 — ✅ 已完成（待实验验证）
- [x] Self-Ask、Tree of Thoughts、Graph of Thoughts 中的提问机制
- [x] System prompt 对 proactive vs reactive 倾向的影响
- [x] Design experiments: different prompt strategies and their effect on questioning rate
- [x] 产出稳定的 questioning prompt template 库（notes/02-prompt-questioning-style.md）
- [x] **实验协议**: 纳入 researches/03-agent-stop-mechanism-synthesis.md §6

## 当前状态

| 任务 | 状态 | 说明 |
|------|------|------|
| goal机制技术调查 | ✅ 已完成 | memory/goal-mechanism-technical-analysis.md (153行) |
| Ralph Loop vs /goal 对比 | ✅ 已完成 | 纳入技术分析文档 |
| 提取对话记录中的用户消息 | ✅ 已完成 | raw/ 中 554 条消息，94.4% 关于 goal/ralph loop |
| **Agent goal 机制对比** | ✅ 已完成 | Unified memo: researches/03-agent-stop-mechanism-synthesis.md |
| **Prompt 激发提问风格** | ✅ 已完成 | Templates + experiment protocol in §6 of unified memo |
| goal架构设计 | 📋 完成建议 | 规划层（Goal 系统）+ 执行层（Ralph Loop）整合方案 |

## 核心发现

1. **根因**: `stop_reason: "end_turn"` ≠ "goal 完成" — 它是 turn-level 信号，不是 goal-level 信号
2. **共同模式**: 三个系统都没有内置 task completion detection
3. **停止决策完全由外部决定**: hook 文件状态、用户指令、或自动结束
4. **突破方案**: Stop hook（最稳健）/ Prompt persistence / 内置完成检测 / Loop wrapper
5. **提问风格激发**: 结构化输出 prompt（D/E 组）预计最稳定，需实验验证

## 产出文件
- `memory/goal-mechanism-technical-analysis.md` — 技术分析归档（153行）
- `researches/01-agent-goal-mechanism-comparison.md` — 三系统对比（原始）
- `researches/03-agent-stop-mechanism-synthesis.md` — **统一研究 memo**（对标 arXiv 格式）
- `notes/01-agent-goal-mechanisms.md` — Claude Code 二进制分析
- `notes/02-prompt-questioning-style.md` — Prompt 模板库

## 数据来源
- 对话日志: 554 条用户消息 (86% 关于 goal/ralph loop)
- Ralph Loop 插件源码分析
- Claude Code 二进制字符串提取
- Hermes Gateway/Plugin/Shell Hook 源码分析

---

*状态唯一来源: TASKS.md*
*origin: ai — 任务状态文档*

---

## 新任务（2026-06-22）

### Thompson Sampling 实证研究 — ✅ 已完成
- [x] 实现 Thompson sampling 多臂老虎机模拟器
- [x] 运行 500 次独立实验，收敛性分析
- [x] 多策略比较：TS vs UCB vs ε-greedy
- [x] 产出实验结果与研究备忘录
- [x] 映射到 AI Agent 置信度驱动决策框架

### 核心发现
1. Thompson sampling regret = 13.67 (远低于 UCB 73.14, ε-greedy 85.85)
2. 最优臂选择率 98%，收敛时间 ~200 轮
3. Beta 分布天然编码置信度，对应 Ralph Loop "置信度驱动自主"
4. 此框架可直接应用到 AI Agent 工具/方法选择问题

## 产出文件
- `researches/04-thompson-sampling-bandit.py` — Thompson sampling 模拟器
- `researches/05-thompson-sampling-results.md` — 实验结果分析
- `researches/06-strategy-comparison.py` — 多策略比较代码
- `researches/07-strategy-comparison-results.md` — 策略比较分析
