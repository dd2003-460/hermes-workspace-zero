# 02-目标澄清（Iteration 7）— 多星座混合网络手征 ORF

**所属规格**：`/Users/a1-6/Desktop/workspace/loop/1-loop/02-目标澄清.md`
**状态**：in-progress
**输入**：loop/1-loop/01-任务澄清-Iteration7.md
**输出**：本文件 + 内嵌验收标准

---

## 阶段目标

在 Iteration 6 严格证明三角 OLC Michelson-like 变量手征 ORF = 0（对称性恒等式）的基础上，扩展至**多星座混合网络**交叉相关计算，验证不同星座间能否获得非零 Gamma^V。

**核心问题**：不同星座（OLC triangle、Taiji triangle、LISA triangle）之间的 Michelson-like 变量交叉相关，其 chiral factor 是否因几何不对称性而突破 Gamma^V = 0 的限制？

**具体目标**：
1. 计算 **OLC triangle × Taiji triangle** 交叉相关 chiral ORF（P0：相同可测量类型 = 频率偏移）
2. 计算 **Taiji triangle × LISA triangle** 交叉相关 chiral ORF（验证基准：对标 Orlando et al. 2021，60 度倾角下 |Gamma^V| ~ 0.3）
3. 计算 **OLC triangle × LISA triangle** 交叉相关 chiral ORF（扩展：不同可测量，需处理归一化）
4. 确认同一星座自关联（OLC × OLC）仍为 Gamma^V = 0，与 Iteration 6 结果一致
5. 分析 chiral ORF 随星座间相对几何参数（相对倾角、相对相位）的变化规律

---

## 期望结果

### 必须产出（Iteration 7 完成标志）

1. **混合星座 chiral ORF 数值表**：对 OLC×Taiji、Taiji×LISA、OLC×LISA 三种组合给出 Gamma^V(f) 在关键频率点的值
2. **频率依赖曲线**：在 0.1 mHz — 10 Hz 范围内绘制 |Gamma^V(f)|，公共频段重点标注
3. **单一星座 vs 混合网络对比图**：可视化展示混合网络（Gamma^V ≠ 0）vs 单一星座（Gamma^V = 0）的对比
4. **Taiji × LISA 基准验证**：确认 Taiji×LISA 组合的 |Gamma^V| 在低频率极限下与 Orlando et al. 2021 的 LISA-Taiji 结果一致（~0.3）

### 理论目标

1. **确认突破**：验证混合星座确实能产生非零 chiral ORF
2. **量化优势**：给出混合网络的 chiral ORF 量级，与 PTA/LISA-Taiji 对比
3. **指导任务设计**：为未来空间时钟星座网络的 chiral 探测能力提供定量约束

---

## 判定标准

### 必须满足（Pass/Fail）

| # | 判定标准 | 通过条件 | 类型 |
|---|---------|---------|------|
| 1 | **混合星座非零检验** | OLC × Taiji 的 |Gamma^V| > 1e-3（至少在 1 个频率点） | 硬约束 |
| 2 | **自关联零检验** | OLC × OLC（同星座自关联）的 |Gamma^V| < 1e-10 | 硬约束 |
| 3 | **Taiji × LISA 基准** | Taiji × LISA 的 |Gamma^V|_max 在 0.05 — 0.5 范围内（对标 Orlando 2021 的 ~0.3） | 硬约束 |
| 4 | **标准 ORF 自洽** | 所有组合的标准 ORF Gamma^I 量级在 0.01 — 1.0 范围内 | 硬约束 |
| 5 | **网格收敛** | ntheta=32→64 时，|Gamma^V| 变化 < 10% | 硬约束 |
| 6 | **频率平坦性** | |Gamma^V(f)| 在公共频段内变化 < 1 个量级（归一化后） | 可妥协 |
| 7 | **几何参数扫描** | 至少扫描 3 组相对倾角（0°、30°、60°），展示趋势 | 可妥协 |
| 8 | **可视化完整性** | 频率依赖曲线 + 星座对比图 + 参数扫描图全部生成 | 可妥协 |

### 失败标准

- 所有混合星座组合的 |Gamma^V| < 1e-3：chiral 灵敏度仍然不可观测，需要 4+ 卫星星座或非 Michelson 可观测构造
- |Gamma^V| 发散或 > 1.0：数值错误或公式错误
- Taiji × LISA 的 |Gamma^V| 与 Orlando 2021 偏差 > 50%：代码实现存在系统性偏差
- OLC × OLC 自关联 |Gamma^V| > 1e-8：与 Iteration 6 结果不一致，基础框架有偏差

