### 摘要
使用 activation patching 检测和分析 persona 在推理过程中的作用.

### 核心方法
1. 通过 activation patching 定位 persona 相关的 latent representations
2. 观察 persona 激活如何影响推理路径
3. 证明 persona 不是 post-hoc 修饰, 而是推理过程的核心部分

### 对 persona-v3 的启示
传统 prompt-based persona 评估只能检测关键词, 而 activation-based 可以检测"真实的人格表达". persona-v3 可以未来尝试 finetune persona-specific activation probes.

### 与 persona-v3 的协作
Activation patching 是检测层, persona-v3 是控制层. 两者结合可以实现闭环 persona 管理.