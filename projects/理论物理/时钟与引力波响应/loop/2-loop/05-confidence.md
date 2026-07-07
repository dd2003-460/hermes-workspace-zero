# 05-confidence（置信度检查）— Iteration 5 手征 ORF

**所属规格**：`/Users/a1-6/Desktop/workspace/loop/2-loop/05-confidence.md`
**状态**：completed
**输入**：loop/2-loop/03-execute.md 产出 + scripts/09-olc-chiral-orf.py 直接审查
**输出**：confidence report

---

## 产出内容

### 置信度评估

| 方面 | 置信度 | 说明 |
|------|--------|------|
| 公式正确性 | 1.00 | `F_+1*F_×2 - F_×1*F_+2` 是 Kato & Soda (2016) 标准奇宇称组合，代码实现与论文公式完全一致 |
| 物理合理性 | 1.00 | 单臂 OLC 对所有构型 null result (~1e-18) 与 Kato & Soda 2016、Orlando 2021 的多臂必要性结论一致；单臂标量可观测量的本质导致手征通道消失，这是深刻的物理洞察而非bug |
| 代码正确性 | 0.95 | 三个验证测试全部通过；`f`→`fw` 命名冲突已修复，`pcolormesh` 维度已修复，探测器方向 fix 已加入；`n_orient=16` 用于测试收敛性，生产分析用 `n_orient=12`/`24`，收敛验证存在但未做系统收敛研究 |
| 论文准确性 | 0.90 | 论文草稿正确报告 null result，与 Kato & Soda 2016、Orlando et al. 2021、Hu PRD 2025 引用正确，§2.4 新增单臂零结果定理；但 SNR 公式未从噪声 PSD 正确转换到应变单位（`P_i(f)` 的定义与 OLC 实际噪声谱的关系未详细推导） |
| 验证覆盖 | 0.80 | 04-verify.md 文件存在但实际是 M1（混合网络迭代）的验证，非 Iteration 5 手征 ORF 的独立验证；手征 ORF 工作从 03-execute 直接推进到本步，缺少专门的 04-verify 报告 |

### 综合置信度
**overall_confidence = 0.88**

### 不确定性来源
1. **缺失独立验证报告**：04-verify.md 内容为 M1 混合网络迭代（2026-07-01），Iteration 5 手征 ORF 工作（2026-07-05）无对应独立验证文件，置信度评估基于直接审查代码而非验证报告。
2. **收敛性未系统研究**：测试使用 `n_orient=16`，生产分析使用 `n_orient=12`/`24`，代码注释称 "N_theta=32, N_phi=64 sufficient for <1% accuracy"，但未提供收敛性扫描证明该估计。
3. **SNR 噪声转换未充分推导**：论文草稿中 `P_i(f)` 作为"noise PSD converted to equivalent strain units"表述模糊，OLC 的实际噪声谱形式与标准应变噪声谱之间的转换关系未显式给出。
4. **`u1_th, u1_ph = (pi/3, pi/6)` 修复的回归测试**：代码中将探测器1方向从 `(pi/4, 0)`（与 `arm_directions_3d` 的默认 base 相同）修复为 `(pi/3, pi/6)`，此修复已验证且测试通过，但原始 bug 的具体触发场景未在 commit 记录中追溯。

### 改进建议
- **为 Iteration 5 补充独立 04-verify.md**：记录手征 ORF 专门验证项（公式审查、null result 物理解释、测试覆盖度），避免与 M1 验证混淆。
- **添加收敛性扫描**：在 `analyze_chiral_frequency_dependence` 中加入 `n_orient=[8, 16, 24, 32]` 扫描，证明 `<1%` 精度估计。
- **完善 SNR 噪声模型**：将 `P_i(f)` 替换为实际的 OLC 位移噪声/时钟噪声 PSD 公式（参考 Lou 硕士论文第3章），建立与 Hu PRD 噪声框架的连接。
- **追溯 `f`→`fw` bug 来源**：该 bug 说明 `write_paper` 函数最初使用 `f` 作为文件句柄，在外部循环中 `f` 被赋值为频率浮点数后引发 `AttributeError`，建议审查代码库中是否存在类似命名冲突。

---

## 完成时间
last_completed_at: 2026-07-05
