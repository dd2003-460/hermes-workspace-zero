# Iteration 210: 从迭代日志提取 Prompt 推理相关论文

## 目标
响应 TASKS.md 中新任务"Prompt深度推理激发研究", 调研现有覆盖度并从迭代日志提取相关论文.

## 调研结果

### 覆盖度检查

| 关键词 | 覆盖 | 说明 |
|--------|------|------|
| prompt结构 | 无覆盖 | researches/ 中无此关键词 |
| 推理激活 | 无覆盖 | |
| chain of thought / cot | 无覆盖 | |
| context length | 无覆盖 | |
| 指令跟随 | 无覆盖 | |
| behavior activation | 无覆盖 | |
| 深度推理 | 无覆盖 | |

### 迭代日志中的相关论文

尽管 researches/ 覆盖度低, 但迭代日志中有相关论文:
- iteration-147: CoPrompter, Promptware Engineering, BiasRunsDeep, LoveFirstKnowLater
- iteration-166: LATTE, RGoT, PPAI, HydraPrompt, TAME

## 执行动作

从迭代日志提取 3 篇最相关的论文到独立摘要:

| 文件 | 论文 | 来源 | 相关度 |
|------|------|------|--------|
| BiasRunsDeep-persona-reasoning-bias.md | 浅层 persona 分配产生推理偏差 | iteration-147 | 高 |
| RGoT-rl-adaptive-prompt.md | RL 驱动自适应 prompt 生成 | iteration-166 | 高 |
| CoPrompter-instruction-alignment.md | 用户中心 LLM 指令对齐评估 | iteration-147 | 中 |

## 关键发现: BiasRunsDeep

"浅层人格分配 ≠ 深层认知架构" — 这是 persona-v3 设计的最重要实证支持:
- 传统 persona = 角色标签 → 有偏推理
- persona-v3 = 思维习惯 + 6 维度 → 无偏认知架构
- 6 维度 (自适应精度/探索/感知/先验/自我/投影) 是认知策略, 不是角色设定

## 教训

1. 迭代日志是宝贵的信息资源 — 论文信息往往只存在于迭代日志中, 需要定期提取到独立文件
2. researches/ 目录的覆盖度滞后于迭代日志 — 这与 iteration 206 的"综述文件滞后"同类
3. 建议: 将"从迭代日志提取相关论文到独立文件"加入周期性维护清单
