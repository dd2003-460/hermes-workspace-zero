# FileGram: Grounding Agent Personalization in File-System Behavioral Traces

## 来源
Liu, Tian, Hu, Dong, Yang, Li, Yang, Loy, Ziwei Liu

## 核心问题
Privacy boundaries 导致数据约束严重，传统 personalization 依赖对话日志。

## 方案
从 atomic file operations 构建用户 profile，引入新的 memory evaluation benchmark。

## 关键发现
1. **文件操作 > 对话日志** — 用户对文件系统的行为比对话更能反映真实 persona
2. **atomic trace 作为 grounding** — 每个文件操作是一个不可辩驳的事实锚点
3. **privacy-preserving** — 不需要对话内容，只需要文件操作日志

## 与 persona-v3 的关联

### 高度互补
1. **D1-persona-align 项目本身就是 file-system behavior** — 所有 analysis 文件、scripts、researches 都是成璐的文件操作 trace
2. **FileGram 的思路验证了 persona-v3 的数据来源** — 52 个 idea analysis 文件 + researches + scripts 已经是完整 persona trace
3. **benchmark 可复用** — FileGram 的 memory evaluation benchmark 可以用作 persona-v3 的额外评估维度

### 改进方向
1. **FileGram benchmark 集成** — 考虑将文件操作一致性作为 persona-v3 评估的额外维度
2. **trace-based grounding** — persona-v3 self-preservation 可以参考 atomic trace 思路

## 关键引用
> "effective personalization remains limited by severe data constraints due to strict privacy boundaries"
> "builds user profiles from atomic file operations rather than conversation logs"
