# 02-目标澄清（Iteration 8）— 三角形 3 卫星 OLC 手征 ORF 物理分析 + 深度非共面构型

**所属规格**：`/Users/a1-6/Desktop/workspace/loop/1-loop/02-目标澄清.md`
**状态**：in-progress
**输入**：loop/1-loop/01-任务澄清-Iteration8.md
**输出**：本文件 + 内嵌验收标准

---

## 阶段目标

在 Iteration 6 严格证明三角 OLC Michelson-like 变量手征 ORF = 0、Iteration 7 验证多星座混合网络交叉相关实现 |Gamma^V| ~ 1.0 的基础上，探索**单三角形 OLC 星座通过"深度非共面构型"实现可探测 Gamma^V**的可能性。

**核心问题**：一个单三角形 OLC 星座（无需多星座交叉相关）能否通过非共面构型获得非零手征 ORF？其物理起源与多星座交叉相关是否相同？

**具体目标**：

1. 计算**共面三角形 E 变量 (CW sum) 的 Gamma^V**，严格验证镜面反射对称性导致 Gamma^V = 0
2. 构造**非共面三角形构型**（高度差、不等臂、倾斜平面）并使用 E 变量计算 Gamma^V(f)
3. 扫描非共面参数空间，建立 **|Gamma^V| 与非共面度量** 的定量关系（倾斜角/高度差/边长比）
4. 将深度非共面单三角 OLC 的 Gamma^V 与多星座交叉相关结果直接比较
5. 分析高频极限下传递函数相位因子对 F_A(u) = F_A(-u) 对称性的破坏

---

## 期望结果

### 必须产出（Iteration 8 完成标志）

1. **非共面参数扫描数值表**：对至少 6 组非共面构型（见参数扫描表）给出 Gamma^V(f) 在关键频率点的值
2. **|Gamma^V| vs 非共面度量关系曲线**：在 1 mHz — 100 Hz 范围内展示 |Gamma^V| 随非共面参数的变化趋势
3. **共面 E 变量零检验图**：验证共面情况下 E 变量 Gamma^V < 1e-10
4. **深度非共面 Gamma^V 极值图**：找到 |Gamma^V|_sky_max 最大的构型，标注其参数和数值
5. **与多星座结果的比较图**：单三角非共面 vs LISA x Taiji 的 |Gamma^V| 量级对比

### 理论目标

1. **确认或否定**：单三角非共面能否实现 |Gamma^V| > 1e-3（可探测阈值）
2. **量化最优构型**：给出达到最大 |Gamma^V| 的非共面参数组合
3. **物理起源对比**：确认单三角非共面与多星座交叉相关的 Gamma^V 是否共享同一对称性破缺机制

---

## 判定标准

### 必须满足（Pass/Fail）

| # | 判定标准 | 通过条件 | 类型 |
|---|---------|---------|------|
| P1 | **共面 E 变量零检验** | 共面等边三角形的 E 变量 Gamma^V < 1e-10 | 硬约束 |
| P2 | **非共面 E 变量非零检验** | 至少一种非共面构型的 Gamma^V > 1e-3 (f > 10 mHz) | 硬约束 |
| P3 | **可探测极值** | 找到至少一种构型使得 |Gamma^V|_sky_max > 0.01 | 硬约束 |
| P4 | **几何-响应关系** | 建立 |Gamma^V| 与几何参数（倾斜角/非共面度）的定量关系（线性或二次拟合，R^2 > 0.5） | 硬约束 |
| P5 | **高频极限** | 单臂非共面链路对在 f >> c/L 时 |Gamma^V| > 1.0（与 Iteration 6 已知结果 K3 一致） | 硬约束 |
| P6 | **网格收敛** | ntheta=32→64 时，|Gamma^V| 变化 < 10% | 硬约束 |
| P7 | **Michelson 零检验** | 任意非共面三角形的 Michelson 变量 Gamma^V = 0（与 Iteration 6 结果一致） | 硬约束 |
| P8 | **频率扫描覆盖** | 频率范围 1 mHz 到 100 Hz，log-spaced，至少 20 个点 | 硬约束 |

### 失败标准

- 所有非共面构型的 |Gamma^V| < 1e-3：单三角非共面无法实现可探测手征响应，P0 假设不成立
- |Gamma^V|_sky_max < 0.01：无法与多星座交叉相关结果（~1.0）建立有意义的比较基准
- Michelson 变量在非共面情况下 |Gamma^V| > 1e-8：与 Iteration 6 结果矛盾，基础框架有偏差
- 共面 E 变量 |Gamma^V| > 1e-8：镜面反射对称性证明存在漏洞

