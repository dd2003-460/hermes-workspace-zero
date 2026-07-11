# 05-完备核验（Iteration 8）— 三角形 3 卫星 OLC 手征 ORF 物理分析 + 深度非共面构型

> 所属规格：`/Users/a1-6/Desktop/workspace/loop/1-loop/05-完备核验.md`
> 迭代编号：8
> 输入：01-任务澄清-Iteration8.md + 03-任务分解-Iteration8.md
> 注意：Iteration 8 未执行 04-信息搜集阶段（跳过），本核验基于 01+03 直接评估

---

## Step 1：理论完整性评估

### 评估结果: **partial**

### 已确立的理论基础

| 理论断言 | 来源 | 状态 |
|----------|------|------|
| 单平面探测器 R^V = 0（镜面反射对称性严格证明） | memory/16 | 已验证 |
| 共面三角 Michelson Gamma^V = 0（数值验证） | Iteration 6, scripts/10 | 已验证 |
| 单臂非共面链路对 |Gamma^V| > 0.041 at 30 mHz | Iteration 6 已知结果 K3 |
| 多星座交叉相关 |Gamma^V|_max ~ 1.0 | Iteration 7 已验证 |
| chi_orb = 0.17 是 Fisher 最佳拟合，非响应函数比 | memory/15 | 已解析 |
| 三归一化约定已区分 | memory/15 | 已确认 |

### 未确立的理论假设

| # | 假设 | 置信度 | 论据 |
|---|------|--------|------|
| T1 | 单三角非共面构型（倾斜+高度差+不等臂）可产生可观测 Gamma^V | 0.55 | 有单臂非共面链路对的已知结果支撑（|Gamma^V| > 0.041），但 E 变量三臂 CW sum 可能因对称性抵消而归零（sub-brain 质疑 #2） |
| T2 | |Gamma^V| 与 coplanarity 度量存在单调定量关系 | 0.60 | 物理直觉支持，但需数值验证。若 E 变量三臂贡献相互抵消，关系可能不存在 |
| T3 | 倾斜角 0-90 度扫描覆盖最优构型方向 | 0.70 | 参考平面 = xy 平面，绕 X 轴旋转。物理上合理但不保证没有更好的旋转轴 |
| T4 | 高频极限下单臂非共面链路对 |Gamma^V| > 1.0 | 已知结果 K3，Iteration 6 已验证 |

### 理论完整性结论

核心理论框架（镜面反射对称性 -> 对称性破缺 -> 非零 R^V）是完整的。关键缺口是 **T1**：E 变量三臂 CW sum 在深非共面构型下的实际行为未知。这是本迭代的探索目标而非理论缺陷。

---

## Step 2：工程可行性评估

### 评估结果: **partial**

### 代码依赖关系分析

| 脚本 | 用途 | 状态 | 风险评估 |
|------|------|------|---------|
| `scripts/10-olc-chiral-orf-triangular.py` | 三角 OLC 手征 ORF 框架 | 存在，Iteration 6 验证通过 | LOW — 成熟代码 |
| `scripts/11-multi-constellation-chiral-orf.py` | E 变量 CW sum + 归一化 | 存在，Iteration 7 验证通过 | LOW — 成熟代码 |
| `scripts/test_crosscorr_symmetry.py` | 对称性验证参考 | 存在，验证通过 | LOW — 参考代码 |
| `scripts/12-noncoplanar-triangular-chiral-orf.py` | **新建**: 非共面构型主脚本 | 不存在，Fork 产物 | **HIGH** — 本次迭代唯一新文件 |
| `scripts/09-olc-chiral-orf.py` | 双探测器求解器 (double-check) | 存在 | LOW — 备用验证 |

### Fork 策略评估

迭代 02 明确要求"不修改任何已有脚本 — fork 新脚本"。Fork 策略为：
- M1 将脚本 10 和 11 合并 fork 为脚本 12
- 脚本 12 需实现 `build_noncoplanar_triangle()`, `coplanarity_measure()`, `compute_e_variable_chiral_orf()`, `compute_michelson_chiral_orf()`, `compute_single_arm_pair_chiral_orf()`

**风险评估**:
- 脚本 10 和 11 使用相同的 `olc_transfer_function`（确认一致）
- 脚本 10 的 link_response 函数基于 atomic projection 构建单臂响应
- 脚本 11 的 E 变量天线模式基于 chiral antenna pattern（chiral_antenna 函数）
- **关键接口对齐风险**: 两个脚本使用不同的天线模式实现路径，需确认在共面极限下收敛到相同物理结果
- 脚本 11 使用 `chiral_antenna(arm1, arm2)` 返回 (GR1-GR2, GL1-GL2)，其中 GR = (a+ib)^2/4
- 脚本 10 使用 `olc_link_response_grid` 直接计算 R_plus, R_cross
- 两种方法在共面等边三角形极限下应一致（已有数值验证）

