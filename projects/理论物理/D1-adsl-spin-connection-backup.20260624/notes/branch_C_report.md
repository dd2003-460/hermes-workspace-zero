# Branch C Report: σ symbolic solve

> Date: 2026-04-01 09:35

## Finding

将 σ 参数化为 9 个未知数（σ^a_b，a=0,1,2，b=0,1,2），联立 EOM2+EOM3 共 18 个方程。
SymPy solve 返回无解——系统 overdetermined 且 inconsistent。

σ=-κ 验证：EOM2[0] 残差 {(0,1): -2r/ℓ²}，EOM2[2] 残差 {(1,2): -2}。
（注：这是用 ε_{abc} 修正后的结果。）

## Interpretation

不存在满足 EOM2+EOM3 的常数系数 σ。可能原因：
1. σ 应为 r-dependent 函数（但 κ 本身就是 r-dependent 的，已包含）
2. EOM 的形式与我们实现的有差异
3. 论文的 σ=-κ 在某个我们未使用的规范/变换后才成立

## Next

- 需要检查 dr 符号约定（ingoing vs outgoing 的 e⁰ 中 dr 系数 +1 vs -1）
- 需要搜索 Fuentealba et al. 的其他 AdSL 论文确认约定
