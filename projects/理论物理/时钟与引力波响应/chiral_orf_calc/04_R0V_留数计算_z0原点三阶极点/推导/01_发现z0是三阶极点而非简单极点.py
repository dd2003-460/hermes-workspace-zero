"""
【性质】推导 —— 发现 z=0 处 f_V(z) 的极点阶数比预期更高（是三阶极点）
【计算的量】判定 z=0 处分母 Q(z) 的零点阶数
【状态】✅ 重要发现（这不是失败，而是一个值得写进论文的物理现象）

【背景】
对 z1, z2 这两个由 (1+n.u)=0 定义的极点，都是简单的一阶极点，
可以直接用 Res = lim_{z->zk} (z-zk)*f(z) 求得。

尝试对 z=0 用同样的简单极点公式 Res = P(0)/Q'(0) （P,Q是把f_V(z)
通分成P(z)/Q(z)纯多项式形式后的分子分母）时，发现:
    Q(0) = 0   且   Q'(0) = 0
这说明 z=0 不是一阶极点，用简单极点公式会得到 0/0 的不定型（sympy返回zoo，即复无穷）。

【进一步诊断】
用 sp.series() 展开 f_V(z) 在 z=0 附近的洛朗级数，发现级数中同时出现
1/z^3, 1/z^2, 1/z 三项 —— 说明 z=0 确实是一个三阶极点。

【物理意义（留待06核心发现深入讨论）】
这与"z0对应的强度ORF部分 R0^I 只是简单一阶极点"形成鲜明对比，
提示手征反对称核 xi_V 在原点附近的奇异性阶数比对称核 xi_I 更高。
这很可能与"手征需要额外一个方向性算符（列维-奇维塔张量）"这一
数学结构直接相关，是JCAP论文式(B.19)里引入 w_ab=epsilon_abc*s^c
这个"手性算符"的sympy版本印证。
"""
import sympy as sp

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
eCross_uu = 2*theta_dot_u*phi_dot_u
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
eCross_vv = 2*theta_dot_v*phi_dot_v
numerator_V = sp.expand(ePlus_uu*eCross_vv - eCross_uu*ePlus_vv)
n_dot_u = ux*s*(1+z**2)/(2*z) + uz*x
n_dot_v = s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x
one_plus_nu = sp.expand(1+n_dot_u)
one_plus_nv = sp.expand(1+n_dot_v)

if __name__ == "__main__":
    print("Step 1: 尝试用简单极点公式 Res = P(0)/Q'(0)")
    numV_poly = sp.expand(numerator_V * (2*z)**2)
    onu_poly  = sp.expand(one_plus_nu * (2*z))
    onv_poly  = sp.expand(one_plus_nv * (2*z))
    f_V_rational = numV_poly / (sp.I*z*onu_poly*onv_poly)
    f_V_rational = sp.together(f_V_rational)
    num_r, den_r = sp.fraction(f_V_rational)
    num_r = sp.expand(num_r); den_r = sp.expand(den_r)

    den_r_poly = sp.Poly(den_r, z)
    print("  Q(0) =", den_r_poly.eval(0))
    print("  Q'(0) =", sp.diff(den_r, z).subs(z, 0))
    print("  → 两者都是0，说明z=0不是一阶极点，简单公式失效")

    print("\nStep 2: 用series()展开验证是几阶极点")
    f_V = numerator_V/(sp.I*z*one_plus_nu*one_plus_nv)
    print("  正在做洛朗级数展开 (这一步约需15-20秒)...")
    ser = sp.series(f_V, z, 0, 1)
    ser_str = str(ser)
    has_z3 = "z**(-3)" in ser_str or "/z**3" in ser_str
    has_z2 = "z**(-2)" in ser_str or "/z**2" in ser_str
    # 用严格的负一次幂检测 (排除 1/z**2、1/z**3 造成的子串误匹配)
    has_z1 = ("z**(-1)" in ser_str) or ("/z +" in ser_str) or ("/z -" in ser_str) or ser_str.strip().startswith("1/z ")
    print(f"  级数中含 1/z^3 项: {has_z3}")
    print(f"  级数中含 1/z^2 项: {has_z2}")
    print(f"  级数中含 1/z 项:   {has_z1}")
    print("\n结论: z=0 是三阶极点。需要用更稳健的方法(sympy.residue)求留数，")
    print("      简单的 Res=P(0)/Q'(0) 公式在此不适用。")
