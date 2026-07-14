# 04-verify.md — P2/P3 验证

**所属阶段**：`/Users/a1-6/Desktop/workspace/loop/2-loop/04-verify.md`
**状态**：completed
**输入**：`loop/2-loop/03-execute.md`
**输出**：验证报告
**完成时间**：2026-07-13
**回滚**：回滚到 `archive-iter1-restart/2-loop/04-verify-iteration103.md`

---

## 验证清单

| V# | 验证项 | 结果 |
|----|--------|------|
| V1 | 代码可编译 | PASS |
| V2 | abs vs linear 对比测试 | PASS |
| V3 | Coplanar $\Gamma^V = 0$ | PASS |
| V4 | Non-coplanar $\Gamma^V \neq 0$ | PASS |
| V5 | P^V strict form equivalent | PASS |
| V6 | Helicity flip symmetry | PASS |
| V7 | P2-3 精确匹配（相对误差 < 0.1%） | PASS |
| V8 | PDF 编译通过（xelatex 51页） | PASS |
| V9 | P5 跨验证: 共面 $\Gamma^V = 0$ (对称性) | PASS |
| V10 | P5 跨验证: $b^V_0 = \frac{4}{5}(j_1 - j_3)$ (球谐积分) | PASS |
| V11 | P5 跨验证: $b^V_1 = \frac{4}{35} j_3$ (球谐积分) | PASS |
| V12 | P5 跨验证: 低频极限行为 $b^V_0 \propto \psi, b^V_1 \propto \psi^3$ | PASS |
| V13 | P5 跨验证: $j_1 - j_3$ 偶极-八极干涉物理诠释 | PASS |
| V14 | P5 跨验证: 与代码数值交叉验证 (量级一致) | PASS |

## 关键数值验证

- $R^V$ 频率独立性：比值 $R^V(f)/R^V(0.001) = 1.000000000000$（12 位小数）
- Sky-averaged $R^V = 8.178519\times 10^{-9}$，接近零
- Single-sky $|R^V|$ 约为 sky-avg 的 $10^6$ 倍
