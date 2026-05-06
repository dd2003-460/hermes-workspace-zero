# 相关文献检索框架 — 理论发展前置检查

**创建**: 2026-05-04（迭代 49 → 50 过渡期）
**目的**: 理论构建前的学术查检索体系，确保知识贡献的增量定位

---

## 一、当前能力声明

### 训练知识覆盖范围
本系统基于预训练语料（截至 2025 年），对以下领域有较高的理论覆盖：

| 领域 | 覆盖度 | 关键理论/作者 |
|------|--------|---------------|
| 动力学系统/同步 | ★★★★☆ | Kuramoto (1975), Winfree (1967), Strogatz (2000) |
| 统计物理/相变 | ★★★★☆ | Ising 模型、临界现象、Haken 协同学 |
| 博弈论/协调博弈 | ★★★★☆ | Kandori-Mailath-Rob (1993), Ellison (1993) |
| 信息论/学习理论 | ★★★★☆ | VC 维度、PAC 学习、信息瓶颈 |
| 社会动力学 | ★★★☆☆ | Schelling 隔离模型、Hegselmann-Krause |
| 认知科学 | ★★★☆☆ | 有限理性、有界置信度 |
| 量子信息几何 | ★★☆☆☆ | Bures 距离、量子统计流形 |
| 复杂网络 | ★★★☆☆ | 小世界、无标度、社区检测 |

### Web 检索工具状态
| 工具 | 状态 | 备注 |
|------|------|------|
| WebSearch | ❌ 受限 | arXiv/Google Scholar 422 错误 |
| WebFetch | ⚠️ 部分可用 | Google Scholar 有反爬验证 |
| arXiv API | ❌ 受限 | 需要直接 HTTP 请求 |

---

## 二、D45 自证预言文献清单（训练知识）

### 经典理论
1. **Thomas Theorem (1928)** - "如果人们将情境定义为真实的，那么其在后果上就是真实的"
   - 社会心理学基础：信念定义现实

2. **Merton (1948)** - "自证预言" 术语创始人
   - 文献：《自证预言的社会学》(1968)

3. **Popper "Oedipus Effect"** - 预测对被预测事件的影响

4. **Pygmalion Effect (Rosenthal & Jacobson, 1968)** - 教师期望效应

### 数学模型
5. **Schelling 隔离模型 (1971)** - "Dynamics Models of Segregation"
   - **最关键相关**：agent-level threshold 模型（"如果邻居 X% 是某类人，我就离开"）
   - **数学形式**：布尔阈值 → 宏观 segregation pattern
   - **与你 D45-B 的关联**：完全一致——信念阈值触发行为对齐

6. **Granovetter 阈值模型 (1978)** - 集体行为中的行为级联
   - agent 有异质阈值 θ，当 ≥ θ 的邻居采取行动时跟随

7. **DeGroot 意见动力学 (1974)** + **Friedkin-Johnsen (1990)**
   - 信念更新：x(t+1) = Wx(t) + v（加权平均 + 先验）

8. **KMRW 演化博弈 (1993)** - "Social Learning and Play"
   - 小扰动均衡选择 → 你的 D45-A 类似逻辑斯谛增长

9. **Hegselmann-Krause (2002)** - 有界置信度模型
   - 只与信念距离 < ε 的 agent 互动 → 集群形成

10. **Acemoglu-Ozdaglar (2011)** - 社交网络中学习
    - 贝叶斯学习 + 群体行为级联

### 正反馈模型
11. **May (1973)** - "Stability and Complexity in Model Ecosystems"
    - 正反馈导致不稳定

12. **Arthur (1989)** - "Competing Technologies, Increasing Returns"
    - **路径依赖 + 正反馈 = 锁定效应**
    - QWERTY 键盘、VHS vs Beta 的技术锁定

### 信仰/信念动力学
13. **Brams-Knowlton (1998)** - 博弈中的信念调整

14. **Page (2007)** - "Understanding Diversity in Opinion Dynamics"

---

## 三、查重分级系统

### 理论 Novelty 评估
| 级别 | 定义 | 贡献定位 |
|------|------|----------|
| **N0** | 已有完整数学模型 | 重新表述/新应用场景 |
| **N1** | 有直觉框架但缺形式化 | 数学严谨化 |
| **N2** | 部分定理已证明 | 扩展到新领域 |
| **N3** | 无直接先验工作 | 原创理论贡献 |

### D45 预估 Novelty 级别
- **D45-A (S形增长)**: N0 — Schelling(1971), Arthur(1989) 都有类似逻辑斯谛增长
- **D45-B (相变阈值)**: N1 — Schelling 阈值模型是定性框架，但你的正反馈 + 信念相变组合有 N2
- **D45-C (干预抑制)**: N2 — 有相关研究但数学形式化较少
- **D45-D (记忆持久性)**: N1 — 指数衰减是标准建模假设

### 建议论文贡献声明
> "We unify Schelling's threshold model with dynamical systems theory to provide a rigorous mathematical characterization of self-fulfilling prophecy dynamics, including phase transition analysis and intervention effectiveness bounds."

---

## 四、检索关键词清单

### 英文关键词（优先级排序）
```
Level 1 (核心):
- "self-fulfilling prophecy" mathematical model
- Schelling threshold model 1971
- coordination game evolutionary dynamics Kandori
- belief aggregation consensus formation

Level 2 (扩展):
- positive feedback social dynamics
- agent threshold model cascade
- opinion dynamics heterogeneous agents
- path dependence increasing returns Arthur

Level 3 (交叉):
- chimera state sociology coordination
- order parameter belief alignment
- symmetry breaking social behavior
- bifurcation theory opinion polarization

中文关键词:
- 自证预言 数学模型
- 社会动力学 正反馈
- 阈值模型 集体行为
- 意见动力学 一致性
- 协调博弈 演化稳定
```

### GitHub 工具检索
```
- "chimera state" synchronization (已有优秀库：parchment, kuramoto 等)
- "opinion dynamics" simulation
- "evolutionary game theory" python
- "phase transition" social simulation
- "network coordination" equilibrium
```

---

## 五、后续操作指南

### 当 Web 搜索可用时
1. 对每个新理论执行 Level 1 + Level 2 关键词检索
2. 记录 arXiv ID、引用数、关键论文链接
3. 更新本文档的文献清单
4. 评估 novelty 级别是否需要调整

### Novelty 降级处理
如果发现新理论与已有工作高度重合：
- **N3→N2**: 调整贡献定位，强调应用场景差异
- **N2→N1**: 转向 methodology improvement
- **N1→N0**: 考虑合并到现有理论，或寻找未被覆盖的边界条件

---

*此框架应在每次理论开发前查阅，并在理论完成后更新查重结果*
