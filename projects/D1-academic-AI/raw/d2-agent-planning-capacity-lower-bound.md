# D2-1: Agent规划能力的信息瓶颈下界

## 来源
转化自：
- raw/ai_information_theory_optimization.md (4): Agent自主完成工程的完整计划
- raw/ai_information_theory_optimization.md (5): Agent规划能力检验

## 核心猜想

**Agent规划容量的信息论下界（猜想）**：设 $A$ 为具备规划能力的Agent，任务空间为 $\mathcal{T}$，动作序列长度为 $L$。定义**规划信息**：

$$I_{plan} = I(\text{plan}; \mathcal{T}, y_{target})$$

**猜想**：若 $|A| < I_{plan}^* + \delta_{margin}$（其中 $\delta_{margin} \approx 10\%$ 为"推理冗余预算"），则Agent无法完成 $(L, |\mathcal{T}|)$ 级别的规划任务。

## 关键洞察

这与D9-I中"冗余预算"的概念一致——但**专门针对规划能力给出定量下界**。

区别于标准的信息瓶颈：
- 标准IB关注 $X \to Z \to Y$（感知→表征→输出）
- **规划IB**关注 $\mathcal{T} \to \text{plan} \to \text{action\_sequence}$

**规划信息** $I_{plan}$ 的特殊性：
1. **递归结构**：规划本身可以包含子规划
2. **反事实依赖**：规划需要评估"如果做了A会怎样，那么做B会更好"
3. **时间延展**：规划信息跨越多个决策步骤

## 可验证性

1. **模型规模扫掠**：在不同规模的GPT模型上测试规划任务的可解阈值
2. **任务复杂度控制**：固定Agent规模，变化任务描述长度 $L$ 和动作空间 $|\mathcal{T}|$
3. **信息瓶颈拟合**：估计实际 $I_{plan}$ 与模型参数量的关系

## 理论延伸

**猜想2（规划能力的相变）**：存在一个**临界规模** $|A|_c$，当 $|A|$ 接近此值时，规划能力出现**不连续跃迁**——从"机械执行"到"自主规划"。

这与grokking现象有相同的数学结构。

## 方法论问题

1. $I_{plan}$ 如何从实证数据中估计？（需要逆信息瓶颈方法）
2. $\delta_{margin}$ 是否依赖于任务领域的结构化程度？
3. 是否存在一个"元规划容量"——Agent能否学会如何更好地规划？

---
*Created: 2026-04-29 | Status: Conjecture — Requires agent benchmarking at scale*
