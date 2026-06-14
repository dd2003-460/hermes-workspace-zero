# 跨论文综合评审 — 迭代19

**来源**: 副脑质询
**评估范围**: Chimera, DistCat v5, S12-1, S17-1, S18-1 (5篇论文)

## 发现8项系统性问题

### P0: S17-1曲率符号错误
正曲率≠双曲几何。源文件已修复，需Mac重编。

### P1: 零交叉引用
5篇论文互不引用，在一个结构化研究计划中是系统性疏漏。
- S18-1的complexity matching与S1-1的search-exploitation变分原理相关
- S12-1的co-discovery可用S1-1的Critical Time Window解释
- Chimera的coexisting attractor对应统一框架Theorem 10 Phase III
- S17-1的JSD与信息几何Fisher-Rao距离有Amari等价性

### P1: "相变"术语不一致
4篇论文用"phase transition"但数学含义不同:
- S18-1: inflection point/crossover (有限系统非相变)
- S12-1: Heaviside step (证据与指数增长无法区分)
- Chimera: coexisting attractor (数学严谨)
- S17-1: curvature (与相变无关)

建议统一术语或明确定义。

### P1: 投稿策略缺失
无统一投稿策略。S12-1实证最强适合science of science期刊，Chimera适合nonlinear dynamics，S18-1需扩大实验规模。

### P2: 统一框架未运作
UNIFIED-FRAMEWORK的8个定理零引用。

### P2: 实证策略不一致
合成数据占4/5篇论文。

### P2: Chimera种子选择偏差
3个种子都来自chimera-producing seeds。

### P2: S12-1证据不足
指数增长拟合几乎一样好(R²=0.86 vs 0.96)。

## 建议优先级
1. 修复S17-1曲率 (P0) — 已完成
2. 统一"相变"术语 (P1)
3. 建立交叉引用网络 (P1)
4. 制定投稿策略 (P1)