---

## 硬约束（不可妥协）

### 1. 复用已有代码框架

- **Base 1**: `scripts/10-olc-chiral-orf-triangular.py` (Iteration 6 — Michelson-like 变量 + 单臂链路响应)
- **Base 2**: `scripts/11-multi-constellation-chiral-orf.py` (Iteration 7 — E 变量 CW sum + 归一化约定)
- **Validation**: `scripts/test_crosscorr_symmetry.py` (镜面反射对称性验证框架)
- **双检测器求解器**: `scripts/09-olc-chiral-orf.py` (double-check，已验证)
- **不修改任何已有脚本** — fork 新脚本

### 2. 与 Iteration 6/7 方法论一致

- 天区数值积分（不用留数定理）
- 网格：ntheta >= 32, nphi >= 64
- 积分权重：sin(theta) * (pi/ntheta) * (2*pi/nphi)
- 归一化：sqrt(auto1 * auto2)
- sky-averaged 和 sky-maximized **两种** 都必须计算

### 3. E 变量天线模式 (CW sum)

- R_E+ = sum_{CW links} F_+(link_k) * T(f, L, cos_nu)
- R_Ex = sum_{CW links} F_x(link_k) * T(f, L, cos_nu)
- CW links: (0→1, 1→2, 2→0)
- 归一化约定：norm_V = 1.0 for coplanar CW sum (同 Iteration 7)

### 4. 非共面构型参数定义

以下参数必须在 [0, pi] 或合理物理范围内：

| 参数 | 符号 | 扫描范围 | 步长/点数 | 物理意义 |
|------|------|---------|----------|---------|
| 倾斜角 | theta_inc | 0°–90° | 0, 15, 30, 45, 60, 75, 90 (7 点) | 三角形平面法向量与参考方向夹角 |
| 高度差 | delta_h/L | 0–0.5 | 0, 0.1, 0.2, 0.3, 0.4, 0.5 (6 点) | 卫星偏离理想平面的归一化高度 |
| 边长比 | L_max/L_min | 0.7–1.3 | 1.0, 1.1, 1.2, 1.3 (4 点) | 不等臂三角形 |
| 标量三重积 | coplanarity | 0 (共面) 到 0.1 (深度非共面) | 连续扫描 | (r2-r1) . ((r3-r1) x n_ref) |

**深度非共面构型构造方法**（示例，具体实现见计算计划）：
- 将三角形平面绕 X 轴旋转 theta_inc
- 在三卫星中沿法线方向附加高度差 delta_h
- 调整三臂长度比

### 5. 频率扫描范围

- 1 mHz 到 100 Hz
- log-spaced，至少 20 个点
- 重点标注公共频段 1 mHz — 10 Hz

### 6. 归一化约定

使用 Iteration 7 已确认的 norm_V = 1.0 归一化约定（E 变量 CW sum）。**不可与 Orlando 的 chi_orb = 0.17 混为一谈**（memory/15 已解析二者量纲不同）。

---

## 可妥协部分（质量降级但可交付）

1. **边长比扫描可减少**：如果计算资源有限，边长比可减少为 2 个点 (1.0, 1.2)，但不推荐
2. **深度非共面构型优先选择**：如果全参数空间扫描量过大，优先扫描 theta_inc (7 点) x delta_h/L (3 点) = 21 种组合，边长比固定为 1.0
3. **频率范围缩减**：如果全频段计算量过大，可先计算 1 mHz — 10 Hz 公共频段
4. **图表 DPI**：不达标时可降低但仍保留数据

---

## 前置依赖

- 阶段 1 输出（`loop/1-loop/01-任务澄清-Iteration8.md`）
- Iteration 6 代码 `scripts/10-olc-chiral-orf-triangular.py` (三角 Michelson 变量 + 单臂链路响应，已验证)
- Iteration 7 代码 `scripts/11-multi-constellation-chiral-orf.py` (E 变量 CW sum + 归一化约定，已验证)
- 对称性验证 `scripts/test_crosscorr_symmetry.py` (镜面反射对称性验证框架，已验证)
- Iteration 7 决策文件 (multi-constellation baseline data)
- Orlando et al. 2021 JCAP 的 LISA-Taiji chiral ORF 结果（基准参考）
- memory/15-orlando-chi_orb-resolution-iteration8.md (归一化约定解析)
- memory/16-orlando-nonzeroRV-mirror-plane.md (镜面反射对称性与 R^V = 0)