---

## 硬约束（不可妥协）

1. **复用已有代码框架**
   - 在 `scripts/10-olc-chiral-orf-triangular.py` 的基础上 fork → `scripts/11-multi-constellation-chiral-orf.py`
   - 不修改任何已有脚本
   - 使用 `scripts/09-olc-chiral-orf.py` 中的 chiral ORF 求解器作为 double-check
   - 使用 `scripts/06a-patched-mixed-network.py` 中的 detector 参数（噪声模型、灵敏度）

2. **与 Iteration 6 方法论一致**
   - 天区数值积分（不用留数定理，保持数值积分方法）
   - 网格：ntheta >= 32, nphi >= 64
   - 积分权重：sin(theta) * (pi/ntheta) * (2*pi/nphi)
   - 归一化：sqrt(auto1 * auto2)

3. **Michelson 变量构建一致**
   - 每个 Michelson 变量 = 两条反向单向链路的相干叠加
   - 有效天线方向图 = 两条链路天线方向图的叠加（包含传递函数）
   - R_A^M(u) = R_A(link_a) + R_A(link_b)，其中 link_a 和 link_b 为构成 Michelson 的两条单向链路

4. **探测器参数定义**
   - OLC triangle: 臂长 L_OLC = 0.17 Gm（空间 OLC 参数，紧凑构型）或 3 Gm（扩展构型），两组参数均需扫描
   - Taiji triangle: 臂长 L_Taiji = 2.5 Gm
   - LISA triangle: 臂长 L_LISA = 2.5 Gm
   - 不同星座的相对位置：假设在同一日心轨道上（最小复杂度假设）
   - 日心轨道半径：1 AU
   - 轨道倾角：参数化扫描（0°、30°、60°）

5. **相对几何参数化**
   - 星座间相对倾角 delta_i：从 0° 到 90°，步长 15°（至少 3 个点：0°, 30°, 60°）
   - 星座间相对相位 delta_phi：从 0 到 2pi，固定为一个参考值（如 pi/2）
   - 星座间角距离 delta_alpha：假设星座中心在同一轨道平面上有固定角距离（如 0°、60°、120°）

6. **不同可观测量的处理**
   - OLC × Taiji（相同可测量 = 频率偏移）：直接使用 chiral ORF 公式
   - Taiji × LISA（相同可测量 = 应变差）：直接使用 chiral ORF 公式
   - OLC × LISA（不同可测量）：需要频率偏移灵敏度转换为等效应变灵敏度
     - OLC 频率偏移灵敏度 S_h_OLC(f) = 2*pi*f * S_y_OLC(f)（等效应变）
     - 交叉相关归一化因子需统一量纲

---

## 可妥协部分（质量降级但可交付）

1. **OLC × LISA 暂时不做**：如果不同可观测量的转换存在理论不确定性，可先只计算 OLC × Taiji 和 Taiji × LISA，后续扩展
2. **几何参数扫描点数不足**：如果计算资源有限，相对倾角扫描可减少为 2 个点（0°、60°），但不推荐
3. **频率范围缩减**：如果全频段（0.1 mHz — 10 Hz）计算量过大，可先计算公共频段（1 mHz — 1 Hz）
4. **图表分辨率**：DPI/分辨率不达标时可降低但仍保留数据

---

## 前置依赖

- 阶段 1 输出（`loop/1-loop/01-任务澄清-Iteration7.md`）
- Iteration 6 代码 `scripts/10-olc-chiral-orf-triangular.py`（三角 Michelson 变量 + chiral ORF 计算引擎，已验证）
- Iteration 5/6 双探测器求解器 `scripts/09-olc-chiral-orf.py`（double-check 用，已验证）
- Iteration 3 混合网络 `scripts/06a-patched-mixed-network.py`（detector 参数，已修复 4 个 bug）
- Orlando et al. 2021 JCAP 的 LISA-Taiji chiral ORF 结果（~0.3 at 60° inclination），用于验证基准
- Hu PRD 111, 084065 (2025) — 标准 ORF 精确计算方法
- Kato & Soda PRD 93, 062003 (2016) — 手征 ORF 定义
- Chen-Liu-Zhang JCAP 05, 050 (2025) (arXiv:2410.18916) — 双三角网络框架参考

---

## 后置依赖

