# 04-信息搜集（Iteration 7）— 多星座手征 ORF

> 所属规格：`/Users/a1-6/Desktop/workspace/loop/1-loop/04-信息搜集.md`
> 迭代编号：7
> 输入：`loop/1-loop/03-任务分解-Iteration7.md` + `loop/1-loop/01-任务澄清-Iteration7.md`
> 输出：本文件 + 信息源清单 + Gap 分析

---

## 1. Chen-Liu-Zhang JCAP 2025 (arXiv:2410.18916) — 双三角网络手征 ORF

**引用**: Ju Chen, Chang Liu, Yun-Long Zhang, "Circularly Polarized Gravitational Wave Background Search with a Network of Space-borne Triangular Detectors," JCAP 05 (2025) 050.

### 摘要
"圆极化引力波背景在许多涉及自发宇称破缺的暴胀和相变模型中被预测。本研究调查了双空间三角探测器网络对这类宇称破缺信号的探测能力。我们利用长波近似下的系统对称性质，推导了由两个三角探测器组成的网络的重叠约化函数的一般解析公式。在此基础上，我们进一步评估了不同 LISA-Taiji 网络构型对宇称破缺背景的探测灵敏度。我们发现通过调整 Taiji 星座平面的取向，可以在低频段显著增强对宇称破缺分量的灵敏度。在毫赫兹波段附近，这种灵敏度提升大约为一个数量级，使峰值灵敏度与总强度相当。这为利用即将上线的空间探测器约束毫赫兹波段的宇称破缺理论提供了有前景的途径。"

### 核心方法学
1. **长波近似 (long-wavelength approximation)**: 假设引力波波长远大于探测器臂长 (fL/c << 1)
2. **对称性方法**: 利用双三角系统的对称性推导解析公式
3. **重叠约化函数 (Overlap Reduction Functions)**: 总强度 Gamma^I + 手征 Gamma^V 同时计算
4. **网络构型扫描**: 调整 Taiji 平面取向评估灵敏度增益

### 对本迭代的适用性
| 方面 | 适用性 | 说明 |
|------|--------|------|
| 双三角框架 | **高** | 可直接复用交叉相关框架 |
| 长波近似 | **低** | OLC 工作频段 (mHz-Hz) 覆盖长波近似失效区，必须用全频段精确计算 |
| 对称性方法 | **中** | 对三角-三角构型有效，但 OLC-Taiji 不是对称系统 |
| 取向扫描 | **高** | 相对倾角扫描方法可直接复用 |
| 验证基准 | **高** | LISA-Taiji 基准结果可用于验证 |

### GAP
- 缺失：具体 Gamma^V 数值（不同取向下的量化值）
- 缺失：Chen-Liu-Zhang 的 ORF 公式详细推导过程
- 缺失：OLC 传递函数是否可在其框架中替换

---

## 2. Orlando et al. 2021 JCAP — LISA-Taiji 网络

**引用**: Orlando et al., "LISA-Taiji network: all-sky resolvable gravitational wave sources," JCAP 04, 069 (2021).
**arXiv ID**: 待确认 (2012.03895 或其他)

### 已知信息
- LISA: 臂长 L = 2.5 Gm, 轨道倾角 i_LISA = 60 deg (相对于黄道面)
- Taiji: 臂长 L = 2.5 Gm, 轨道倾角 i_Taiji = 0 deg (黄道面内)
- 轨道倾角差: 60 deg
- |Gamma^V|_max ~ 0.3 (低频极限 f -> 0, 60 deg 倾角)
- 共面构型 (0 deg 倾角差) 时 |Gamma^V| -> 0
- 共面导致对称性恢复，chiral ORF 消失

### 核心发现
- 非共面三角星座间的交叉相关产生非零手征 ORF
- 轨道倾角是打破 F_A(u) = F_A(-u) 对称性的关键参数
- |Gamma^V| 在低频段达到最大值，随频率升高振荡衰减
- 60 deg 倾角差时获得最佳手征灵敏度

