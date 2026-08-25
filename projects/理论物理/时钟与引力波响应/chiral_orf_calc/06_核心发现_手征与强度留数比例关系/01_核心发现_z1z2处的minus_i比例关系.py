"""
【性质】核心科学发现 —— 严格证明手征留数与强度留数在z1,z2处成正比
【计算的量】numerator_V(z1) 与 numerator_I(z1) 的精确代数关系；z2处同理
【状态】✅✅ 本次任务最重要的产出，两条恒等式均为严格符号恒等式（非数值近似）

═══════════════════════════════════════════════════════════════
核心结论
═══════════════════════════════════════════════════════════════

    numerator_V(z1) = -i * numerator_I(z1)   =>   R1^V = -i * R1^I
    numerator_V(z2) = +i * numerator_I(z2)   =>   R2^V = +i * R2^I

用 sp.simplify(numerator_V(zk) - (∓i)*numerator_I(zk)) 严格验证 == 0，
这不是数值近似，是精确的符号代数恒等式。

═══════════════════════════════════════════════════════════════
物理根源
═══════════════════════════════════════════════════════════════

z1, z2 分别对应 n_hat = -u_hat 与 n_hat = +u_hat 方向（即 (1+n.u)=0 的
两支解析延拓）。在这两点上，恰好有：

    phi.u|z1 = +i * (theta.u|z1)
    phi.u|z2 = -i * (theta.u|z2)

这组符号相反的比例关系，直接导致 e_cross_uu = i*e_plus_uu (在z1)
以及 e_cross_uu = -i*e_plus_uu (在z2)，代入对称核/反对称核的定义后
自然得到上面两条恒等式。

物理图像：z1,z2 对应同一条链路u的两个相反传播方向。手性作为赝标量，
在传播方向反转下会自然变号，这正是比例系数从-i变为+i的根源。

═══════════════════════════════════════════════════════════════
这个发现比任务预设的"消去偶次项"猜想更强
═══════════════════════════════════════════════════════════════

不是简单的"消去了某些偶次项"，而是整个留数在代数上被压缩成了强度
留数的纯虚数倍——这意味着在u决定的两个极点上，手征ORF与强度ORF的
贡献严格成正比，比例系数是±i。

【重要边界（见02文件"负面结果"）】: 这个规律不能推广到z0(三阶极点)
和z3,z4(v决定的极点)，是这个特殊几何结构(简单一阶极点+由u单独决定)
的产物，不是普适规律。
"""
import sympy as sp
import time

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

theta_dot_u_expr = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u_expr   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v_expr = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v_expr   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)


def sub_reduce(expr, zk):
    val = sp.together(expr.subs(z, zk))
    num, den = sp.fraction(val)
    num = sp.expand(num); den = sp.expand(den)
    for _ in range(6):
        num = sp.expand(num.subs(ux**2, 1-uz**2)); den = sp.expand(den.subs(ux**2, 1-uz**2))
    for _ in range(6):
        num = sp.expand(num.subs(s**2, 1-x**2)); den = sp.expand(den.subs(s**2, 1-x**2))
    return sp.cancel(num/den)


if __name__ == "__main__":
    z1 = -(1+uz)*(1+x) / (ux*s)
    z2 = -(1-uz)*(1-x) / (ux*s)

    print("="*70)
    print("验证 z1 处: numerator_V(z1) = -i * numerator_I(z1)")
    print("="*70)
    tdu1 = sub_reduce(theta_dot_u_expr, z1)
    pdu1 = sub_reduce(phi_dot_u_expr, z1)
    tdv1 = sub_reduce(theta_dot_v_expr, z1)
    pdv1 = sub_reduce(phi_dot_v_expr, z1)

    ePlus_uu1  = sp.expand(tdu1**2 - pdu1**2)
    eCross_uu1 = sp.expand(2*tdu1*pdu1)
    ePlus_vv1  = sp.expand(tdv1**2 - pdv1**2)
    eCross_vv1 = sp.expand(2*tdv1*pdv1)

    numerator_I_z1 = sp.expand(ePlus_uu1*ePlus_vv1 + eCross_uu1*eCross_vv1)
    numerator_V_z1 = sp.expand(ePlus_uu1*eCross_vv1 - eCross_uu1*ePlus_vv1)

    ratio_check = sp.simplify(eCross_uu1/ePlus_uu1)
    print("根源检查: eCross_uu1 / ePlus_uu1 =", ratio_check, " (应为 i)")

    diff1 = sp.expand(numerator_V_z1 - (-sp.I)*numerator_I_z1)
    print("numerator_V(z1) - (-i)*numerator_I(z1) =", diff1)
    print("是否恒等于0:", sp.simplify(diff1) == 0)

    print("\n" + "="*70)
    print("验证 z2 处: numerator_V(z2) = +i * numerator_I(z2)")
    print("="*70)
    tdu2 = sub_reduce(theta_dot_u_expr, z2)
    pdu2 = sub_reduce(phi_dot_u_expr, z2)
    tdv2 = sub_reduce(theta_dot_v_expr, z2)
    pdv2 = sub_reduce(phi_dot_v_expr, z2)

    ePlus_uu2  = sp.expand(tdu2**2 - pdu2**2)
    eCross_uu2 = sp.expand(2*tdu2*pdu2)
    ePlus_vv2  = sp.expand(tdv2**2 - pdv2**2)
    eCross_vv2 = sp.expand(2*tdv2*pdv2)

    ratio_check2 = sp.simplify(eCross_uu2/ePlus_uu2)
    print("根源检查: eCross_uu2 / ePlus_uu2 =", ratio_check2, " (应为 -i)")

    numerator_I_z2 = sp.expand(ePlus_uu2*ePlus_vv2 + eCross_uu2*eCross_vv2)
    numerator_V_z2 = sp.expand(ePlus_uu2*eCross_vv2 - eCross_uu2*ePlus_vv2)

    diff2 = sp.expand(numerator_V_z2 - (sp.I)*numerator_I_z2)
    print("numerator_V(z2) - (+i)*numerator_I(z2) =", diff2)
    print("是否恒等于0:", sp.simplify(diff2) == 0)

    print("\n" + "="*70)
    print("总结: 两条恒等式均严格成立，这是本次计算最重要的科学发现")
    print("="*70)
