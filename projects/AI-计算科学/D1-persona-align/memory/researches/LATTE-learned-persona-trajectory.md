### 摘要
根据任务上下文自适应调整 token 粒度, 支持 learned persona trajectory 预测.

### 核心方法
1. 从训练数据学习 adaptive token 策略
2. 动态预测最佳 token 粒度
3. 证明 learned persona (动态预测) > learned persona (静态 profile)

### 对 persona-v3 的启示
"自适应精度"维度已隐含 token 粒度自适应, 但 LATTE 提供了具体的训练方法.

### 与 persona-v3 的关键洞察
LATTE 证明静态 learned persona < 动态 learned persona trajectory. persona-v3 通过 prompt 层动态适应而非序列预测器实现相同目标 — 这是零训练成本的替代方案.