---

## 后置依赖

- 本阶段输出（`03-任务分解.md`）是阶段 4（信息搜集）的输入
- 2-loop 执行将基于本阶段的任务分解
- 如果阶段 4 发现需补充文献 → 阶段 4 产出影响阶段 5 的置信度评估
- 论文第 7 章将基于本阶段结果更新（非共面构型章节）

---

## 风险与阻塞

| 风险 | 级别 | 缓解措施 |
|------|------|---------|
| R1: 深度非共面单三角 OLC 的 Gamma^V 最大值远小于 1e-3 | **HIGH** | 已知单臂非共面链路对可实现 |Gamma^V| ~ 0.041 (30 mHz)。如果 E 变量的三臂求和后 Gamma^V 衰减，应转向单臂链路对计算。高频区 (f > 30 mHz) 重点分析。 |
| R2: E 变量的三臂 CW sum 可能恢复某种对称性导致 Gamma^V = 0 | **HIGH** | 检查 R_E+ 和 R_Ex 中各臂贡献的相对符号。如果三臂贡献恰好抵消，尝试不对称权重组合（如 E' = a*X + b*Y + c*Z with a != b != c）。 |
| R3: 倾斜角扫描中 Theta_inc = 0° 和 180° 可能产生相同结果（镜面对称） | **MEDIUM** | 在参数扫描前验证对称性，避免冗余计算。 |
| R4: 参数空间扫描计算量大（7 x 6 x 4 = 168 种构型 x 20 频率点 x 32x64 天区网格） | **MEDIUM** | 优先级排序：先扫 theta_inc x delta_h/L = 42 组合，确认趋势后再扩展边长比。使用向量化 numpy 运算，分批计算。 |
| R5: 非共面构型的"参考平面"定义歧义 | **LOW** | 明确定义：参考平面 = xy 平面（日心轨道面），倾斜绕 X 轴旋转。 |

---

## 计算计划（1-loop/02 阶段）

### Script 策略

| 编号 | 脚本 | 来源 | 动作 |
|------|------|------|------|
| S1 | `scripts/12-noncoplanar-triangular-chiral-orf.py` | fork 10 + 11 | **新建**: 主脚本，实现非共面构型生成 + 参数扫描 |
| S2 | `scripts/10-olc-chiral-orf-triangular.py` | Iteration 6 | 只读复用：Michelson 验证、单臂链路响应 |
| S3 | `scripts/11-multi-constellation-chiral-orf.py` | Iteration 7 | 只读复用：E 变量 CW sum 框架、归一化 |

### S1 脚本核心函数设计

```python
def build_noncoplanar_triangle(theta_inc, delta_h, side_ratios):
    """
    构建非共面三角形构型
    theta_inc: 倾斜角 (rad)
    delta_h: 高度差 (m)
    side_ratios: [L12, L23, L31] / L0  臂长比
    返回: numpy array of 3 satellite positions (N, 3, 3)
    """
    # 1. 先构建等边三角形在 xy 平面
    # 2. 绕 X 轴旋转 theta_inc
    # 3. 沿法线方向附加高度差
    # 4. 调整臂长比
    pass

def coplanarity_measure(sat_positions):
    """
    标量三重积非共面度量
    coplanarity = |(r2-r1) . ((r3-r1) x n_ref)| / (|r2-r1| * |r3-r1|)
    值 = 0 表示共面，值 > 0 表示非共面
    """
    r1, r2, r3 = sat_positions
    return abs(np.dot(r2-r1, np.cross(r3-r1, n_ref))) / ...

def compute_e_variable_chiral_orf(f, sat_positions, L):
    """
    E 变量 (CW sum) 手征 ORF 计算
    复用 11-multi-constellation 中的 antenna_pattern_e_variable_universal
    """
    pass

def michelson_chiral_orf(f, sat_positions, L):
    """
    Michelson-like 变量手征 ORF
    复用 10-olc-chiral-orf-triangular.py
    """
    pass
```

### 参数扫描优先级

