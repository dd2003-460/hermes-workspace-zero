# 02-goal-definition — Iteration 32: 整合手征引力波计算解析 ORF

> **Goal Definition Output**
> **Iteration**: 32
> **Input**: 01-clarification.md (Iteration 32)

---

## 1. 验收标准 (Acceptance Criteria)

所有验收标准必须可验证、可量化。

### AC-1: 共面网络 Gamma^V = 0

**验证方法**：数值积分测试，两个相同的 coplanar 等边三角探测器（arm length $L = 2.5\,\text{Gm}$，同一平面内）：

$$|\Gamma^V(f = 0.01\,\text{Hz})| < 10^{-6}$$

- **验收数值**：$|\Gamma^V| < 10^{-6}$
- **测试频率**：$f = 0.01\,\text{Hz}$（低频，小臂近似范围）
- **积分精度**：$N_\theta = 128, N_\phi = 256$
- **通过条件**：满足以上不等式

### AC-2: 非共面网络 Gamma^V 可探测

**验证方法**：LISA ($i = 60^\circ$) × Taiji ($i = 0^\circ$) 交叉相关：

- **sky-averaged**：$|\langle \Gamma^V \rangle| > 10^{-3}$
- **sky-max normalized**：$0.01 \leq |\Gamma^V|_{\max}^{\text{norm}} \leq 1.5$
- **测试频率**：$f = 0.01\,\text{Hz}$

Sky-max normalized 的定义为：

$$|\Gamma^V|_{\max}^{\text{norm}} = \max_{\hat{n}} \frac{|F_1^+(\hat{n})F_2^\times(\hat{n}) - F_1^\times(\hat{n})F_2^+(\hat{n})|}{\sqrt{\sum_A |F_1^A(\hat{n})|^2 \sum_A |F_2^A(\hat{n})|^2}}$$

- **通过条件**：sky-max 在 $[0.01, 1.5]$ 范围内
- **Orlando 2021 参考**：从 arXiv:2011.07059 Figure 5 读出 $|\Gamma^V|_{\max} \sim 0.3$（近似值，范围 $[0.01, 1.5]$ 覆盖 convention 差异）

### AC-3: Gamma^I 与现有验证代码一致性

**验证方法**：共面网络（$i_1 = i_2 = 0^\circ$，相同 constellations）的 $\Gamma^I(f)$ 对比：

$$\frac{|\Gamma^I_{\text{analytical}}(f) - \Gamma^I_{\text{numerical}}(f)|}{|\Gamma^I_{\text{numerical}}(f)|} < 5\%$$

- **验证频率点**：$f \in \{0.001, 0.005, 0.01, 0.05, 0.1\}\,\text{Hz}$
- **参考代码**：`scripts/01-olc-orf-solver.py`（已验证的 OLC ORF solver，QC PASS）
- **通过条件**：所有 5 个频率点相对误差 $< 5\%$

### AC-4: 解析解与数值积分一致性

**验证方法**：对于倾斜网络（LISA×Taiji），在以下频率点对比解析解与高精度数值积分：

$$\frac{|\Gamma_{\text{analytical}}(f) - \Gamma_{\text{numerical}}(f)|}{|\Gamma_{\text{numerical}}(f)|} < 5\%$$

- **频率范围**：$f \in [0.001, 0.1]\,\text{Hz}$（$fL/c < 0.1$，小臂近似有效）
- **数值积分网格**：$N_\theta = 256, N_\phi = 512$（高精度参考）
- **通过条件**：$\Gamma^I$ 和 $\Gamma^V$ 在所有频率点相对误差 $< 5\%$
- **超出范围标注**：如果 $fL/c > 0.1$ 时误差增大，应在输出中明确标注小臂近似的适用边界

### AC-5: 三重标量积几何论证

**验证方法**：解析证明 $\Gamma^V_{ij} \propto (\hat{n}_{1,i} \times \hat{n}_{2,i}) \cdot \hat{d}_{ij}$，其中 $\hat{n}_{m,i}$ 为探测器 $m$ 的某个参考臂方向，$\hat{d}_{ij}$ 为探测器连线方向。

- **通过条件**：推导过程中明确展示：
  - (a) 在共面情况下，$(\hat{n}_{1} \times \hat{n}_{2})$ 垂直于 $\hat{d}$ → 三重积为零
  - (b) 在非共面情况下，三重积非零
  - (c) 比例常数的显式表达式

### AC-6: 产出代码通过全部测试

**验证方法**：运行验证脚本 `scripts/verify-chiral-orf-analytical.py` 的 `--tests` 模式：

```bash
python3 scripts/verify-chiral-orf-analytical.py tests
```

所有测试用例必须 PASS：
- Test 1: 共面网络 self-correlation $\Gamma^V \approx 0$
- Test 2: 非共面网络 (LISA×Taiji) $\Gamma^V \neq 0$ 且 sky-max 在合理范围
- Test 3: 解析 vs 数值一致性（至少 3 个频率点）
- Test 4: 小臂近似边界测试

---

