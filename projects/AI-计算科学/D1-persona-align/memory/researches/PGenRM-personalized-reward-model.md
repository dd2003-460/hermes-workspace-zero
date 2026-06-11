### 摘要
为每个用户训练个性化奖励模型, 评估生成质量.

### 核心方法
1. 基于用户交互数据训练个性化奖励模型
2. 评估不同 persona 下的生成质量
3. 建立 user-specific reward landscape

### 对 persona-v3 的启示
persona-v3 alignment_checker 本质上是一个粗糙的奖励模型. P-GenRM 证明 per-user reward model 比通用 scorer 更准确.

### 改进建议
将 persona-v3 的 6 维度权重与 user-specific 偏好结合 (如成璐更看重"跨域类比"而非"信息论第一")