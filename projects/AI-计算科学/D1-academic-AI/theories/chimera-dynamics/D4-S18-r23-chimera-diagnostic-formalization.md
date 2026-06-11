# D4-S18-r23：Chimera vs 梯度锁相 — 形式化区分与诊断协议

**日期**：2026-05-04
**依赖**：D4-S18-r22（梯度锁相发现），D4-S18-r22+（时间涨落测试）
**状态**：诊断协议提出（待实证验证）

---

## 问题陈述

D4-S18-r22 的发现暴露了一个理论层面的定义危机：

> **现象描述**（局部同步区 + 局部失步区）是 chimera 的*结果特征*，而非*机制特征*。
>
> 频率梯度同样通过不同机制产生相同现象，称为**梯度锁相（gradient-locking）**。

**理论危机**：如果两个不同物理机制产生相同观测现象，需要建立**机制诊断协议**来区分它们。

---

## 理论区分框架

### 定理 D4-S18-r23-T1：梯度锁相的存在性

**命题**：考虑 Kuramoto 模型，当耦合为均匀但存在频率梯度 ωᵢ = ω₀ + g·sin(2πi/N) 时，系统在 K > Kᶜ 条件下必然产生**准稳态区域锁定**。

**证明框架**：
1. 频率梯度在 i/N ≈ 0 和 i/N ≈ 1 处产生局部频率匹配
2. 耦合使频率匹配区域形成局部同步（平均场效应）
3. 频率梯度中心 i/N ≈ 0.5 处频率差异最大 → 局部失同步
4. 结果：两个同步区 + 一个失同步区 = 视觉上的 chimera-like 结构

**稳态稳定性判据**：
$$\left|\frac{d\theta_i}{dt} - \omega_i\right| \rightarrow 0 \implies \text{锁定到频率}, \text{不是 chimera 动力学}$$

---

### 定理 D4-S18-r23-T2：真实 Chimera 的机制特征

**定义（修正版）**：纯空间耦合驱动的真实 chimera 必须满足：

$$\mathcal{M}_{\text{chimera}} \equiv \nexists \omega: \quad \frac{d\theta_i}{dt} - \omega_i \not\approx \text{const.} \quad \text{(相变持续发生)}$$

**核心区别**：
| 特征 | Chimera | 梯度锁相 |
|------|---------|----------|
| 时间角色 | 持续局部同步切换 | 稳定锁定 |
| 空间角色 | 空间耦合定义同步边界 | 频率梯度定义分布 |
| 相干性演化 | 涨落（即使缓慢） | 单调收敛到稳态 |
| N 缩放 | 涨落幅度 ∝ N⁻¹/⁴ | 涨落幅度 ∝ N⁻¹/² |

---

### 定义 D4-S18-r23-D1：Chimera 诊断不变量

**1. 空间相干窗口不变量（SCI）**

$$\text{SCI} = \frac{\sigma_{\text{spatial}}}{\mu_{\text{spatial}}}$$

其中 $\sigma_{\text{spatial}}$ 是相邻空间扇区间同步率的方差，$\mu_{\text{spatial}}$ 是其均值。

- SCI ≈ 0.3（梯度锁相，均匀分布）
- SCI > 0.8 或 < 0.1（真实 chimera，区域化同步）

**2. 时间涨落诊断（TFD）**

$$\text{TFD}(t_1, t_2) = \frac{1}{T} \int_{t_1}^{t_2} \left\| \frac{d}{dt} \mathcal{R}(t) \right\|^2 dt$$

其中 $\mathcal{R}(t)$ 是时空同步率场。

- TFD ≈ 0（梯度锁相，稳态锁定）
- TFD > 0（真实 chimera，有动力学）

**3. 机制纯度指数（MPI）**

$$\text{MPI} = 1 - \frac{|\text{TFD} - \text{TFD}_{\text{lock}}|}{\max(\text{TFD})} \times \frac{|\text{SCI} - \text{SCI}_{\text{lock}}|}{\max(\text{SCI})}$$

- MPI > 0.8：高置信度 chimera
- MPI < 0.3：梯度锁相主导
- 0.3 < MPI < 0.8：混合效应

---

## 诊断协议

### 协议 D4-S18-r23-P1：双阶段 chimera 认证

```
阶段1：预筛（实时）
    计算 S = max(segment_sync) - min(segment_sync)
    if S < 0.2: 标记为 "全局态（非chimera）"
    else: 进入阶段2

阶段2：机制诊断（验证）
    步骤1：收集 T 步时间窗口数据
    步骤2：计算 TFD — 时间涨落
    步骤3：计算 SCI — 空间分布均匀性
    步骤4：计算 MPI — 机制纯度
    结论：
        MPI > 0.8 → "Chimera (纯耦合驱动)"
        MPI < 0.3 → "Gradient-Locking"
        else → "混合态（需分析）"
```

### 参数约束

**基于 r22 时间涨落测试的发现**：
- N ≥ 500 时 chimera 涨落可能太小无法检测
- **推荐**：T > 50000 时间步 + 耦合 g < 0.1 以增强涨落可见性
- **或者**：接受 MPI > 0.6 的扩展 chimera 定义

---

## 与 D9 框架的新连接

### 理论命题：梯度锁相 = 分布式表征

在 D9-II 选择压力框架下：
- **梯度锁相态**：信息通过频率梯度进行编码
- **Chimera 态**：信息通过空间聚类进行编码
- **统一观点**：两种都是"表征结构的涌现"

**D9 连接**：两种机制都满足 $\mathcal{C}_4$（结构性表征）— 但结构类型不同：
- 梯度模式：连续编码（有序）
- chimera 模式：离散编码（聚类）

---

## 预期输出

- [ ] 理论文档：本文件
- [ ] 实验代码：`labs/simulations/chimera_diagnostic_v2.py`（包含双阶段协议）
- [ ] 实验数据：`chimera_diagnostic_results.json`
- [ ] 论文框架更新：D4-S18 理论章节扩展

---

*D4-S18-r23 是 r22 发现的形式化理论响应。*
*完成时间：2026-05-04 | 轮次：r01*