### 工程可行性结论

Fork 策略可行，主要风险在于脚本 12 的合并接口对齐。M2（共面零检验）正是为此设计的回归验证——如果接口不对齐，零检验失败即触发修复。

---

## Step 3：工具就绪度评估

### 评估结果: **partial**

### 工具清单

| 工具 | 版本 | 就绪度 | 说明 |
|------|------|--------|------|
| Python 3 | system | complete | N/A |
| numpy | system | complete | 天区积分、几何运算 |
| matplotlib | system | complete | 绘图输出 |
| scipy (拟合) | system | complete | M5 回归拟合 |
| 天区数值积分 | ntheta=32, nphi=64 | complete | 标准配置 |
| 脚本 10 框架 | Iteration 6 | complete | 只读复用 |
| 脚本 11 框架 | Iteration 7 | complete | 只读复用 |
| 脚本 12 (fork) | 待创建 | **missing** | 阻塞所有计算 |
| 参数扫描引擎 | 待实现 | **missing** | 脚本 12 的一部分 |
| 结果可视化 | 待实现 | **missing** | 脚本 12 的一部分 |
| figures/ 目录 | 待创建 | **missing** | 输出目录 |
| ORF_data_8.csv 格式 | 待定义 | **missing** | 数据结构需定义 |

### 阻塞项

