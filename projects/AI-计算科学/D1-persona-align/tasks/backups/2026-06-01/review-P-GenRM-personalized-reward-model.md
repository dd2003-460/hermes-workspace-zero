# P-GenRM: Personalized Generative Reward Model with Test-time User-based Scaling

## 基本信息
- **论文**: P-GenRM: Personalized Generative Reward Model with Test-time User-based Scaling
- **作者**: Pinyi Zhang, Ting-En Lin, Yuchuan Wu, Jingyang Chen, Zongqi Wang, Hua Yang, Ze Xu, Fei Huang, Kai Zhang, Yongbin Li
- **来源**: arXiv
- **相关度**: 极高相关

## 核心贡献

P-GenRM 是首个带有"测试时用户缩放"的个性化生成奖励模型。传统方法在个性化奖励建模中过度简化偏好信号，P-GenRM 的创新在于：

1. **测试时用户缩放 (Test-time User-based Scaling)**: 在推理阶段根据用户特征动态调整奖励模型输出，提供额外的 3% 性能提升
2. **用户原型聚类 (User Prototypes)**: 将用户聚类为原型，使偏好推断从个体噪声中泛化
3. **双粒度缩放机制 (Dual-granularity Scaling)**: 在用户原型级别和个体级别分别进行缩放，减轻噪声同时保持个性化

## 与 persona-v3 的关联

### 对齐 Checkpoint 的量化信号
P-GenRM 提出的"准确的用户特定奖励信号"与 persona-v3 alignment_checker 的**对齐全分**概念同构：
- persona-v3 通过 6 维度评估检测对齐度 (alignment score)
- P-GenRM 通过用户特定奖励建模检测偏好对齐
- 两者共同指向一个核心问题：**如何量化 AI 输出与目标用户偏好的对齐程度**

### 用户原型聚类 → persona-v3 6 维度的校准
P-GenRM 的用户原型聚类为 persona-v3 提供了新的视角：
- persona-v3 的 6 维度 (精度/探索/感知/先验/自我/投影) 可以看作是"粗粒度用户原型"
- P-GenRM 的双粒度缩放为 persona-v3 提供了从粗粒度 (persona) 到细粒度 (个体) 的迁移框架

## 可迁移的技术

1. **测试时缩放机制**: persona-v3 alignment_checker 可以考虑在推理时对不同维度进行动态加权 (类似 P-GenRM 的 test-time scaling)
2. **用户原型聚类**: 可以用于构建多人格模板库，根据输入自动选择最接近的原型
3. **双粒度缩放**: 可以用于 persona-v3 的权重自适应 — 粗粒度按 persona 原则调整，细粒度按具体上下文调整

## 对 persona-v3 的影响

P-GenRM 验证了一个关键假设：**个性化不是静态的对齐，而是动态的、可扩展的过程**。这与 persona-v3 的"自适应"核心原则完全一致 — 自适应精度、自适应探索、自适应先验等维度本质上都是在不同粒度上实现测试时缩放。

## 评估标准 (ReportBench 视角)

- **引用相关性**: 3/3 — 直接支持 persona-v3 核心假设
- **事实可信度**: 4/4 — 实证论文，有 benchmark 验证
