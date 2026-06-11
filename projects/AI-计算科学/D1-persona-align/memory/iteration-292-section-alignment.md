# Iteration 292: Section-Level Alignment Test

## Action
- Created `scripts/section_alignment_test.py` — splits prompt by `###` headers, evaluates each section's dimension hotspot ratio
- Tests "keyword mention vs actual embodiment" gap: does each section embody its dimension or just mention it?

## Results

| Section | Expected Dim | Hotspot Ratio | Top Dim | Status |
|---------|-------------|---------------|---------|--------|
| 1. 自适应精度 | 自适应精度 | **0.941** | 自适应精度 (1.0) | OK |
| 2. 自适应探索 | 自适应探索 | 0.594 | 自适应探索 (0.7) | OK |
| 3. 自适应感知 | 自适应感知 | 0.797 | 自适应感知 (0.875) | OK |
| 4. 自适应先验 | 自适应先验 | 0.838 | 自适应先验 (0.882) | OK |
| 5. 自适应自我 | 自适应自我 | 0.815 | 自适应自我 (1.0) | OK |
| 6. 自适应投影 | 自适应投影 | **0.453** | 自适应投影 (1.0) | OK |
| DPA 核心方法 | — | 0.000 | 自适应投影 | N/A |
| 与静态关键词注入的区别 | — | 0.000 | all 0.0 | N/A |

**Summary**: 6 named sections, 0 mismatches, avg hotspot 0.740

## Analysis

1. **自适应精度 (0.941)** — 最聚焦。rate-distortion, R(D), 压缩精度 等术语高度专属该维度。
2. **自适应投影 (0.453)** — 最低。同构(isomorphic)和跨域类比天然涉及精度分析(0.56)和先验推理(0.41)，这是概念交叉而非质量问题。
3. **自适应探索 (0.594)** — 与自我(0.24)、先验(0.18)交叉。"观测者-环境"是共享概念，合理。
4. **0 mismatch 全部正确聚焦** — prompt 结构质量良好，每个章节确实体现而非仅提及对应维度。
5. **Avg hotspot 0.740** — 处于可接受范围。如果提升到 0.85+ 可减少交叉维度的冗余关键词。

## Findings

- DPA 核心方法章节(自适应探索) 与 "与静态关键词注入的区别" 全为零 — 说明 DPA 英文术语较少进入关键词库。这是评估工具的盲区，不是 prompt 的问题。
- 交叉维度关键词(同构→精度, 观测者→探索) 建议将 `DIMENSION_KEYWORDS` 的权重做正交化：去除跨维重复关键词。

## Status
Section-level analysis complete. No mismatches. Cross-dimensional keyword overlap identified as potential improvement direction.