| 优先级 | 扫描 | 组合数 | 预期时间 |
|--------|------|--------|---------|
| P0 | theta_inc = [0, 30, 60, 90] x delta_h/L = [0, 0.25, 0.5] | 12 | ~2 min |
| P1 | theta_inc = [0, 15, 30, 45, 60, 75, 90] x delta_h/L = [0, 0.25, 0.5] | 21 | ~4 min |
| P2 | P1 + side_ratio = [1.0, 1.2] | 42 | ~8 min |
| P3 | 全参数空间 7 x 6 x 4 | 168 | ~32 min |

**交付要求**: P0 + P1 是最低交付要求（确认趋势），P2 + P3 是推荐完整扫描。

### 天区积分细节

- 基础网格: ntheta = 32, nphi = 64
- 验证网格: ntheta = 64, nphi = 128 (在至少 3 种构型上验证收敛)
- 积分权重: dOmega = sin(theta) * (pi/ntheta) * (2*pi/nphi)

### 预期输出

| 输出 | 格式 | 说明 |
|------|------|------|
| ORF_data.csv | CSV | 所有构型 + 频率的 Gamma^V, Gamma^I, auto 值 |
| gammaV_vs_coplanarity.png | PNG | |Gamma^V| 随非共面度量变化曲线 |
| gammaV_vs_inclination.png | PNG | |Gamma^V| 随倾斜角变化曲线 |
| gammaV_frequency_comparison.png | PNG | 所有构型的频率依赖曲线对比 |
| comparison_multiconstellation.png | PNG | 单三角非共面 vs 多星座结果对比 |
| memory/17-noncoplanar-olc-chiral-orf-iteration8.md | MD | 更新 memory 文件 |

---

## 置信度评估

| 维度 | 初始值 | 论据 |
|------|--------|------|
| 理论基础 | 0.90 | Iteration 6 严格证明 + Iteration 7 多星座验证 + memory/15/16 归一化约定解析 |
| 代码可用度 | 0.90 | Iteration 6 + 7 脚本可直接复用（10 和 11） |
| 单臂非共面链路对已知结果 | 0.95 | 已知 |Gamma^V| > 0.041 at 30 mHz (K3) |
| E 变量单三角非共面未知程度 | 0.50 | E 变量是三臂 CW sum，可能破坏或恢复对称性，需要数值验证 |
| 参数空间复杂度 | 0.70 | 全参数空间 168 种构型，计算量可控 |
| **综合置信度** | **0.70** | |

**目标置信度**: 0.80（通过 Iteration 8 验证 P1-P5 判定标准达成）

---

## 副脑质疑

### 质疑 #1：单三角非共面与多星座交叉相关的物理起源是否真的相同？

**回答方向**：
- 多星座交叉相关的非零 R^V 来自**网络效应**：不同轨道位置 (~60° 分离) 的空间相位因子 exp(-2pi i k . (x_1 - x_2)) 破坏对称性 (memory/16)
- 单三角非共面的非零 R^V 来自**构型效应**：三卫星不在同一平面内破坏镜面反射对称性
- 二者都涉及 3D 几何，但前者是**空间分离**，后者是**局部非共面**
- 关键问题：单三角构型的非共面尺度 (~2.5 Gm) vs 多星座的空间分离 (~1 AU) 是否意味着完全不同的物理？

### 质疑 #2：如果 E 变量 CW sum 的三臂贡献恰好相互抵消怎么办？

**回答方向**：
- 共面等边三角形中，三臂 CW sum 的 R_E+ = F_+(0->1) + F_+(1->2) + F_+(2->0)
- 如果各臂 R_+ 对天空各向同性分布，求和可能接近零
- 但是 R_Ex 可能有非零贡献，chiral factor 是 R_E+ * R_Ex 的叉积
- 如果不抵消：R_Ex = R_E+ 且 R_Ex = R_E+（相同函数形式）→ chiral factor 仍为零
- **最坏情况**：E 变量三臂和可能恰好恢复某种对称性
- **降级方案**：直接计算单臂链路对 Gamma^V，跳过 E 变量

### 质疑 #3：深度非共面是否"物理可执行"？人工构造 vs 真实轨道

**回答方向**：
- Q1 关注真实轨道运动导致的自然非共面性：需要轨道动力学计算，不在本迭代核心范围内
- Q2 聚焦人工构造深度非共面构型，这是验证性研究
- 即使人工构造在现实中不可行，也能为设计原则提供指导（非共面度与 Gamma^V 关系）
- 如果人工非共面构型实现 |Gamma^V| > 0.01，即使数值高于真实可达值，也为未来探测方案提供上限估计

---

## 完成时间

last_completed_at: pending

---

## 回滚

回滚到 01-任务澄清。
