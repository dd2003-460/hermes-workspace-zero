### 摘要
通过价值观引导 LLM 行为, 证明价值观比规则列表更有效.

### 核心方法
1. 从人类价值观数据中学习 steering vector
2. 价值观对齐比行为对齐更稳定
3. 价值观作为 higher-level constraint

### 对 persona-v3 的启示
persona-v3 behavioral constraints 本质上是价值观约束. Teaching Values 证明从价值观出发比从规则列表出发更稳定.

### 改进建议
将 behavioral constraints 从"规则列表"升级为"价值体系" — 定义核心价值观 (简洁/直接/不解释) 而非具体规则 (避免"总的来说")