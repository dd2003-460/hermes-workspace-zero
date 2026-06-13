# 1-loop Brain Sub — Iteration 28

## 当前状态
迭代 27 完成了:
- Agent goal 机制对比（Claude Code/Codex/Hermes 三系统分析）
- Prompt 提问风格研究（4个模板+2个实验设计）
- D1-goal-investigation 项目重建

## 质询问题

### 1. "非完成即停止"的根因分析是否有应用价值？
我们发现三个 Agent 的停止根因都是"无内置 completion detection"。
这意味着 Ralph Loop 的 stop hook 是唯一有效的突破方式。
但 stop hook 也有局限（状态文件管理复杂、容易出错）。

**建议**: 是否应该设计一种"prompt-only"的 continuation 机制？
即在 system prompt 中声明任务状态，让 LLM 在每次 turn 开始时自我检查任务完成度，
如果未完成则主动继续工作（不调用退出）？

### 2. 提问风格模板是否应该在 Ralph Loop 中试验？
4个模板中，模板C（持续提问循环）和模板D（置信度+提问）特别适合 Ralph Loop。
**建议**: 在下一次 Ralph Loop 迭代中使用这些模板，测试是否能稳定激发提问。

### 3. S1-1 Thompson sampling 实证是否应该启动？
S1-1 的实证可以验证工具搜索-探索折衷的变分原理。
这是比抽象形式化更有价值的产出。
**建议**: 先启动 S1-1 实证，用简单的 multi-agent tool selection 任务。

### 4. D1-goal-investigation 项目的最终产出应该是什么？
这个项目目前产出了：
- Agent goal 机制对比
- Prompt 提问风格研究
- 用户消息提取分析

但它的"research contribution"是什么？
**建议**: 定义一个明确的 research question，比如：
"How do AI agents decide when to stop, and how can this be improved?"
