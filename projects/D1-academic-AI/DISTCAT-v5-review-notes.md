# DistCat v5 Review Notes

## 编译状态
- 33 页, 466KB, 编译通过（仅 pdfTeX destination warning，不影响内容）

## 已知结构问题（需要在 arXiv 提交前修复）

### 1. 两个 misplaced bibliography 环境
- Line 759-765: 第一本参考文献（仅 1 项，出现在 Example 1 中间）
- Line 1157-1580: 第二本参考文献（16 项，出现在 Example 5 中间）
- 正确位置：应在全文末尾（Sec 9 Discussion 之后）

### 2. 重复的 Example 5 (EMRI)
- 第一个出现在 line 926: `\section{Example 5: EMRI Chaos as D26 Resonance Amplification}`
- 第二个出现在 line 1318: `\section{Example 5: EMRI Chaos as D26 Resonance Amplification}`
- 两个内容几乎相同（从 base structure 到 summary 全部重复）

### 3. 修复优先级
- Critical: 合并 bibliography 到正确位置
- Should-fix: 删除重复的 Example 5
- Nice-to-have: 统一 label 引用

## 作者确认时请检查
1. 上述结构问题是否已修复
2. 所有物理推导的准确性
3. DistCat v5 vs DistCat v4 的内容完整性

## 提交建议
- arXiv 类别: math.CT（首选）或 physics.comp-ph
- 关键词: 2-category, distance derivation, functorial QFT, gravitational waves, EMRI
