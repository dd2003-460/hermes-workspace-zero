# D32: Information-Theoretic Phase Transition — Bounds on Emergent Capability via Mutual Information

## 核心洞见

D31证明能力涌现是容量上的相变。D30-2用信息瓶颈证明CoT大小下界。D32将两者统一：**能力涌现的本质是互信息在模型内部层的重新组织（information bottleneck restructuring）**。

**定理**：对于涌现能力 $A$，存在临界互信息 $I_c$ 使得：
$$I(M; A) < I_c \implies \text{no emergence}, \quad I(M; A) \geq I_c \implies \text{emergence occurs}$$

其中 $I_c$ 与临界容量 $p_c$ 相关：$I_c = f(p_c)$。

## 形式化

### 定义 D32-1：信息瓶颈重组

设模型内部表示为 $Z_1, Z_2, \ldots, Z_L$（各层激活值）。定义：
$$\mathcal{I}_\ell(p) = I(X; Z_\ell) - I(Y; Z_\ell)$$
为第 $\ell$ 层的**信息瓶颈势**。

### 定义 D32-2：涌现临界信息

$$I_c = \inf \left\{ I \in \mathbb{R}^+ : \exists \ell, p > p_c \text{ s.t. } \frac{\partial \mathcal{I}_\ell}{\partial p} > 0 \text{ and } \frac{\partial^2 \mathcal{I}_\ell}{\partial p^2} < 0 \right\}$$

### 定义 D32-3：信息-容量对应原理

$$I_c(p) \sim p^\gamma \quad \text{at } p \to p_c$$

其中 $\gamma$ 是D31中的临界指数。

### 定理 D32-1：信息瓶颈相变

**假设**：
- (A1) 涌现能力 $A$ 需要至少 $k$ 步推理
- (A2) 每一步推理消耗至少 $I_{\mathrm{step}}$ 互信息
- (A3) 模型总可用互信息为 $I_{\mathrm{total}}(p) \sim \log p$

**则**：
$$p_c = \exp(k \cdot I_{\mathrm{step}} / c)$$
其中 $c$ 是模型效率常数（D30-2中的architecture constant）。

**解释**：临界容量由"信息需求 vs 信息供给"的平衡决定。模型必须积累足够的互信息来支持 $k$ 步推理。

### 推论 D32-1a：互信息阈值律

$$\exists I_c : I(M; A) < I_c \implies P(\text{emergence}) \approx 0, \quad I(M; A) > I_c \implies P(\text{emergence}) \approx 1$$

这解释了为什么涌现是"突然出现"——互信息达到阈值后，能力自动涌现。

### 推论 D32-1b：CoT的互信息下界

结合D30-2：
$$I(M; \mathcal{T}_{\mathrm{cot}}) \geq \mathcal{I}(\mathcal{T}_{\mathrm{cot}}; \mathcal{Q}) - \mathcal{I}(\mathcal{T}_{\mathrm{cot}}; \mathcal{D}_{\mathrm{train}} | M)$$

在 $p \to p_c^+$ 时，$I(M; \mathcal{T}_{\mathrm{cot}})$ 必须超过涌现阈值 $I_c$。

### 推论 D32-1c：深度-推理不等式

对于 $L$ 层模型：
$$I(X; Z_L) \leq L \cdot \max_\ell \left( \text{layer\_efficiency}_\ell \right)$$

深层模型必须更"信息高效"。如果任何层的效率低于临界值，涌现不会发生。

## 与现有D1论文的关联

| 论文 | 关联 |
|------|------|
| **D31** (Phase Transition) | D31定义 $p_c$；D32给出 $p_c$ 的互信息解释：$p_c$ 是互信息达到涌现阈值所需的容量 |
| **D30-2** (IB-CoT-Bound) | D30-2给出CoT bound；D32将此bound解释为涌现阈值 |
| **D29** (Scaling-Understanding) | D29指出大模型经验成功但理论不可解释；D32解释：因为大模型的互信息结构在 $p_c$ 处重组，小模型框架无法描述 |
| **DistCat** | 2-范畴框架可描述不同"信息相"之间的态射 |

## 实证验证协议

### D32-A：测量内部表示的互信息

训练不同大小的模型，估计各层 $I(X; Z_\ell)$ 和 $I(Y; Z_\ell)$。检测 $p_c$ 处的突变。

### D32-B：信息瓶颈势相变

追踪 $\mathcal{I}_\ell(p)$ 随容量的变化。检测相变点。

### D32-C：深度-推理不等式验证

测量不同深度模型的实际互信息效率，检验不等式。

## 相关文献

- Tishby & Zaslavsky (2015) - Information bottleneck
- Weng (2020) - Mutual information bounds
- Shwartz-Ziv & Tishby (2017) - Opening the black box: Neural training reveals IB
- Saxe et al. (2021) - Information bottleneck in deep learning
- Wei et al. (2022) - Emergent abilities
- Belkin et al. (2019) - Double descent
