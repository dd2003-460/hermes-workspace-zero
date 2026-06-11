# Learning Personalized Agents from Human Feedback

## 来源
Liang, Kruk, Qian, Yang, Bi, Yao, Nie, Zhang, Liu, Fisac, Zhou, Hosseini

## 核心问题
AI 需要适应 evolving user preferences，但 static training data 无法处理动态变化。

## 方案
Online learning loop：
1. **Clarify intent before acting** — 行动前先澄清意图
2. **Retrieve stored preferences** — 检索存储的偏好
3. **Update memory based on post-interaction feedback** — 根据交互后反馈更新记忆

## 关键发现
1. **动态偏好是核心挑战** — 用户偏好会随时间变化，静态 persona 不够
2. **online learning loop 是必要机制** — 需要在交互中持续更新
3. **clarify-then-act 减少错误** — 行动前确认意图比盲动更好

## 与 persona-v3 的关联

### 直接支持
1. **clarify intent = persona-v3 追问机制** — 两个理念完全一致
2. **post-interaction feedback update** — 对应 persona-v3 的记忆传递和自适应先验
3. **evolving persona** — persona-v3 当前是静态的，但成璐的偏好也会随时间变化

### 改进方向
1. **在线更新机制** — persona-v3-prompt.txt 目前是静态的，可以考虑增加 feedback loop
2. **但成璐场景不同** — 成璐是"数字分身"延续其已有意志，不是学习新用户。静态 persona 更合适
3. **折中方案** — 保持 prompt 静态，但 memory/ 中的分析文件可以持续更新

## 关键引用
> "preferences that change over time with static training data"
> "online learning loop that clarifies intent before acting"
