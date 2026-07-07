# 01-pre-check — Iteration 5 手征 ORF 求解器

**所属规格**：`/Users/a1-6/Desktop/workspace/loop/2-loop/01-pre-check.md`
**状态**：completed
**输入**：loop/1-loop/06-决策-Iteration5.md (enter_2loop: true)
**输出**：预检查结果

---

## 环境检查

| 检查项 | 结果 |
|--------|------|
| Python 版本 3.9.6 | ✅ PASS |
| numpy 2.0.2 | ✅ PASS |
| scipy 1.13.1 | ✅ PASS |
| matplotlib 3.9.4 | ✅ PASS |
| 磁盘可用 352 GiB (61%) | ✅ PASS |
| 脚本文件存在 `scripts/09-olc-chiral-orf.py` | ✅ PASS |
| py_compile 语法检查 | ✅ PASS |
| 脚本可导入 (compute_orf_chiral, compute_orf_standard, arm_directions_3d 等) | ✅ PASS |
| 脚本可运行 (quick 模式) | ✅ PASS |

## 1-loop 阶段文件验证

| 文件 | 存在 | 内容状态 |
|------|------|---------|
| loop/1-loop/01-任务澄清.md | ✅ | 方向 A 选择，填补 7.2.2 节空白 |
| loop/1-loop/02-目标澄清.md | ✅ | 8 项判定标准，3 项硬约束 |
| loop/1-loop/03-任务分解.md | ✅ | M1-M5 DAG |
| loop/1-loop/04-信息搜集.md | ✅ | 7 个信息源 |
| loop/1-loop/05-完备核验.md | ✅ | Gap 分析，置信度 0.71 |
| loop/1-loop/06-决策-Iteration5.md | ✅ | enter_2loop，P0 = 断言补充 |

## 备份状态

| 检查项 | 结果 |
|--------|------|
| loop/2-loop/ 目录存在 | ✅ |
| 2-loop 历史文件 (Iteration 3 遗留) | ⚠️ 存在但属上一轮 |
| 本次迭代专属备份 | 待 2-loop/02 执行 |

## 关键发现

### 1. 环境完全就绪
Python 3.9.6 + numpy 2.0.2 + scipy 1.13.1 + matplotlib 3.9.4 均可正常工作，无 OOM 风险。

### 2. 脚本运行发现：chiral ORF 对所有配置均为零
在 `quick` 模式下运行脚本，发现 `|Gamma^V| = 0` 对 **所有** dihedral 角度（包括非共面配置）均为零：
```
dihedral=0.0: |G^V|=0.000000
dihedral=22.5: |G^V|=0.000000
dihedral=45.0: |G^V|=0.000000
dihedral=60.0: |G^V|=0.000000
dihedral=90.0: |G^V|=0.000000
```

### 3. 根本原因定位
通过代码分析发现 `arm_directions_3d()` 返回的基方向 `u` 始终为 `(pi/4, 0)`（极坐标，z 轴附近），而测试代码和 `quick` 命令中检测器 1 的固定方向也是 `(pi/4, 0)`。当检测器 1 位于球坐标极点时：
- F_plus 关于源方向对称，F_cross 关于源方向反对称
- chiral 组合 `F1p*F2x - F1x*F2p` 在全天区积分中恒为零
- 这导致所有配置的 chiral ORF 都为零

### 4. 影响评估
- **代码逻辑正确性**：物理公式实现正确（共面零、自关联零均通过）
- **测试覆盖问题**：测试 2 和 `quick` 使用退化的极点几何，无法验证非共面非零响应
- **P0 断言补充后**：单调性断言可能因上述几何退化而无法验证（Gamma^V 恒为零）
- **2-loop/03 执行前需修复**：`arm_directions_3d` 的使用方式或测试代码中检测器方向的设定

## 进入 2-loop/02 的条件确认

| 条件 | 状态 | 说明 |
|------|------|------|
| 1-loop/06 决策存在且 enter_2loop=true | ✅ | `06-决策-Iteration5.md` |
| Python 环境就绪 | ✅ | 3.9.6 + numpy/scipy/matplotlib |
| 脚本语法正确 | ✅ | py_compile 通过 |
| 脚本可执行 | ✅ | quick 模式成功运行 |
| 任务包文件完整 | ✅ | 01-05 全部存在 |
| 磁盘空间充足 | ✅ | 352 GiB 可用 |
| P0 任务定义明确 | ✅ | 断言补充代码已给出 |

**结论：预检查通过 — 环境就绪，可进入 2-loop/02 备份阶段**

---

## 完成时间
last_completed_at: 2026-07-05

## 回滚
回滚到 1-loop/06-决策-Iteration5.md