## 2. 质量要求

### Q-1: 公式推导完整性

- 所有公式必须从第一性原理推导，不跳步
- Hu I1-I4 框架的留数计算必须显式展示五个极点的留数求和
- OLC sinc 转移函数的极点结构必须明确分析
- JCAP $\Gamma^I$ 和 $\Gamma^V$ 的分解必须与 Hu 框架兼容地展示

### Q-2: 代码可读性

- 每个函数必须有清晰的 docstring（输入、输出、物理含义）
- 物理常数和单位必须明确标注（SI 单位制）
- 关键步骤必须有 inline 注释引用公式编号（如 "Hu Eq.(24)"）

### Q-3: 可复现性

- 脚本必须可在标准 Python 3.9+ / NumPy 环境下运行
- 不依赖未公开发布的代码库
- 所有测试用例的运行时间应 $< 60\,\text{s}$（高精度积分）

### Q-4: 物理一致性检查

- [ ] $\Gamma^I(f = 0) = \text{constant}$（低频极限下 ORF 为几何常数）
- [ ] $\Gamma^V(f = 0) = 0$（低频极限下宇称奇 ORF 为零，因为反平行）
- [ ] $\Gamma^I$ 关于探测器交换对称：$\Gamma^I_{ij} = \Gamma^I_{ji}$
- [ ] $\Gamma^V$ 关于探测器交换反对称：$\Gamma^V_{ij} = -\Gamma^V_{ji}$
- [ ] 共面网络的自相关 $\Gamma^V_{ii} = 0$

---

## 3. 硬约束 (Hard Constraints)

1. **必须使用 OLC sinc 转移函数**（Lou Eq.2-30），不能使用 Hu 的指数形式
2. **必须使用 JCAP 的 $\Gamma^I / \Gamma^V$ 分解**（Eq.2.9），不能用 Orlando 的 $R^R / R^L$ 直接定义
3. **必须通过共面 $\Gamma^V = 0$ 测试**（$< 10^{-6}$），这是物理正确性的最低门槛
4. **必须包含 Hu I1-I4 留数定理框架**，不能只做数值积分
5. **小臂近似结果必须显式给出解析公式**，不能只是数值拟合
6. **归一化约定**：使用 $1/4\pi$（JCAP convention），与 Lou 论文一致
7. **RALPH Loop 规则**：必须经 1-loop(6 阶段) → 2-loop(6 阶段)，Commander 不亲自写代码

---

## 4. 灵活部分 (Flexible Parts)

### F-1: 天线变量选择

- 可以使用 Michelson-like 变量或 TDI E-variable
- E-variable 的 detector tensor 计算方法可以更精确（比 CW sum 方法物理上更正确）
- 最终应优先使用 detector tensor 方法，因为 CW sum 方法在等边三角形上有 $R_\times \approx 0$ 的物理问题

### F-2: 频率扫描范围

- 验证脚本应至少在 $[0.001, 0.1]\,\text{Hz}$ 范围运行
- 可选扩展至 $[0.001, 1.0]\,\text{Hz}$ 以探测小臂近似失效点
- 超出小臂近似范围（$fL/c > 0.1$）的结果应标记为"近似可能失效"

### F-3: 探测器构型

- 基准测试使用 LISA×Taiji（倾斜 60°）
- 可选额外测试：OLC×Taiji（不同倾角）、三星座网络等
- 这些额外测试不作为验收标准，但有助于增加置信度

### F-4: 输出格式

- 解析公式笔记可以包含 LaTeX 源文件或 Markdown（推荐 Markdown，带 MathJax 渲染）
- 验证脚本可以输出文本报告或生成可视化图表
- 输出格式以"可验证"为最高优先级

---

## 5. 交付物清单

| # | 交付物 | 路径 | 验收方式 |
|---|--------|------|---------|
| D1 | 解析推导笔记 | `note/P-chiral-orf-analytical.md` | 公式完整性审查 |
| D2 | 验证脚本 | `scripts/verify-chiral-orf-analytical.py` | 通过所有 `--tests` |
| D3 | 可视化图表 | `figures/chiral-orf-*.png`（可选） | 物理合理性判断 |
| D4 | 总结报告 | `note/P-chiral-orf-summary.md` | AC 逐项检查清单 |

---

## 6. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| sinc 函数的留数计算比 Hu 指数形式复杂得多 | 中 | 高 | 如果无法解析求和，至少在小臂近似下给出解析结果 |
| 小臂近似误差超过 5% | 低 | 中 | 明确标注近似边界，额外提供中间阶近似 |
| Orlando 2021 benchmark 值因 convention 差异无法直接对比 | 中 | 低 | 使用 sky-max normalized 作为不变量比较 |
| TDI E-variable 的 detector tensor 定义在文献中不统一 | 中 | 中 | 采用 Green & Gair (2013) 的统一定义 |
| JCAP $\Gamma^V$ 定义中的比例常数不明确 | 低 | 低 | 通过 JCAP Eq.(2.9-2.10) 直接推导，不引用额外文献 |
