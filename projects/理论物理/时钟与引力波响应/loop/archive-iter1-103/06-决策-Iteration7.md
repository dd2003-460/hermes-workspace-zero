# 06-决策（Iteration 7）— 多星座手征 ORF

> 所属规格：`/Users/a1-6/Desktop/workspace/loop/1-loop/06-决策.md`
> 迭代编号：7
> 输入：01-任务澄清 + 05-完备核验

---

## 决策结论: enter_2loop

**置信度: 0.82** (>= 0.70 门槛)

**决定: 进入 2-loop 执行阶段**

---

## 核心科学结论

### 科学问题
不同星座的交叉相关能否突破单一星座 chiral ORF = 0 的限制？

### 预期答案
是。不同星座的空间位置、轨道倾角、臂长差异破坏了 F_A(u) = F_A(-u) 的对称性条件，使 Gamma^V 非零。

### 关键依据
1. **Orlando 2021**: LISA-Taiji 非共面构型 |Gamma^V|_max ~ 0.3（已验证）
2. **Chen-Liu-Zhang JCAP 2025**: 双三角网络框架证实此方向有效性
3. **Iteration 6**: 已严格证明单一星座内 Michelson-like 变量的零结果（对称性恒等式）
4. **物理机制**: 不同星座的 R_a ≠ R_b（不同几何 = 不同响应 = 不对称性）

---

## 执行计划概要

### M1 (P0): 代码 Fork + 多星座基础框架
- 从 `10-olc-chiral-orf-triangular.py` fork 为 `11-multi-constellation-chiral-orf.py`
- 新增 Constellation 类 + compute_cross_orf() 函数
- 验收: 单星座回归测试通过（OLC x OLC = 零结果）

### M2 (P0): Taiji x LISA 基准验证
- 对标 Orlando 2021
- 验收: 60 deg 倾角下 |Gamma^V|_max 在 0.05-0.5 范围内

### M3 (P0): OLC x Taiji 核心计算
- 验收: |Gamma^V| 至少在某些频率 > 1e-3

### M5 (P0): 频率扫描 + 参数化研究
- 验收: 频率曲线连续、收敛性验证通过

### M4 (P1): OLC x LISA 扩展
### M6 (P1): 结果总结 + 论文更新

---

## 失败条件

如果以下任一条件触发，终止迭代并重新规划：
1. Taiji x LISA 基准验证失败（|Gamma^V| 与 Orlando 偏差 > 50%）
2. OLC x Taiji 的 |Gamma^V| 始终 < 1e-3（需要探索 4+ 星座或其他方案）
3. 数值计算出现非物理发散

---

## DAG 拓扑排序

```
M1 (Fork) -> [M2, M3] -> M5 -> M6
             M4 (并行，可延后)
```

---

last_updated: 2026-07-05
decision: enter_2loop
next_brain_sub: dispatch sub-brain critique, then enter 2-loop/01
