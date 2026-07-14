# Iteration 6: Triangular OLC Chiral ORF — 信息搜集调查报告

> 创建时间: 2026-07-05
> 状态: Investigation completed, 2-loop paper update in progress

---

## 子任务完成情况

### Task 1: OLC Michelson-like 变量天线方向图公式
**来源**: Hu PRD 111 (2025) + 通用 ORF 框架 + Iteration 5-6 代码

**关键发现**:
- OLC 测量单向频率偏移（非干涉仪相位差），传递函数为单臂形式
- Michelson-like 变量: $M = \text{link}(a) + \text{link}(b)$，其等效天线方向图为两条路径响应的线性叠加
- 天线方向图公式 $F_{+, \times}$ 与 PTA/LISA 形式相同，因为 GW-物质耦合是普适的
- **致命限制**: 对 Michelson-like 变量，$R_+^{(1)} / R_\times^{(1)} = R_+^{(2)} / R_\times^{(2)}$，使得手征因子 $R_+^{(1)} R_\times^{(2)} - R_\times^{(1)} R_+^{(2)}$ 严格为零

**置信度**: 0.95（物理论证 + 代码验证 + JCAP 理论一致）

### Task 2: LISA 三角配置手征 ORF 数值
**来源**: Chen-Liu-Zhang (JCAP 2025, arXiv:2410.18916)

**关键数值**:
- LISA-TAIJIm 对 (双三角网络): $V$ 分量灵敏度在低频处比 $I$ 分量好 $\sim 10$ 倍
- 最优轨道面夹角: $\sim \pi/2$ (近似正交)
- 共面网络 (LISA-TAIJIc): $V$ 响应为零（对称性）
- 单三角探测器: $\Gamma^V \to 0$ in low-frequency limit

**置信度**: 0.99（JCAP 为最权威来源，公式与数值均已提取）

### Task 3: Kato & Soda 2016 手征灵敏度讨论
**来源**: Phys. Rev. D 93 (2016) 062003, arXiv:1512.09139

**关键发现**:
- Kato & Soda 讨论了 LISA 三角配置对手征 SGWB 的灵敏度
- 核心结论: 单 LISA 三角对圆偏振背景有有限的手征响应
- **但注意**: JCAP 2025 进一步证明，当使用正确的 TDI 变量（A, E, T）进行交叉相关后，单三角的手征响应趋于零
- 这可能是因为 Kato & Soda 使用的变量定义与 JCAP 的 A/E/T 通道不同

**置信度**: 0.70（论文原文未完整获取，结论基于 JCAP 的引用和解读）

### Task 4: OLC 星座合成 ORF 方法
**来源**: Chen-Liu-Zhang (JCAP 2025, 2025), Hu PRD 111 (2025)

**关键发现**:
- 对于多探测器网络，Chen-Liu-Zhang 给出了通用的有效 ORF 公式:
  - $\hat{\gamma}_{\rm eff}^I = \sqrt{\sum_\alpha (\hat{\gamma}_\alpha^I)^2 - (\sum_{\alpha\beta} \hat{\gamma}_\alpha^I \hat{\gamma}_\beta^V)^2 / \sum_\beta (\hat{\gamma}_\beta^V)^2}$
  - $\hat{\gamma}_{\rm eff}^V = \sqrt{\sum_\alpha (\hat{\gamma}_\alpha^V)^2 - (\sum_{\alpha\beta} \hat{\gamma}_\alpha^I \hat{\gamma}_\beta^V)^2 / \sum_\beta (\hat{\gamma}_\beta^I)^2}$
- 几何因子 $X^V_{mn}$ 取决于各探测器的轨道面法向量和分离向量
- 对于单三角: 所有 $X^V_{mn}$ 相互抵消，$\Gamma^V = 0$
- 对于双三角: $X^V_{mn}$ 非零，有效手征响应可达显著水平

**置信度**: 0.85（公式完整，但 OLC 具体映射尚未实施）

---

## 可直接使用的公式

### 1. 手征 ORF 辅助张量 (JCAP Eq. 2.15)

$$\hat{I}_{abcd} = b_0(\hat{y}) \delta_{ac}\delta_{bd} + b_1(\hat{y}) \delta_{ac}s_bs_d + b_2(\hat{y}) s_as_bs_cs_d$$
$$\hat{V}_{abcd} = b_0^V(\hat{y}) w_{ac}\delta_{bd} + b_1^V(\hat{y}) w_{ac}s_bs_d$$
其中 $w_{bd} = \varepsilon_{bdc}s_c$

### 2. 球贝塞尔系数 (JCAP Eq. 2.16)

$$bI_0(\hat{y}) = 2j_0(\hat{y}) - \frac{10}{7}j_2(\hat{y}) + \frac{4}{7}j_4(\hat{y})$$
$$bI_1(\hat{y}) = j_2(\hat{y}) - j_4(\hat{y})$$
$$bI_2(\hat{y}) = j_4(\hat{y})$$
$$bV_0(\hat{y}) = 4j_1(\hat{y}) - j_3(\hat{y})$$
$$bV_1(\hat{y}) = 5j_3(\hat{y})$$
其中 $\hat{y} = 2\pi f r/c$