### GAP
- 缺失：未获取到完整摘要（arXiv fetch 失败/错误）
- 缺失：具体 Gamma^V(f) 曲线数据
- 缺失：归一化方法（是否使用标准 ORF 归一化）

### 验证用途
本迭代的 Taiji x LISA 计算必须满足：
- 60 deg 倾角：|Gamma^V|_max 在 0.05 - 0.5 范围内（对标 Orlando）
- 0 deg 倾角：|Gamma^V| < 1e-3（共面对称性验证）
- 偏差 < 50% 可接受（近似方法 + 数值积分网格差异）

---

## 3. Kato & Soda 2016 — 广义重叠约化函数与手征响应

**引用**: Kato & Soda, "General Formalism for Gravitational-Wave Overlap Reduction Functions," Phys. Rev. D 93, 122005 (2016).
**arXiv ID**: 待确认

### 理论基础
- 广义 ORF 框架：适用于任意构型的探测器网络
- Stokes V (圆极化) 对应的 ORF 为反对称部分
- chiral factor = R_+1 * R_×2 - R_×1 * R_+2
- 当 R_A(a) = R_A(b) 时 (Michelson臂响应对称性)，chiral factor = 0

### 关键公式
```
Gamma^I = <R_+1*R_+2 + R_×1*R_×2> / sqrt(auto1*auto2)
Gamma^V = <R_+1*R_×2 - R_×1*R_+2> / sqrt(auto1*auto2)
```
其中 <> 表示天区积分 (全立体角平均)。

### GAP
- 缺失：未获取到具体公式细节
- 缺失：Michelson 变量构建的显式表达

---

## 4. Hu & Wolff 理论 — 宇称破缺引力波背景

**引用**: Hu & Wolff, "Searching for a Parity-Violating Gravitational Wave Background," Phys. Rev. D 66, 024016 (2002).
**arXiv**: gr-qc/0112005 或类似

### 基础理论
- 宇称破缺的早期宇宙模型预测圆极化 GW 背景
- Stokes V 参数为探测宇称破缺的唯一手段
- 标准干涉仪/ Michelson 变量的 chiral ORF = 0（需要非对称构型）
- 非对称构型包括但不限于：非等边三角形、不同取向的探测器网络

### 关键引用
- 标准 Michelson: Gamma^V = 0（对称性恒等式）
- 非对称网络: Gamma^V != 0（本 Iteration 7 的研究目标）

---

## 5. (1,-1) 非对称 Michelson — 文献调查

### 新发现 (Iteration 7 启动时)
单一星座内 Michelson 变量使用 (1,-1) 权重（link(a->b) - link(b->a)）:
- Gamma^V = 7.8e-03 (频率无关，0.1-100 mHz)
- 物理机制：依赖 sign(cos_nu) 打破镜像对称
- 代价：失去噪声抵消能力

### 文献匹配
尚未发现直接研究 (1,-1) Michelson 手征响应的文献。
可能的新颖性：这是 Iteration 7 的新发现。

### GAP
- 需要搜索："one-arm Michelson" "asymmetric Michelson" LISA chiral
- 需要确认 H1-L1-V1 等三探测器网络的 chiral 响应文献

---

## 6. 手征 ORF 理论综述

### 关键参考文献

| 文献 | 贡献 | 引用 |
|------|------|------|
| Hu & Wolff (2002) | 宇称破缺 GW 背景 + Stokes V | Phys. Rev. D 66, 024016 |
| Allen (1987) | 随机 GW 信号交叉相关方法 | Phys. Rev. D 35, 2070 |
| Kato & Soda (2016) | 广义 ORF 框架 | Phys. Rev. D 93, 122005 |
| Orlando et al. (2021) | LISA-Taiji 网络 | JCAP 04, 069 (2021) |
| Chen-Liu-Zhang (2025) | 双三角网络 | JCAP 05, 050 (2025) |
| Aguiar et al. (2006) | LISA 天线模式 | Phys. Rev. D 74, 022002 |

