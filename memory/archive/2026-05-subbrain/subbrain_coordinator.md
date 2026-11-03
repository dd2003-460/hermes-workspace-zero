# Ralph SubBrain 协调器

## 目的
通过循环迭代推进工作区任务。每个 iteration：
1. 读取上轮输出 (memory/notes/subbrain_iteration_XX.md)
2. 检查阻塞项是否解除
3. 推进可执行的工作
4. 写入本轮报告
5. 提出下一步

## 迭代序列
- Iteration 1 (01:03): 项目结构检查 ✅ — 部分误报（D1-anyon-hawking memory/ 实际存在，.bak 文件仅 14 个）
- Iteration 2 (02:00): 纠错 + 全面诊断 — 无状态变化，阻塞项待作者决策
- 下一轮迭代检查项:
  - arXiv 提交是否进行
  - D1-anyon-hawking 是否值得 1-loop 推进
  - workspace 是否有新的活跃任务
  - bayesian-frame 项目迁移
