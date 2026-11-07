# origin: human（原始 idea）+ ai（迁移整理与实现思路）

> 来源：`~/workspace-zero/tasks/`（2026-03-29 提取，1110 个对话文件 → 808 条研究想法）
> 迁移日期：2026-11-07
> 数据文件：`ideas-2026-03-extracted-raw.json`（808 条原始）、`ideas-2026-03-themed.json`（按主题归类）

## 这是什么

成璐 2026 年 2-3 月与多个 AI 服务（Claude/DeepSeek/Gemini 等）的对话记录，经自动提取后得到的 **808 条研究想法**。每条包含：来源文件、日期、用户原话（original_quote）、摘要。

**不是新产生的 idea**——是历史对话的挖掘产物。价值在于：这些想法当时散落在上千个会话文件里，现在集中可检索。

## 主题分布（7 大主题 + 未归类）

| 主题 | 条数 | 占比 | 核心内容 |
|------|------|------|----------|
| AI & 机器学习系统 | 566 | 70% | D1 系统架构、写作元优化、信息论方法 |
| 自主智能体系统 | 129 | 16% | Zero 智能体：持续运行、身份锁定、状态管理 |
| 学术写作与出版 | 31 | 3.8% | Writing Sample 系列、投稿策略、LaTeX |
| 研究方法论与认识论 | 15 | 1.9% | 正交化分解、分类即压缩、多视角验证 |
| 理论物理与数学 | 10 | 1.2% | P vs NP、Metric-Affine 几何、认知边界 |
| 资本与金融策略 | 8 | 1.0% | 信息不对称套利、统计套利 |
| 学术生涯与平台建设 | 3 | 0.4% | PhD 申请、宽松教职定义 |
| 未归类 | 46 | 5.7% | — |

## 实现思路（从 summary 提案提取）

### 主推方向：持久自主智能体架构

**题目**：*Persistent Cognitive Loop: A Single-Brain Architecture for 24/7 Autonomous AI Agents with State Continuity and Self-Reflection*

**核心创新点**：
1. **认知循环**：cron → 读思维流 → 生成新想法 → 更新状态 → 执行任务 → 压缩归档（闭环）
2. **类人状态模型**：mood / energy / interests，使行为可预测
3. **身份锁定**：配置文件不可改，身份恒定
4. **三层记忆压缩**：500 行完整 → 7 天摘要（5KB）→ 长期精华（2KB）

**已有实现**（Zero 智能体，workspace-zero 中）：
- ✅ 单主脑 + cron 每 5 分钟一轮
- ✅ soul_state.json 持久化
- ✅ continuous_thought.md 追加
- ✅ Discord/Telegram 推送
- ❌ 6 个已知缺陷（energy 无恢复、compress 膨胀 bug、stale backup 未清理、day/dawn 切换、紧急干预缺失、归档检索缺失）

**17 周计划**（原提案）：
- 阶段 1（4 周）：修 bug + 补功能
- 阶段 2（6 周）：三条件对照实验（baseline / fixed / enhanced）
- 阶段 3（6 周）：分析 + 写作 + 投稿

**目标 venue**：AAMAS / IAAI / ASPLOS workshop / HCOMP

### 其他可执行子方向

| 方向 | 来源 | 状态（2026-03） | 当前关联 |
|------|------|----------------|----------|
| 思维流压缩算法形式化 | AI 系统主题 | 未开始 | → D1-memory / D1-memory-hooks |
| 正交化过程方法论 | 方法论主题 | 概念阶段 | → pfb 1-loop 01 阶段已部分落地 |
| 分类即压缩（信息论） | 方法论主题 | 概念阶段 | → pfb rubric O3 surprisal 加权（TASK-surprisal-reward-survey.md） |
| 量化金融论文 | 金融主题 | arXiv 就绪 | → 独立项目，非 academic-AI 主线 |
| Writing Sample Ch5 | 写作主题 | 进行中 | → 写作-社会系统/ |

## 与当前工作区的映射

这批 idea 产生于 2026-03，当时 workspace 结构不同（`~/Desktop/D1/`）。迁移到当前 `D1-academic-AI/raw/` 的理由：
- raw/ 优先原则：原始思维归 raw/
- 主题归属：AI 系统 + 自主智能体 = D1-academic-AI 的核心范围
- 不与 pfb 冲突：pfb 是 prompt-first 消融实验（2026-10 起），这批是更早的系统级 idea

**注意**：其中"自主智能体"方向的很多 idea 已在后续工作中被吸收或替代（如 D1-persona-align 的身份机制、D1-memory 的压缩方案）。本文件是**原始记录**，不代表当前最优方案——做决策时以各项目 loop-state.json 为准。

## 局限（继承自原报告）

1. 提取基于关键词过滤（20+ 词），可能有漏检
2. 部分 JSON 结构异常被跳过
3. 2026-03 时 web 搜索不可用，文献空白判断基于对话推断
4. "summary" 字段对短消息就是原话本身（无额外摘要）