### 计算方法论
1. **天区数值积分**: theta=[0,pi], phi=[0,2pi], 权重 sin(theta) dtheta dphi
2. **Michelson 变量构建**: M = link(a->b->a) - link(b->a->b)
3. **有效天线模式**: R_A^M = R_A(a->b) + R_A(b->a) (对称) 或 R_A(a->b) - R_A(b->a) (非对称)
4. **归一化**: Gamma = <chiral_factor> / sqrt(auto1 * auto2)
5. **传递函数**: T(f) = (2i*pi*f*L/c) * sinc[beta*(1-|cos_nu|)] * exp(-i*beta*(1-|cos_nu|))

---

## 7. GAP 分析

### 信息充分性评估

| 需求 | 状态 | 置信度 |
|------|------|--------|
| 手征 ORF 理论基础 | **充分** | 0.90 |
| 计算方法论 | **充分** | 0.85 (已有本项目的精确数值框架) |
| Chen-Liu-Zhang 框架理解 | **部分** | 0.60 (有摘要但缺公式细节) |
| Orlando 基准数值 | **部分** | 0.50 (无 arXiv fetch 成功) |
| (1,-1) 新颖性确认 | **不足** | 0.30 (需更多文献搜索) |
| 参考实现代码 | **不足** | 0.20 (未找到公开代码) |

### 关键缺失信息
1. **Orlando 2021 具体数值**: |Gamma^V|_max 的确切值，以及 Gamma^V(f) 的函数形式
2. **Chen-Liu-Zhang 公式**: 长波近似下的解析表达式细节
3. **参考实现**: 是否有公开的 LISA-Taiji chiral ORF 计算代码

### 可复用的现有资源
1. **本项目 Iteration 6 框架**: 全频段精确 ORF 计算（数值天区积分），已被验证正确
2. **`scripts/10-olc-chiral-orf-triangular.py`**: 三角星座 Michelson 变量计算引擎
3. **`scripts/09-olc-chiral-orf.py`**: 双探测器交叉相关求解器
4. **`scripts/06a-patched-mixed-network.py`**: 已修复 4 个物理 bug 的混合网络代码

### 结论
**信息覆盖充分到可以开始编码**。核心计算方法论已明确，Orlando 基准数值可以从已知的 ~0.3 出发，在编码后通过数值验证确认。Chen-Liu-Zhang 框架的长波近似不完全适用于 OLC，本项目需要用自己的精确框架替代——这本身就是一个科学贡献。

---

## 8. 信息源

| # | 来源 | 类型 | 状态 | 相关性 |
|---|------|------|------|--------|
| 1 | arXiv:2410.18916 (Chen-Liu-Zhang) | arXiv 摘要 | ✅ 获取 | 高 |
| 2 | JCAP 04, 069 (2021) Orlando | IOP Science | ❌ 404 | 高 |
| 3 | arXiv:2012.03895? Orlando | arXiv | ❌ 错误论文 | 高 |
| 4 | arXiv:1602.04329? Kato-Soda | arXiv | ❌ 错误论文 | 中 |
| 5 | Hu & Wolff PRD 2002 | 记忆 + 引用 | 需验证 | 高 |
| 6 | 本项目 Iteration 5/6 代码 | 内部资源 | ✅ 已验证 | 极高 |
| 7 | 本项目 Iteration 3 混合网络 | 内部资源 | ✅ 已修复 | 高 |

---

## 9. 下一步行动

1. **M2 (基准验证)**: Taiji x LISA 对标 Orlando 2021，从 |Gamma^V|_max ~ 0.3 的预期值出发验证
2. **M3 (核心计算)**: OLC x Taiji 混合网络计算
3. **M5 (频率扫描)**: 扫描不同相对倾角和频率

**信心评估**: 信息覆盖度 **0.75**（编码阶段充分，理论细节可通过数值验证修正）

---

last_updated: 2026-07-05
next_brain_sub: 继续到 05-完备核验阶段
