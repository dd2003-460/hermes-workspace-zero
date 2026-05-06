# D2-1 实验验证设计

## 核心目标

检验定理1和定理2的可观测预测：
- **P1**：规划成功率 vs 模型规模 — 阶梯函数而非S形曲线
- **P2**：$d_c$ vs 任务空间维度 — 幂律关系
- **P3**：Grokking延迟 $\tau$ vs 容量缺口 — 幂律发散
- **P4**：中间层表征的任务区分度 — 在 $d_c$ 处跃迁

---

## 实验1：规划能力阶梯函数检验（验证P1）

### Benchmark选择
**推荐**：**C-Bench (Chain-of-Thought Benchmark)** 或 **PlanningBench v2**
- C-Bench：覆盖逻辑推理、数学规划、代码生成三类任务
- PlanningBench v2：专门针对多步规划（Sudoku、Tower of Hanoi变体）

### 实验设计
```
变量：
- X轴：模型参数量 |A| ∈ {7B, 13B, 34B, 70B, 175B}（或内部模型缩放）
- Y轴：规划任务成功率 p_success(|A|, t)

控制变量：
- 固定提示模板（避免prompt variation）
- 固定任务难度分布
- 每个任务 ≥ 100次采样

预期结果：
- 若定理成立：p_success(|A|) ≈ step((|A| - d_c)/σ)
- 对比标准S形：sigmoid(|A|/T) — 检验sharpness差异
```

### 统计检验
- **Kolmogorov-Smirnov test**：阶梯分布 vs S形分布拟合优度
- **Change-point detection**：估计 $d_c$ 及其不确定性

---

## 实验2：任务维度与临界规模关系（验证P2）

### 任务集构造
构建不同维度的任务空间 $\mathcal{T}_d$：

| 维度 d | 定义 | 示例任务集 |
|--------|------|------------|
| d=1 | 单步决策 | Binary choice |
| d=2 | 两因素组合 | A×B task pairs |
| d=k | k-ary product | Cartesian product of k base tasks |

### 实验设计
```
1. 对每个维度 d，独立估计 d_c(d)（通过实验1的方法）
2. 拟合关系：d_c(d) = k · d^(1/α) + b
3. 预期：α ∈ [0.5, 1]（由定理2给出）
```

### 关键验证
- **线性化检验**：log(d_c) vs log(d) 的斜率 = 1/α
- **残差分析**：检验幂律拟合的R²

---

## 实验3：Grokking延迟与容量缺口（验证P3）

### 方法
训练小型规划Agent，系统变化参数：

```python
# Pseudocode
for d in parameter_range:  # 模型规模
    for t_max in training_steps:
        train(agent(d), tasks, steps=t_max)
        record(grokking_time(d))  # L_train converged but L_test not yet

# 拟合：τ(d) = C · (d_c - d)^(-γ) for d < d_c
```

### 数据收集
- **训练曲线**：L_train(t), L_test(t) 随时间演化
- **Grokking点**：L_test首次低于阈值的时间 t_grokk
- **容量缺口**：Δd = d_c - d

### 统计检验
- **幂律拟合**：log(τ) vs log(d_c - d)，预期斜率 = γ > 0
- **临界慢化**：在 d → d_c⁻ 时，τ 的发散行为

---

## 实验4：中间层表征跃迁（验证P4）

### 测量方法
使用**线性探针**量化中间层表征的任务区分度：

```python
# 对于每个隐藏层 h_i:
probe_h = LinearRegression()
probe_h.fit(features(X, layer=h_i), task_labels)
accuracy_h = probe_h.score(test_features, test_labels)

# 预期：accuracy_h(d) 在 d ≈ d_c 处出现不连续跃迁
```

### 额外分析
- **t-SNE可视化**：观察 d < d_c vs d > d_c 时任务表征的聚类结构变化
- **Canonical Correlation Analysis (CCA)**：量化不同规模模型间表征的相似度

---

## 实验优先级与资源需求

| 实验 | 优先级 | GPU需求 | 时间估计 | 风险等级 |
|------|--------|---------|----------|----------|
| E1: 阶梯函数 | P0（立即可做） | A100×4 (7B-13B) | 2周 | 低 — 可用API模型 |
| E4: 表征跃迁 | P0（立即可做） | A100×2 | 1周 | 低 — 需修改推理代码 |
| E3: Grokking延迟 | P1（需训练） | A100×8 | 4周 | 中 — 训练时间长 |
| E2: 维度关系 | P1（需设计） | A100×4 | 3周 | 中 — 任务集构造复杂 |

---

## 替代方案（无GPU资源）

### 使用开源模型API
- **Mistral 7B/13B**、**Llama 2/3** 系列 — 通过 Together.ai / Fireworks.ai
- **范围限制**：只能覆盖2-3个规模点，统计效力有限

### 使用轻量级任务集
- **MiniF2F**：数学证明任务（轻量，适合小规模实验）
- **ARC-AGI**：抽象推理挑战赛子集

### 使用表征分析工具
- **Mechanistic Interpretability** 库（Transformer Circuits）— 无需训练，分析已有模型

---

## 预期论文结构

1. **Introduction**：规划能力的信息瓶颈视角
2. **Theory**：定理1-3 + 证明（附录）
3. **Experiments**：E1+E4 作为核心验证，E2+E3 作为扩展
4. **Discussion**：与grokking、emergent abilities的关联

---
*设计完成: 2026-04-30 | Status: Ready for execution — E1 recommended as starting point*