### 3. 手征几何因子 (JCAP Eq. 2.23)

$$X^V_{00} = \frac{1}{2}\cos^2 c\,(3 + \cos^2 c)$$
$$X^V_{01} = X^V_{10} = \cos a\cos b\cos c\,(2\sin^2 a + 2\sin^2 b + \sin^2 c) - \frac{1}{2}\cos^2 c\,(2\cos 2a + 2\cos 2b + \cos 2a\cos 2b + 1)$$
$$X^V_{11} = \sin a\sin b\sqrt{2\cos a\cos b\cos c + \sin^2 c}$$
其中 $a, b, c$ 为轨道面法向量之间的夹角

### 4. SNR 为手征探测 (JCAP Eq. 2.12)

$$\rho_I^2 = \frac{T_{\rm obs}}{42} \int_0^\infty df \left[\sum_\alpha (\hat{\gamma}_\alpha^I)^2 - \frac{(\sum_{\alpha\beta}\hat{\gamma}_\alpha^I\hat{\gamma}_\beta^V)^2}{\sum_\beta(\hat{\gamma}_\beta^V)^2}\right] \frac{I^2(f)}{\bar{N}^2}$$
$$\rho_V^2 = \frac{T_{\rm obs}}{42} \int_0^\infty df \left[\sum_\alpha (\hat{\gamma}_\alpha^V)^2 - \frac{(\sum_{\alpha\beta}\hat{\gamma}_\alpha^I\hat{\gamma}_\beta^V)^2}{\sum_\beta(\hat{\gamma}_\beta^I)^2}\right] \frac{V^2(f)}{\bar{N}^2}$$

---

## 置信度评估

| 要素 | 置信度 | 说明 |
|------|--------|------|
| 单三角 Michelson-like $\Gamma^V = 0$ | **0.95** | 物理论证 + 代码验证 + JCAP 理论一致 |
| 单臂非共面 $\vert\Gamma^V\vert$ 频率依赖 | **0.80** | 代码验证，但缺少网格收敛测试 |
| JCAP 公式的 OLC 适用性 | **0.70** | 公式正确，但 OLC 的 $D^{ab}$ 张量构造尚未明确 |
| 双三角网络 chiral 灵敏度 | **0.90** | JCAP 数值结果 + 文献引用充分 |
| Kato & Soda 结论 | **0.60** | 论文原文未完整获取 |

**Overall triangular OLC chiral ORF confidence: 0.70**
— The JCAP framework provides the complete formalism for multi-constellation chiral ORF. However, the specific mapping from OLC frequency-shift measurements to detector tensors $D^{ab}$ is not yet established.

---

## 遗留问题

1. **OLC 的 A/E/T 通道构造**: Michelson-like (X, Y, Z) 不是 JCAP 的 A/E/T 通道。如何用 OLC 单向链路构造 TDI-like 的 A/E/T 变量？这需要参考 LISA TDI 理论。

2. **单三角 vs 双三角手征灵敏度对比**: 论文草稿需要明确引用 JCAP 的双三角结果，而非使用推测性数字。

3. **Kato & Soda 2016 原文**: 如果他们的结论与 JCAP 不一致，需要在论文中调和。

4. **长波近似适用性**: OLC 臂长（m-Gm）对应的 $f_{\max} \approx c/(2\pi L) \sim 20$ mHz，远低于 LISA 的适用频率上限。需要在代码中验证长波近似的适用范围。

---

## 下一步

### 短期 (2-loop 剩余阶段)
- 论文草稿已更新，包含 Iteration 5-6 全部结果
- 无需进入 2-loop/03 代码执行

### 中期 (Iteration 7)
- 实现 Chen-Liu-Zhang 框架下的 OLC 多星座 chiral ORF 计算
- 核心步骤: (a) 定义 OLC 双星座的轨道几何参数，(b) 计算几何因子 $X^V_{mn}$，(c) 集成球贝塞尔函数，(d) 计算有效手征 ORF 和 SNR
- 目标: 验证 OLC-OLC 双星座在手征 SGWB 探测中的灵敏度

### 长期
- 与 Ganapathy et al. 2026 的协同观测框架整合
- 准备 arXiv 提交

---

## 相关引用

- Chen, Liu, Zhang (2025) "Chiral gravitational-wave detection with triangular detectors" JCAP 05(2025)050, arXiv:2410.18916
- Hu et al. (2025) "Universal overlap reduction functions for clock networks" PRD 111, 084065
- Kato & Soda (2016) PRD 93, 062003, arXiv:1512.09139
- Ganapathy et al. (2026) arXiv:2606.01516 (preprint)
- Schaffrath et al. (2025) trap suppression proof

---

last_updated: 2026-07-05
next_brain_sub: 继续 (Iteration 7: multi-constellation chiral ORF per JCAP)