- 本阶段输出（`03-任务分解.md`）是阶段 4（信息搜集）的输入
- 2-loop 执行将基于本阶段的任务分解
- 如果阶段 4 发现需补充文献 → 阶段 4 产出影响阶段 5 的置信度评估
- 论文第 7 章 §7.2.2 节将基于本阶段结果更新

---

## 风险与阻塞

| 风险 | 级别 | 缓解措施 |
|------|------|---------|
| 混合星座 Gamma^V 仍接近零（< 1e-3） | **HIGH** | 如果不同星座间对称性仍未被打破，探索 4+ 卫星星座或非 Michelson 可观测构造 |
| Taiji × LISA 基准验证失败（与 Orlando 2021 偏差 > 50%） | **HIGH** | 仔细检查 Michelson 变量定义、天线方向图计算、传递函数形式；Orlando 2021 可能使用了不同的近似 |
| 不同可观测量的交叉相关定义不明确 | **HIGH** | 优先实现相同可测量类型（OLC×Taiji, Taiji×LISA）；OLC×LISA 延后处理 |
| 数值计算量大（3 星座 × 多构型 × 多倾角 × 多频率） | **MEDIUM** | 控制网格密度 (ntheta=32, nphi=64 起步)，向量化 numpy 运算，分批计算 |
| 星座间相对几何参数化复杂 | **MEDIUM** | 从最简单几何开始（同一轨道平面、固定相对相位），逐步增加复杂度 |
| 传递函数频率范围超出数值精度 | **MEDIUM** | OLC 频率范围覆盖 mHz 到 Hz，传递函数在高频可能出现数值振荡，需检查 |

---

## 副脑质疑回答（来自 01-任务澄清）

### 质疑 #1：双 Michelson 结构的对称性能否真正被打破？

**回答**：能打破。关键点在于：
- 同一探测器的 Michelson 变量 M = link_a + link_b 中，两条链路来自同一空间位置、同一时间演化，R_A(link_a) 和 R_A(link_b) 的对称性源于 F_A(u) = F_A(-u) 偶函数性质
- 不同探测器的交叉相关中：R_A^M_OLC 来自 OLC 卫星群，R_A^M_Taiji 来自 Taiji 卫星群
- 即使各自的 M 都是 R_a + R_b 结构，交叉相关的 chiral factor 是：
  ```
  chiral = (R_+^M_OLC_a + R_+^M_OLC_b) * (R_x^M_Taiji_a + R_x^M_Taiji_b)
         - (R_x^M_OLC_a + R_x^M_OLC_b) * (R_+^M_Taiji_a + R_+^M_Taiji_b)
  ```
- 展开后有 4 × 4 = 16 项，其中跨探测器的交叉项（如 R_+^M_OLC_a * R_x^M_Taiji_b）没有 R_a = R_b 的对称性约束
- Orlando et al. 2021 已经数值验证了 LISA × Taiji 的非零 chiral ORF

### 质疑 #2：0 度轨道倾角时 chiral ORF 是否为零？

**回答**：需要数值验证。Orlando 2021 发现 60° 倾角时 |Gamma^V| ~ 0.3，0° 倾角时 |Gamma^V| → 0。这与对称性预期一致：共面构型保持某种手征对称性。**这本身就是重要结果**——可以确认 chiral ORF 对几何参数的敏感度。

### 质疑 #3：OLC 频率偏移与 LISA 应变的交叉相关物理意义？

**回答**：物理上，两种测量都是对同一引力波应变 h_ij 的投影响应，只是响应算子不同。OLC 的响应正比于频率偏移 S_y(f)，LISA 的响应正比于应变差 S_h(f)。交叉相关定义为：
```
C_OLC-Taiji(f) = <h_OLC*(f) * h_Taiji(f)> / (S_OLC(f) * S_Taiji(f))
```
其中 h_OLC = 2*pi*f * y_OLC（将频率偏移转换为等效应变）。量纲一致后交叉相关无量纲，物理意义明确。

### 质疑 #4：非零 chiral ORF 是否可探测？

**回答**：需要后续 SNR 计算（不在本 Iteration 范围内，但作为目标约束）。如果 |Gamma^V|_max > 0.01 且 OLC 频率偏移噪声模型支持，在 Omega_GW ~ 1e-10 的模型下，观测时间 < 1 年可能达到可探测性。SNR 计算留给后续迭代。

---

## 完成时间

last_completed_at: pending

---

## 回滚

回滚到 01-任务澄清。
