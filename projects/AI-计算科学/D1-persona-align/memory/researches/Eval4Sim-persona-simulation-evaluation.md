### 摘要
针对模拟人格的评估框架, 提供多维度的 persona 评估指标.

### 核心方法
1. 定义 persona 一致性, 多样性, 独特性的量化指标
2. 多维度评估体系
3. 建立 persona simulation 的 benchmark

### 对 persona-v3 的启示
Eval4Sim 的多维度评估与 persona-v3 的 6 维度高度互补. 可以互相验证:
- Eval4Sim 的一致性指标 ≈ persona-v3 dimension coverage
- Eval4Sim 的多样性指标 ≈ persona-v3 adaptive exploration
- Eval4Sim 的独特性指标 ≈ persona-v3 behavioral constraints

### 改进建议
建立 persona-v3 维度与 Eval4Sim 指标的映射关系