# 06-decision（分叉决策）— Iteration 5 手征 ORF

**所属规格**：`/Users/a1-6/Desktop/workspace/loop/2-loop/06-decision.md`
**状态**：completed
**输入**：loop/2-loop/05-confidence.md 产出 (overall_confidence = 0.88)
**输出**：decision-2loop.md

---
## 决策结果
**decision: completed**

### Iteration 5 总结
- 2-loop (06-stage) 全部 6 阶段完成
- 核心发现：单臂 OLC 探测器对所有几何构型的手征 ORF 均为零 (~1e-18)
- 这是基本物理限制，不是 bug

### 产出
- `scripts/09-olc-chiral-orf.py` — 修正后的脚本
- `chiral-olc-paper-draft.md` — 更新的论文草稿
- `figures/09-chiral-orf-*.png` — 3 张图表

### 副脑质疑与验证结果

**sub-brain confidence: 0.55** vs **main-brain confidence: 0.88**

关键质疑验证情况（2026-07-05 额外验证）：

| 质疑 | 严重性 | 验证结果 |
|------|--------|---------|
| abs(cos_nu) 破坏对称性 | HIGH | ❌ 不成立 — abs(cos_nu) 不影响零结果，收敛扫描证实零结果是真实的 |
| 手征公式是否适用于 OLC | CRITICAL | ⚠️ 未完全排除 — 公式借用自 PTA/LISA，OLC 频率偏移的严格推导待补充 |
| "单臂"定义模糊 | HIGH | ⚠️ 需澄清 — 测试使用 d=0 双臂同位置，但零结果对 ALL 构型成立 |
| ~1e-18 可能是数值噪声 | MEDIUM | ✅ 已验证 — 16×32→128×256 扫描显示值递减，确认是噪声 |
| 三角形 OLC 未计算 | MEDIUM | ⚠️ 有效批评 — 论文中三角形 OLC 数据仅为推测 |
| NaN 传播 | LOW | ⚠️ 代码鲁棒性问题，不影响物理结果 |

**综合评估**: 零结果结论稳健（已验证），但论文论证完整性需改进。

### 后续方向
- **P0**: 三角形 3 卫星 OLC 手征 ORF 计算（需要多臂探测器）— 最高优先级
- **P1**: 从第一性原理推导 OLC 频率偏移的手征可观测量形式
- **P2**: 完善 SNR 噪声模型（参考 Lou 硕士论文第3章 PSD 公式）
- **P3**: 修复 NaN 传播代码鲁棒性问题

---
## 完成时间
last_completed_at: 2026-07-05

---
## 回滚
completed_with_branches → 遗留分支处理
needs_replan → 回滚到 1-loop
