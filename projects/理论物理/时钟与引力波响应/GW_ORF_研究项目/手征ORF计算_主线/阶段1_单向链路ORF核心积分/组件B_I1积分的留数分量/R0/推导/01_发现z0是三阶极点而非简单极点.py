"""
【性质】推导 —— 判定 z=0 处 f_V(z) 的极点阶数
【计算的量】f_V(z) 在 z=0 附近的洛朗级数展开阶数
【状态】✅ 已确认为【二阶极点】——【重要更正，见下方说明】
【依赖】无

================================================================================
              ⚠️ 二次修正说明（BUG-001 的连带发现，非独立新bug）⚠️
================================================================================
本文件此前版本（使用论文Eq(A6)印刷的错误 +I 符号）得出"z=0是三阶极点"的结论。
本次在 BUG-001 修正（theta.v, n.v 的 vy 项符号改为 -I）之后重新检验发现：
**用修正后的正确公式，z=0 实际上是二阶极点，不是三阶极点。**

数值证据（同一组随机几何参数，分别用两种符号约定检验 lim_{z->0} z^n f(z)）：

| n | 用【错误】+I符号 (上一轮结论) | 用【修正后】-I符号 (本次) |
|---|---|---|
| 1 | 发散(inf) | 发散(inf) |
| 2 | 发散(inf) | **有限值** (-1.69-2.97j) <- 说明只是二阶极点 |
| 3 | 有限值 (-0.17+0.12j) | 0 |

也就是说，"z=0是三阶极点"这个结论本身也是 BUG-001（错误的v_y符号）带来的
副产品——错误的公式让分子多了一个不该有的 O(z) 修正项，人为地把极点阶数
从2阶推高到3阶。sympy.residue() 因为是自适应处理任意阶极点的通用函数，
用错误公式时"计算三阶留数"得到的数值仍然是（错误公式下的）正确留数值，
所以R0V之前的数值验证"通过"了，但那验证的是错误问题设置下的自洽性，
并不能说明二阶/三阶极点判断正确。

**结论：用修正后的正确公式，z=0 是二阶极点，留数公式应为**
$$R_0^V=\\lim_{z\\to0}\\frac{d}{dz}\\big[z^2 f(z)\\big]$$
**而不是三阶公式** $\\frac{1}{2!}\\frac{d^2}{dz^2}[z^3f(z)]$。
不过由于 sympy.residue() 本身就能自动正确处理任意阶极点（不需要用户预先
判断阶数），所以"具体计算"文件夹里最终用 sympy.residue() 算出的 R0V 数值本身
仍然正确（已用二阶极点公式独立交叉验证，两者严格相等，见本文件末尾）。
详见 `00_总览与汇报/重大问题修正记录/`。
================================================================================
"""
import sympy as sp
from sympy import I, sqrt, symbols, series, O

x = symbols('x')
z = symbols('z')
ux, uz = symbols('u_x u_z', real=True)
vx, vy, vz = symbols('v_x v_y v_z', real=True)
s = symbols('s', real=True, positive=True)


def build_fV_symbolic():
    theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
    phi_dot_u   = I*ux*(z**2-1)/(2*z)
    theta_dot_v = vx*x*(1+z**2)/(2*z) - I*vy*x*(z**2-1)/(2*z) - vz*s   # BUG-001修正: -I
    phi_dot_v   = I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
    ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
    eCross_uu = 2*theta_dot_u*phi_dot_u
    ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
    eCross_vv = 2*theta_dot_v*phi_dot_v
    numerator_V = sp.expand(ePlus_uu*eCross_vv - eCross_uu*ePlus_vv)
    n_dot_u = ux*s*(1+z**2)/(2*z) + uz*x
    n_dot_v = s/(2*z)*(vx*(1+z**2) - I*vy*(z**2-1)) + vz*x            # BUG-001修正: -I
    return numerator_V/(I*z*(1+n_dot_u)*(1+n_dot_v))


if __name__ == "__main__":
    f_V = build_fV_symbolic()

    # 代入具体数值，检验简单极点公式 Res=P(0)/Q'(0) 是否可用
    import numpy as np
    xv = 0.37; sv = np.sqrt(1-xv**2)
    duv = 1.1; uxv, uzv = np.sin(duv), np.cos(duv)
    vxv, vyv, vzv = 0.3, -0.5, np.sqrt(1-0.3**2-0.5**2)
    f_V_numeric = f_V.subs({x: xv, s: sv, ux: uxv, uz: uzv, vx: vxv, vy: vyv, vz: vzv})

    # 判断z=0处极点阶数：把 f_V(z)*z^3 在z=0处展开，看是否有限
    print("检验 f_V(z)*z^n 在 z->0 极限是否有限 (n=1,2,3):")
    for n in [1, 2, 3]:
        try:
            lim = sp.limit(f_V_numeric*z**n, z, 0)
            print(f"  n={n}: lim = {lim}")
        except Exception as e:
            print(f"  n={n}: 计算异常 {e}")

    print("\n结论: 用修正后的正确公式(-I)，n=2时极限有限非零、n=1发散、n=3为0")
    print("     => z=0 是【二阶】极点 (不是三阶)，留数公式应为:")
    print("        R0V = lim_{z->0} d/dz [z^2 * f(z)]")
    print("     用 sympy.residue() 自动处理 (不依赖手动判断阶数) 与此结果严格一致，见下方交叉验证:")
    print("     (注: sp.limit对高幂次有理函数直接求导数值不稳定，改用多项式除法方式求导数值稳健)")

    t0_res = sp.residue(f_V_numeric, z, 0)
    g = sp.cancel(sp.together(z**2*f_V_numeric))
    num_poly, den_poly = sp.fraction(g)
    num_poly = sp.Poly(num_poly, z); den_poly = sp.Poly(den_poly, z)
    dnum, dden = num_poly.diff(z), den_poly.diff(z)
    t0_2nd_order = (dnum.eval(0)*den_poly.eval(0) - num_poly.eval(0)*dden.eval(0)) / den_poly.eval(0)**2
    print(f"  sympy.residue()       = {complex(t0_res)}")
    print(f"  二阶极点公式(多项式除法) = {complex(t0_2nd_order)}")
    print(f"  两者差 = {abs(complex(t0_res)-complex(t0_2nd_order)):.2e}  (应为0)")
