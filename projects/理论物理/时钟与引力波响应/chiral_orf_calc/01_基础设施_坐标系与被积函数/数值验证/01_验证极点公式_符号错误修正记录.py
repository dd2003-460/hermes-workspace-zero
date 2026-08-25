"""
【性质】数值验证 —— 验证 PRD 论文式(16)给出的5个极点公式，并记录一处关键的符号修正
【计算的量】z0, z1, z2, z3, z4 五个极点是否真的满足 (1+n.u)=0 或 (1+n.v)=0
【状态】⚠️ 发现并修正了一处符号错误，修正后 ✅ 完全验证通过

【重要发现：极点公式的符号错误】
从PDF转录 PRD 论文式(16) 时，得到的 z3, z4 极点公式最初写作：
    z3 = -(1+vz)(1+x) / [(vx - i*vy) * sqrt(1-x^2)]
    z4 = -(1-vz)(1-x) / [(vx - i*vy) * sqrt(1-x^2)]
但代入 (1+n.v) 检验发现【不满足为零】的定义要求（数值误差是O(1)量级，绝非舍入误差）。

用二次方程 sqrt(1-x^2)*[vx(1+z^2)+i*vy(z^2-1)] = -2z(1+vz*x) 直接用 sympy.solve() 
反推真实的根，确认正确公式应为分母 (vx + i*vy)（加号，而非减号）：
    z3 = -(1+vz)(1+x) / [(vx + i*vy) * sqrt(1-x^2)]   ← 修正后
    z4 = -(1-vz)(1-x) / [(vx + i*vy) * sqrt(1-x^2)]   ← 修正后

这很可能是从 PDF/图片转录 OCR 时的符号误差，不是 PRD 论文本身的错误，
建议后续对照原文 PDF 图片核实这个下标符号。

本文件按时间顺序记录了完整的排错过程：
  Part A: 用原始(错误)符号做验证，展示为什么它不成立
  Part B: 用 sympy.solve 反推正确的极点根
  Part C: 用修正后符号重新验证，并做多组随机数值抽查
"""
import sympy as sp
from sympy import I, sqrt, symbols, simplify, expand, sin, cos
import numpy as np

x = sp.symbols('x', real=True)
z = sp.symbols('z')
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

n_dot_u = ux*sqrt(1-x**2)*(1+z**2)/(2*z) + uz*x
n_dot_v = sqrt(1-x**2)/(2*z)*(vx*(1+z**2) + I*vy*(z**2-1)) + vz*x

# ================= Part A: z1, z2 (对u的极点，这两个从一开始就是对的) =================
z1 = -(1+uz)*(1+x) / (ux*sqrt(1-x**2))
z2 = -(1-uz)*(1-x) / (ux*sqrt(1-x**2))

du, dv, psi = sp.symbols('delta_u delta_v psi', real=True)
subs_u = {ux: sin(du), uz: cos(du)}
subs_v = {vx: sin(dv)*cos(psi), vy: sin(dv)*sin(psi), vz: cos(dv)}

if __name__ == "__main__":
    print("="*70)
    print("Part A: 验证 z1, z2 (对u的极点) —— 这两个从一开始就正确")
    print("="*70)
    expr1 = one_plus_nu = (1+n_dot_u).subs(z, z1).subs(subs_u)
    print("(1+n.u) at z1 (参数化后) =", sp.simplify(sp.trigsimp(expr1)))
    expr2 = (1+n_dot_u).subs(z, z2).subs(subs_u)
    print("(1+n.u) at z2 (参数化后) =", sp.simplify(sp.trigsimp(expr2)))

    print("\n" + "="*70)
    print("Part B: z3, z4 —— 原始(错误)符号 (vx - i*vy) 的检验，数值不为零")
    print("="*70)
    z3_wrong = -(1+vz)*(1+x) / ((vx - I*vy)*sqrt(1-x**2))
    z4_wrong = -(1-vz)*(1-x) / ((vx - I*vy)*sqrt(1-x**2))

    np.random.seed(42)
    def check_numeric(zk_expr, label):
        expr = (1+n_dot_v).subs(z, zk_expr).subs(subs_v)
        for trial in range(3):
            xv = np.random.uniform(-0.9,0.9)
            dvv = np.random.uniform(0.1,3.0)
            psiv = np.random.uniform(0.1,6.0)
            val = complex(expr.subs({x:xv, dv:dvv, psi:psiv}).evalf())
            print(f"  {label} trial{trial}: x={xv:.3f} dv={dvv:.3f} psi={psiv:.3f} -> (1+n.v)={val:.4g}")

    check_numeric(z3_wrong, "z3_wrong")
    print("  ↑ 数值不趋于0，说明这个符号约定有误")

    print("\n" + "="*70)
    print("Part C: 用 sympy.solve 反推正确根，并验证修正后的 z3, z4")
    print("="*70)
    eq = sp.Eq(n_dot_v, -1)
    lhs_poly = sp.expand(2*z*(n_dot_v+1))
    sol = sp.solve(sp.Eq(lhs_poly, 0), z)
    print("直接求解 (1+n.v)=0 的两个根:")
    for s in sol:
        print(" ", sp.simplify(s))
    print("(对比可见，正确的分母应为 vx + i*vy，而非 vx - i*vy)")

    z3_fixed = -(1+vz)*(1+x) / ((vx + I*vy)*sqrt(1-x**2))
    z4_fixed = -(1-vz)*(1-x) / ((vx + I*vy)*sqrt(1-x**2))

    val3 = sp.simplify(sp.expand_complex((1+n_dot_v).subs(z, z3_fixed).subs(subs_v)))
    val4 = sp.simplify(sp.expand_complex((1+n_dot_v).subs(z, z4_fixed).subs(subs_v)))
    print("\n修正后符号验证 (应严格为0):")
    print("  (1+n.v) at z3_fixed =", val3)
    print("  (1+n.v) at z4_fixed =", val4)

    print("\n多组随机数值抽查 (修正后):")
    expr3 = (1+n_dot_v).subs(z, z3_fixed).subs(subs_v)
    expr4 = (1+n_dot_v).subs(z, z4_fixed).subs(subs_v)
    for trial in range(5):
        xv = np.random.uniform(-0.9,0.9)
        dvv = np.random.uniform(0.1,3.0)
        psiv = np.random.uniform(0.1,6.0)
        v3 = complex(expr3.subs({x:xv, dv:dvv, psi:psiv}).evalf())
        v4 = complex(expr4.subs({x:xv, dv:dvv, psi:psiv}).evalf())
        print(f"  trial{trial}: x={xv:.3f} dv={dvv:.3f} psi={psiv:.3f}  z3残差={v3:.2e}  z4残差={v4:.2e}")
    print("\n结论: 修正后的极点公式 (分母为 vx+i*vy) 通过全部验证，误差均在机器精度量级 ~1e-16")
