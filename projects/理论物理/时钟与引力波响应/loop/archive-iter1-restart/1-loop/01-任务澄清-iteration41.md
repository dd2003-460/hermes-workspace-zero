# 01-任务澄清 — Iteration 41

**状态**: completed
**输入**: iteration 40 FAILED, sub-brain critiques (a144309 + a6213d22), P0-1/P1-1/P2-1 understanding notes
**时间**: 2026-07-10

## 背景

迭代 40 因 Agent 基础设施问题（600s 超时）全部失败。三个分解任务 (P0-2/P1-2/P2-2) 未能完成。

子脑批评要点：
1. HIGH: 使用原始文献，而非 Agent 衍生笔记
2. HIGH: 扩展 Phase 4 审计至图片/表格/参考文献
3. MEDIUM: 收敛标准工件单一性问题
4. Agent 持续失败 — 需改变策略

## 迭代 41 目标

基于已有的理解材料 (P0-1/P1-1/P2-1) 和手征 ORF 解析框架 (P-chiral-orf-analytical)，完成以下目标：

### Primary: 验证手征 ORF 解析框架的正确性
- 用 P0-1 (Hu PRD) 的原始公式验证 P-chiral-orf-analytical 中的统一表达式
- 用 P2-1 (OLC) 的传输函数验证 sinc 留数计算
- 确认 Γ^V = 0 for 共面网络的解析证明是否完整

### Secondary: 修复已知局限
- 确认 Nishizawa 2009 的 chiral ORF 结果是否与我们的一致
- 补充 helicity 翻转对称性检查 (chi -> -chi, Gamma^V -> -Gamma^V)

## 收敛标准

- [ ] P-chiral-orf-analytical 中的统一表达式与 Hu PRD 原始公式一致
- [ ] sinc 留数计算与 Hu PRD 的留数方法等价
- [ ] Γ^V = 0 证明完整（共面条件下的三重标量积论证）
- [ ] Nishizawa 2009 chiral ORF 结果交叉验证（或通过/不通过记录）
- [ ] helicity 翻转对称性数值检查通过

## 策略调整

**针对迭代 40 的 Agent 失败问题：**

1. 每个子任务的 Agent 使用更简短的 prompt，明确时间限制
2. 任务范围缩小 — 只做验证，不做新的推导
3. 如果 Agent 仍然失败，Commander 直接完成验证报告（因为 Commander 已经有所有必要的输入）

## 并行策略

三个子任务互相独立，可并行派发。
