"""
【性质】具体计算 —— 用 sympy.residue() 求 z=0 处的留数 R0^I (强度版)
【计算的量】R0^I(x; u_hat, v_hat) = Res_{z=0} f_I(z)，其中 f_I 用对称核xi_I构造
【状态】✅ 成功，数值代入版0.2秒完成，符号版数秒完成
【依赖】无（自包含）

【方法说明】
与手征主线R0V的计算方法完全一致，只是把反对称组装(ePlus_uu*eCross_vv-eCross_uu*ePlus_vv)
换成对称组装(ePlus_uu*ePlus_vv+eCross_uu*eCross_vv)。注意：这里z=0处仍然可能是
高阶极点(手征版发现是二阶)，用sympy.residue()自动处理，不需要手动判断阶数。
"""
import sympy as sp
import numpy as np
import time
import pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')


def build_fI_symbolic():
    theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
    phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
    theta_dot_v = vx*x*(1+z**2)/(2*z) - sp.I*vy*x*(z**2-1)/(2*z) - vz*s
    phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
    ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
    eCross_uu = 2*theta_dot_u*phi_dot_u
    ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
    eCross_vv = 2*theta_dot_v*phi_dot_v
    numerator_I = sp.expand(ePlus_uu*ePlus_vv + eCross_uu*eCross_vv)   # 对称组装
    n_dot_u = ux*s*(1+z**2)/(2*z) + uz*x
    n_dot_v = s/(2*z)*(vx*(1+z**2) - sp.I*vy*(z**2-1)) + vz*x
    return numerator_I/(sp.I*z*(1+n_dot_u)*(1+n_dot_v))


if __name__ == "__main__":
    f_I = build_fI_symbolic()

    print("检验z=0处极点阶数 (数值代入版):")
    xv = 0.37; sv = np.sqrt(1-xv**2)
    duv = 1.1; uxv, uzv = np.sin(duv), np.cos(duv)
    vxv, vyv, vzv = 0.3, -0.5, np.sqrt(1-0.3**2-0.5**2)
    if vyv < 0:
        vyv = -vyv  # 保证vy>0，符合论文推导前提
    f_I_numeric = f_I.subs({x: xv, s: sv, ux: uxv, uz: uzv, vx: vxv, vy: vyv, vz: vzv})
    for n in [1, 2, 3]:
        lim = sp.limit(f_I_numeric*z**n, z, 0)
        print(f"  n={n}: lim = {lim}")

    print("\n方法1: 数值代入版 sympy.residue()")
    t0 = time.time()
    res0_numeric = sp.residue(f_I_numeric, z, 0)
    print(f"  完成, 用时{time.time()-t0:.2f}s, R0I = {complex(res0_numeric)}")

    print("\n方法2: 符号版 sympy.residue() (保留全部几何参数)")
    t0 = time.time()
    R0I_sym = sp.residue(f_I, z, 0)
    R0I_sym_expanded = sp.expand(R0I_sym)
    print(f"  完成, 用时{time.time()-t0:.2f}s, ops={sp.count_ops(R0I_sym_expanded)}")

    with open('R0I_final.pkl', 'wb') as f:
        pickle.dump(R0I_sym_expanded, f)
    print("\n已保存 R0I_final.pkl")

    # 与PRD论文Eq(A8)封闭解对照 (用delta_u,delta_v,gamma参数化)
    print("\n对照PRD论文Eq(A8)封闭解 R0(x) = 2(csc^2(du)-csc^2(dv)) * sqrt(...) + i[...]")
    print("(封闭解含delta_u,delta_v,gamma参数，需组件C阶段用x积分和数值代入对照，此处先确认符号解已获得)")

    print("\n" + "=" * 70)
    print("LaTeX 解析表达式（供贴入 结论与推导过程.md 核对）")
    print("=" * 70)
    t0 = time.time()
    R0I_cancelled = sp.cancel(R0I_sym_expanded)
    print(f"cancel完成，用时{time.time()-t0:.2f}s, ops从{sp.count_ops(R0I_sym_expanded)}降到{sp.count_ops(R0I_cancelled)}")
    print("R0^I =", sp.latex(R0I_cancelled))
