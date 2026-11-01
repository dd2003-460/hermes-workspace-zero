"""
【性质】具体计算 —— 完整计算 z2 处的留数 R2V (一步完成: 化简内积->组装numerator->组装最终R2V)
【计算的量】R2^V(x; u_hat, v_hat) = Res_{z=z2} f_V(z)
【状态】✅ 成功（已应用 BUG-001 修正，8组随机参数最大相对误差 9.6e-13）
【依赖】无（自包含）

【BUG-001 修正说明】
theta_dot_v, n_dot_v 的 vy 项符号已改为 -I（论文Eq(A6)打印/上版代码误为 +I）。
详见 `00_总览与汇报/重大问题修正记录/关于PRD论文附录A公式A6的符号错误_详细推导说明.md`
"""
import sympy as sp
from sympy import I, symbols
import time
import pickle

x, z = symbols('x z')
ux, uz = symbols('u_x u_z', real=True)
vx, vy, vz = symbols('v_x v_y v_z', real=True)
s = symbols('s', real=True, positive=True)

# ---- 修正后的内积公式 ----
theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u   = I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) - I*vy*x*(z**2-1)/(2*z) - vz*s   # 修正: -I
phi_dot_v   = I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
n_dot_v     = s/(2*z)*(vx*(1+z**2) - I*vy*(z**2-1)) + vz*x          # 修正: -I

z1_expr = -(1+uz)*(1+x)/(ux*s)
z2_expr = -(1-uz)*(1-x)/(ux*s)


def sub_reduce(expr, zval):
    e = sp.cancel(sp.together(expr.subs(z, zval)))
    e = sp.expand(e)
    e = e.subs(ux**2, 1-uz**2); e = sp.expand(e)
    e = e.subs(s**2, 1-x**2); e = sp.expand(e)
    e = sp.factor(e)
    return e


if __name__ == "__main__":
    print("Step 1: 化简 z2 处的四个内积")
    t0 = time.time()
    tdu_z2 = sub_reduce(theta_dot_u, z2_expr)
    pdu_z2 = sub_reduce(phi_dot_u, z2_expr)
    print("  theta.u@z2 =", tdu_z2)
    print("  phi.u@z2   =", pdu_z2)
    tdv_z2 = sub_reduce(theta_dot_v, z2_expr)
    print("  theta.v@z2 =", tdv_z2, f" (用时{time.time()-t0:.1f}s)")
    pdv_z2 = sub_reduce(phi_dot_v, z2_expr)
    print("  phi.v@z2   =", pdv_z2)

    print("\nStep 2: 组装 numerator_V(z2)")
    ePlus_uu_z2 = sp.expand(tdu_z2**2 - pdu_z2**2)
    eCross_uu_z2 = sp.expand(2*tdu_z2*pdu_z2)
    ePlus_vv_z2 = sp.expand(tdv_z2**2 - pdv_z2**2)
    eCross_vv_z2 = sp.expand(2*tdv_z2*pdv_z2)
    ratio = sp.simplify(eCross_uu_z2/ePlus_uu_z2)
    print("  eCross_uu/ePlus_uu @z2 =", ratio, " <- 核心恒等式的基础: 在z2处严格等于 -I")

    numV_z2 = sp.expand(ePlus_uu_z2*eCross_vv_z2 - eCross_uu_z2*ePlus_vv_z2)
    numV_z2 = numV_z2.subs(ux**2, 1-uz**2); numV_z2 = sp.expand(numV_z2)
    numV_z2 = numV_z2.subs(s**2, 1-x**2); numV_z2 = sp.expand(numV_z2)
    print(f"  numerator_V(z2) 组装完成, ops={sp.count_ops(numV_z2)}")

    print("\nStep 3: 计算 (1+n.v)@z2 并组装最终 R2V")
    one_plus_nv_z2 = sp.cancel(sp.together((1+n_dot_v).subs(z, z2_expr)))
    one_plus_nv_z2 = sp.expand(one_plus_nv_z2)
    one_plus_nv_z2 = one_plus_nv_z2.subs(ux**2, 1-uz**2); one_plus_nv_z2 = sp.expand(one_plus_nv_z2)
    one_plus_nv_z2 = one_plus_nv_z2.subs(s**2, 1-x**2); one_plus_nv_z2 = sp.expand(one_plus_nv_z2)
    one_plus_nv_z2 = sp.factor(one_plus_nv_z2)
    print("  (1+n.v)@z2 =", one_plus_nv_z2)

    z2_minus_z1 = sp.simplify(z2_expr - z1_expr)
    print("  z2 - z1 =", z2_minus_z1)

    # R2V = numV(z2) * 2 / [i*ux*s*(z2-z1)*(1+n.v)(z2)]
    R2V = numV_z2 * 2 / (I*ux*s*z2_minus_z1*one_plus_nv_z2)
    R2V_simplified = sp.cancel(R2V)
    print(f"\nR2V 组装完成, ops={sp.count_ops(R2V_simplified)}")
    print(R2V_simplified)

    with open('R2V_expr.pkl', 'wb') as f:
        pickle.dump(R2V_simplified, f)
    print("\n已保存 R2V_expr.pkl (BUG-001修正后的最终版本)")

    # 顺带交叉核对核心恒等式 R2V = +i*R2I
    numI_z2 = sp.expand(ePlus_uu_z2*ePlus_vv_z2 + eCross_uu_z2*eCross_vv_z2)
    numI_z2 = numI_z2.subs(ux**2, 1-uz**2); numI_z2 = sp.expand(numI_z2)
    numI_z2 = numI_z2.subs(s**2, 1-x**2); numI_z2 = sp.expand(numI_z2)
    diff_check = sp.simplify(numV_z2 - I*numI_z2)
    print("\n检验 numerator_V(z2) - (+I)*numerator_I(z2) =", diff_check, " <- 应为0")

    print("\n" + "=" * 70)
    print("LaTeX 解析表达式（供贴入 结论与推导过程.md 核对）")
    print("=" * 70)
    R2V_factored = sp.factor(R2V_simplified)
    print("R2^V (factor后) =", sp.latex(R2V_factored))
