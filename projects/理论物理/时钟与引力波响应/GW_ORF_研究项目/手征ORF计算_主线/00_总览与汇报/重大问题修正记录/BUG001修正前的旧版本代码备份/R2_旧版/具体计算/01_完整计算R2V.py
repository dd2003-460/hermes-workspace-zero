"""
【性质】具体计算 —— 完整计算 R2^V (z=z2 的留数)，方法与 R1V 完全平行
【计算的量】R2^V = Res_{z=z2} f_V(z)
【状态】✅ 成功，一次性通过（未再出现类似R1V的符号错误，因为吸取了教训用直接相减而非猜测符号）

【与R1V计算的对比】
z2 = -(1-uz)(1-x) / (ux*s) 对应 n_hat = +u_hat 方向（z1对应n_hat=-u_hat方向）。
方法完全复用02文件夹的"逐个内积化简再组装"策略。

【一个有趣的观察，留待06文件夹详细展开】
在 z2 处，phi.u / theta.u 的比值是 -i （而在z1处是 +i，正好反号）。
这个符号翻转直接导致了 R2^V = +i * R2^I （而 R1^V = -i * R1^I），
物理上对应"z1,z2代表同一条链路两个相反传播方向，手性作为赝标量在方向反转下变号"。
"""
import sympy as sp
import time
import pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

z2 = -(1-uz)*(1-x) / (ux*s)

theta_dot_u_expr = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u_expr   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v_expr = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v_expr   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)


def sub_reduce(expr, zk):
    """标准化简流程：代入极点->通分->展开->约束降幂->cancel（与02文件夹方法一致）"""
    val = sp.together(expr.subs(z, zk))
    num, den = sp.fraction(val)
    num = sp.expand(num); den = sp.expand(den)
    for _ in range(6):
        num = sp.expand(num.subs(ux**2, 1-uz**2)); den = sp.expand(den.subs(ux**2, 1-uz**2))
    for _ in range(6):
        num = sp.expand(num.subs(s**2, 1-x**2)); den = sp.expand(den.subs(s**2, 1-x**2))
    return sp.cancel(num/den)


if __name__ == "__main__":
    t0 = time.time()
    tdu2 = sub_reduce(theta_dot_u_expr, z2)
    pdu2 = sub_reduce(phi_dot_u_expr, z2)
    tdv2 = sub_reduce(theta_dot_v_expr, z2)
    pdv2 = sub_reduce(phi_dot_v_expr, z2)
    print("z2 内积化简完成:", time.time()-t0, "s")
    print("theta.u|z2 =", tdu2)
    print("phi.u|z2   =", pdu2)
    print("phi.u/theta.u at z2 =", sp.simplify(pdu2/tdu2), "  (对照z1处是+i，这里是-i)")

    ePlus_uu2  = sp.expand(tdu2**2 - pdu2**2)
    eCross_uu2 = sp.expand(2*tdu2*pdu2)
    ePlus_vv2  = sp.expand(tdv2**2 - pdv2**2)
    eCross_vv2 = sp.expand(2*tdv2*pdv2)

    numV_z2 = sp.expand(ePlus_uu2*eCross_vv2 - eCross_uu2*ePlus_vv2)
    numV_z2_t = sp.together(numV_z2)
    num2, den2 = sp.fraction(numV_z2_t)
    num2 = sp.expand(num2); den2 = sp.expand(den2)
    for _ in range(6):
        num2 = sp.expand(num2.subs(ux**2, 1-uz**2)); den2 = sp.expand(den2.subs(ux**2, 1-uz**2))
    for _ in range(6):
        num2 = sp.expand(num2.subs(s**2, 1-x**2)); den2 = sp.expand(den2.subs(s**2, 1-x**2))
    print("\nnumerator_V(z2) 分母 =", den2)

    onv_z2 = sub_reduce(s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x + 1, z2)
    print("one_plus_nv(z2) =", onv_z2)

    # z2-z1 = -(z1-z2) = -(-2(uz+x)/(ux*s)) = 2(uz+x)/(ux*s)
    z2_minus_z1 = 2*(uz+x)/(ux*s)
    R2V_expr = (num2/den2 * 2) / (sp.I * ux*s * z2_minus_z1 * onv_z2)

    with open('R2V_expr.pkl', 'wb') as f:
        pickle.dump(R2V_expr, f)
    print("\nR2^V 计算完成，已保存 R2V_expr.pkl")