1. **scripts/12** 未创建 — 阻塞 M2-M6 全部计算任务
2. **figures/** 目录未创建 — 阻塞可视化输出
3. **04-信息搜集-Iteration8.md** 未创建 — 跳过（05 spec 中提到输入来自 tool-inventory，但 Iteration 8 未执行 04 阶段）

### 工具就绪结论

所有基础工具（Python, numpy, matplotlib, scipy）就绪。唯一阻塞项是脚本 12，这是本次迭代的主要产出不属于"就绪度"问题。

---

## Step 4：方向正确性评估

### 评估结果: **complete**

### 判定标准覆盖度

| 判定标准 | 对应子任务 | 方法覆盖 | 评分 |
|----------|-----------|---------|------|
| P1: 共面 E 变量 Gamma^V < 1e-10 | M2 | 共面极限回归测试 | complete |
| P2: 非共面 E 变量 Gamma^V > 1e-3 | M3, M4 | 全参数扫描 | complete |
| P3: |Gamma^V|_sky_max > 0.01 | M4 | 全参数扫描极值搜索 | complete |
| P4: |Gamma^V|-几何参数定量关系 | M5 | 线性/二次拟合 | complete |
| P5: 高频极限 |Gamma^V| > 1.0 | M2 | 单臂链路对标 K3 | complete |
| P6: 网格收敛 < 10% | M5 | ntheta 32->64 对比 | complete |
| P7: Michelson 零检验 < 1e-8 | M2, M3 | 所有构型验证 | complete |
| P8: 频率扫描覆盖 | M2, M3, M4 | 1 mHz-100 Hz, log-spaced, >=20 点 | complete |

### 与 04-信息搜集的衔接

Iteration 8 未执行 04 阶段。03-任务分解已直接基于 Iteration 6/7 代码和 memory/15/16 信息。信息缺口：
- 无 Orlando 2021 原文的额外文献挖掘（但 01 中 R1-R8 参考列表完整）
- 无新的实验数据或仿真结果（理论计算项目，非实验）
- 无额外的基准验证数据

**评估**: 作为理论+数值计算项目，Iteration 8 所需信息已在 01+03 中充分覆盖，04 阶段的跳过是合理的。

---

## Step 5：可回滚性评估

### 评估结果: **complete**

### 各任务回滚方案

| 子任务 | 回滚方案 | 代价 |
|--------|---------|------|
| M1: Fork | 丢弃脚本 12，重新 fork | 低 — 纯编码 |
| M2: 回归验证 | 零检验失败则修复接口 | 低 — 修复后重新验证 |
| M3: 核心扫描 | 调整参数范围后重扫 | 低 — 参数可逆 |
| M4: 全参数扫描 | 跳过（质量降级可交付） | 低 — 可跳过 |
| M5: 拟合+收敛 | 重新拟合或调整网格 | 低 — 分析型任务 |
| M6: 总结+可视化 | 重绘图表 | 低 — 可视化可重做 |

### 代码安全

- 02 明确"不修改任何已有脚本"
- Fork 策略确保脚本 10 和 11 保持原始状态
- 无 git push 操作（仅本地文件）

---

## 核验清单

| # | 判定标准 | 可验证性 | 验证方法 | 阻塞状态 | 风险等级 |
|---|---------|---------|---------|---------|---------|
| P1 | 共面 E 变量 Gamma^V < 1e-10 | 高 | 共面极限回归测试（脚本 12 + 脚本 10 对比） | 阻塞于 M1（脚本 12 未创建） | 低 |
| P2 | 非共面 E 变量 Gamma^V > 1e-3 at f>10mHz | 高 | 全参数扫描（theta_inc x delta_h/L） | 阻塞于 M3（依赖 M2） | 中 — E 变量三臂抵消风险 |
| P3 | |Gamma^V|_sky_max > 0.01 | 中 — 需要全参数空间扫描 | 全参数扫描（M4） | 阻塞于 M4 | 中 |
| P4 | |Gamma^V|-几何参数拟合 R^2 > 0.5 | 高 | 回归分析（M5） | 阻塞于 M3+M4 | 低 |
| P5 | 高频极限 |Gamma^V| > 1.0 | 高 | 单臂链路对标 K3（M2） | 阻塞于 M2 | 低 — 已知结果 |
| P6 | 网格收敛 < 10% | 高 | ntheta 32->64 对比（M5） | 阻塞于 M3 | 低 |
| P7 | Michelson Gamma^V < 1e-8 | 高 | 所有构型验证（M2, M3） | 阻塞于 M1 | 低 |
| P8 | 频率扫描 1mHz-100Hz log-spaced >=20点 | 高 | 代码内实现验证（M2-M4） | 阻塞于 M1 | 低 |

---

## Gap 分析

### Gap 总览

| Gap ID | 描述 | 影响 | 缓解措施 | 严重度 |
|--------|------|------|---------|--------|
| G1 | **scripts/12 未创建** — 所有计算任务的阻塞依赖 | 阻塞 M2-M6 | M1 为主要产出不属于 gap，需执行完成 | 高 |
| G2 | **未执行 04-信息搜集** — Iteration 8 跳过该阶段 | 低 — 信息已在 01+03 中充分覆盖 | 无，跳过合理 | 低 |
| G3 | **E 变量三臂抵消风险** — sub-brain 质疑 #2 尚未验证 | 若 E 变量贡献抵消，P1/P2/P3/P4 均失败 | M2 包含 Michelson 对比（预期 Michelson 始终为 0），E 变量如为零则降级为单臂链路对计算 | **高** |
| G4 | **脚本 10/11 天线模式接口差异** — 两种不同的 R^V 计算方法 | 脚本 12 合并时可能导致共面极限不一致 | M2 共面零检验直接暴露此问题 | 中 |
| G5 | **单臂链路对 vs 全三角 E 变量的物理对应关系** — Iteration 6 中单臂链路对的结果不能直接推广到三臂 CW sum | 可能导致对 P2 的错误预期 | M3 的实际扫描结果将确认 | 中 |
| G6 | **figures/ 目录和 ORF_data_8.csv 数据结构未定义** | M6 产出格式不一致 | 脚本 12 实现时定义 | 低 |
| G7 | **倾斜角扫描轴的选择** — 仅考虑绕 X 轴旋转，可能存在更优的旋转轴 | 可能错过某些高响应构型 | 作为参数扫描的局部探索，物理结论不需要全局最优 | 低 |

### Blocking Gap 判定

**没有 blocking gap。**

- G1（脚本 12 未创建）是本次迭代的核心产出而非 gap
- G3（E 变量三臂抵消）虽有高严重度，但已有缓解措施（降级为单臂链路对），不阻塞 enter_2loop 决策
- 所有判定标准都有明确的验证方法

---

## Risk 缓解评估（R1-R5）

| 风险 | 级别 | 缓解措施评估 | 充分性 |
|------|------|-------------|--------|
| R1: 自然轨道运动非共面性过小 | 中 | 人工构造深度非共面构型 | **充分** — 直接绕过 Q1，专注 Q2 |
| R2: 单三角非共面 Gamma^V 最大值远小于 1e-3 | 中 | 重点分析高频区 (f > 30 mHz)，单臂链路对已知 > 0.041 | **充分** — 高频区有已知理论支撑 |
| R3: F_A(u) = F_A(-u) 在非共面构型下仍然保持 | 低 | E 变量不使用此对称性；单臂链路对独立计算 | **充分** — E 变量破坏此对称性 |
| R4: 168 构型计算量大 | 低 | P0/P1 优先级控制，12-21 组合先扫 | **充分** — 有降级策略 |
| R5: 参考平面定义歧义 | 低 | 明确定义：参考平面 = xy 平面，绕 X 轴旋转 | **充分** |

新增风险（来自 Gap 分析）:

| 风险 | 级别 | 缓解措施 | 充分性 |
|------|------|---------|--------|
| R6: E 变量三臂 CW sum 抵消 | **高** | M2 回归验证后立即暴露；如为零则转单臂链路对分析 | **部分充分** — 降级方案有效但意味着 E 变量方案失败 |
| R7: 脚本 12 接口对齐问题 | 中 | M2 共面零检验暴露；修复后重新验证 | **充分** |

---

## Gap Analysis JSON

```json
{
  "theoretical_integrity": "partial",
  "engineering_feasibility": "partial",
  "tool_readiness": "partial",
  "direction_correctness": "complete",
  "revertibility": "complete",
  "total_criteria": 8,
  "verified": 0,
  "gaps": [
    {
      "id": "G1",
      "description": "scripts/12 未创建 — 所有计算任务的阻塞依赖",
      "impact": "阻塞 M2-M6",
      "resolution": "M1 为本次迭代核心产出，不属于 gap",
      "severity": "high"
    },
    {
      "id": "G2",
      "description": "未执行 04-信息搜集 — 理论+数值项目非必需",
      "impact": "低 — 信息已在 01+03 中充分覆盖",
      "resolution": "跳过合理，无缓解需求",
      "severity": "low"
    },
    {
      "id": "G3",
      "description": "E 变量三臂 CW sum 抵消风险 — 若三臂贡献相互抵消，所有 E 变量判定标准失效",
      "impact": "P1/P2/P3/P4 均可能失败",
      "resolution": "M2 回归验证后暴露；降级为单臂链路对计算",
      "severity": "high"
    },
    {
      "id": "G4",
      "description": "脚本 10/11 天线模式接口差异 — chiral_antenna vs olc_link_response_grid",
      "impact": "脚本 12 合并后共面极限可能不一致",
      "resolution": "M2 共面零检验直接暴露此问题",
      "severity": "medium"
    },
    {
      "id": "G5",
      "description": "单臂链路对与全三角 E 变量对应关系不确定",
      "impact": "对 P2 的预期可能错误",
      "resolution": "M3 实际扫描将确认",
      "severity": "medium"
    },
    {
      "id": "G6",
      "description": "figures/ 目录和 ORF_data_8.csv 数据结构未定义",
      "impact": "M6 产出格式不一致",
      "resolution": "脚本 12 实现时定义",
      "severity": "low"
    },
    {
      "id": "G7",
      "description": "倾斜角仅绕 X 轴旋转，可能存在更优旋转轴",
      "impact": "可能错过某些高响应构型",
      "resolution": "局部探索足够，不影响物理结论",
      "severity": "low"
    }
  ],
  "blocking_gaps": [],
  "enter_2loop_feasible": true,
  "notes": "Iteration 8 的 1-loop 规划完整。核心风险 G3（E 变量抵消）有明确缓解方案。建议 enter_2loop 后优先执行 M2 共面零检验，如验证通过则立即启动 M3 核心扫描。若 M2 中 E 变量共面 Gamma^V 不接近零（> 1e-8），说明接口对齐有问题，需在 M1 层面修复后再继续。"
}
```

---

## 置信度评估

| 维度 | 置信度 | 论据 |
|------|--------|------|
| 理论基础完整性 | **0.85** | Iteration 6 严格证明 + Iteration 7 验证 + memory/15/16 归一化约定解析 |
| 工程可行性 | **0.75** | Fork 策略正确，但脚本 12 接口对齐未知（G4） |
| 工具就绪度 | **0.70** | 基础工具就绪，脚本 12 是本次迭代核心产出 |
| 方向正确性 | **0.90** | 8 项判定标准全部覆盖，验证方法明确 |
| 可回滚性 | **0.95** | 不修改已有代码，每个任务有回滚方案 |
| 核心假设 (G3) | **0.55** | E 变量三臂 CW sum 抵消风险是唯一高严重度不确定因素 |
| **综合置信度** | **0.75** | 加权平均 |

---

## Enter 2-loop 决策

**置信度 0.75 >= 0.70**: **推荐 enter_2loop**

### 理由
1. 理论基础和方法论充分成熟（置信度 0.85）
2. 判定标准 P1-P8 全部覆盖，验证方法明确（置信度 0.90）
3. 代码复用策略正确，回滚可行（置信度 0.95）
4. 无 blocking gap，所有风险有缓解措施
5. 核心风险 G3（E 变量抵消）已在规划中预留降级方案

### 2-loop 执行优先级建议
1. **M2 回归验证** — 如果失败，立即修复 M1 再重试
2. **M3 核心扫描** — 优先 P0+P1（12 组合）确认趋势
3. **M5 拟合+收敛** — 在 M3 结果出炉后立即执行
4. **M4 全参数扫描** — 视 M3 趋势决定是否完整执行
5. **M6 总结** — 收尾阶段

### 退出条件
- 如果 M2 中 E 变量共面 Gamma^V > 1e-8：M1 接口对齐失败，需修复后重新 enter_2loop
- 如果 M3 中所有构型 Gamma^V < 1e-8：E 变量方案失败，降级为单臂链路对分析
- 如果 M3 确认 |Gamma^V| > 1e-3：继续 M4 全参数扫描，进入 2-loop 核心阶段

---

## 副脑质疑响应（Iteration 8 特定）

### 来自 02 文件的质疑 #1：单三角非共面与多星座物理起源是否相同？

**响应**: 不完全相同，但共享同一底层对称性破缺机制。
- 多星座：空间相位因子 `exp(-2pi i k . (x_1 - x_2))` 破坏对称性（network effect）
- 单三角非共面：三卫星不共面直接破坏镜面反射对称性（geometric effect）
- 共同本质：R^V = 0 的条件是镜面反射对称性成立，任何破坏该对称性的几何构型都允许 R^V != 0
- 本迭代的目标之一（通过 M6）就是确认这一物理联系

### 来自 02 文件的质疑 #2：E 变量三臂 CW sum 可能抵消？

**响应**: 已在 Gap G3 中评估，置信度 0.55。缓解措施：
- M2 共面零检验可先验证 E 变量框架正确性
- M3 中若所有倾角 Gamma^V < 1e-8，说明抵消确实发生
- 此时降级为单臂非共面链路对分析（M2 已覆盖此路径）
- 单臂链路对已知 |Gamma^V| > 0.041 at 30 mHz，足以回答核心物理问题

### 来自 02 文件的质疑 #3：深度非共面是否"物理可执行"？

**响应**: 本迭代聚焦人工构造构型作为验证性研究。即使人工构造在现实中不可行，结果也能为探测方案设计提供上限估计和设计指导原则。真实轨道动力学效应（Q1）可留待后续迭代。

---

## 关键输入文件

| 文件 | 内容 | 可靠性 |
|------|------|--------|
| loop/1-loop/01-任务澄清-Iteration8.md | 任务定义 + 8 判定标准 + 4 硬约束 | 高 |
| loop/1-loop/02-目标澄清-Iteration8.md | 详细参数扫描方案 + 置信度评估 | 高 |
| loop/1-loop/03-任务分解-Iteration8.md | M1-M6 DAG + 并行方案 | 高 |
| memory/15-orlando-chi_orb-resolution-iteration8.md | 归一化约定解析 | 高 |
| memory/16-orlando-nonzeroRV-mirror-plane.md | 镜面反射对称性分析 | 高 |
| scripts/10-olc-chiral-orf-triangular.py | 三角 OLC 框架 | 高（Iteration 6 验证） |
| scripts/11-multi-constellation-chiral-orf.py | E 变量 CW sum | 高（Iteration 7 验证） |
| scripts/test_crosscorr_symmetry.py | 对称性验证参考 | 中（参考代码） |

---

## 副脑子任务派发

```
next_brain_sub: 进入 06-决策阶段，基于 enter_2loop_feasible=true 推进执行
sub_brain_focus:
  - M1 优先级最高：Fork 脚本 12，正确实现 build_noncoplanar_triangle + coplanarity_measure
  - M2 是第一个 gate：共面零检验（P1, P7）和单臂链路对标（P5）
  - 需特别关注 E 变量与 Michelson 的对比（验证 E 变量框架正确性）
  - 如 E 变量共面 Gamma^V > 1e-8，说明实现有问题，需回 M1 修复
  - 如果 E 变量共面 Gamma^V < 1e-10 但非共面仍 < 1e-10（三臂抵消），降级为单臂链路对分析
```

---

last_updated: 2026-07-10
decision: enter_2loop (confidence=0.75)
next_brain_sub: 进入 06-决策阶段，推进进入 2-loop 执行
