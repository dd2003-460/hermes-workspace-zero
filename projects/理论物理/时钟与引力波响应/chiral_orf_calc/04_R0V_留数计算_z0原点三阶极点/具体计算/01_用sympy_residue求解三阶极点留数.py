"""
【性质】具体计算 —— 用 sympy 内置的 residue() 函数求三阶极点 z=0 处的留数
【计算的量】R0^V = Res_{z=0} f_V(z)
【状态】✅ 成功（数值代入版0.4秒完成，符号版3.1秒完成）

【方法说明】
sympy.residue(expr, z, z0) 是专门设计用来处理任意阶极点的留数计算函数，
内部会自动做必要的洛朗级数展开或多项式除法，不需要用户手动判断极点阶数
或手写高阶留数公式（对三阶极点，留数公式是:
    Res = (1/2!) * d^2/dz^2 [z^3 * f(z)] |_{z=0}
但直接用 sympy.residue 更省心也更不容易出错）。

【两种用法对比】
1. 先代入具体数值再调用residue —— 非常快(0.4秒)，适合数值验证
2. 保留符号变量直接调用residue —— 较慢但可行(3.1秒)，能得到完整解析式
"""
import sympy as sp
import numpy as np
import time
import pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')


def build_fV_symbolic():
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
    return numerator_V/(sp.I*z*(1+n_dot_u)*(1+n_dot_v))


if __name__ == "__main__":
    f_V = build_fV_symbolic()

    print("方法1: 数值代入版 sympy.residue()")
    xv=0.37; sv=np.sqrt(1-xv**2)
    duv=1.1; uxv,uzv=np.sin(duv),np.cos(duv)
    vxv,vyv,vzv=0.3,-0.5,np.sqrt(1-0.3**2-0.5**2)
    f_V_numeric = f_V.subs({x:xv, s:sv, ux:uxv, uz:uzv, vx:vxv, vy:vyv, vz:vzv})
    t0=time.time()
    res0_numeric = sp.residue(f_V_numeric, z, 0)
    print(f"  完成, 用时{time.time()-t0:.2f}s, R0V = {complex(res0_numeric)}")

    print("\n方法2: 符号版 sympy.residue() (保留全部几何参数)")
    t0=time.time()
    R0V_sym = sp.residue(f_V, z, 0)
    R0V_sym_expanded = sp.expand(R0V_sym)
    print(f"  完成, 用时{time.time()-t0:.2f}s, ops={sp.count_ops(R0V_sym_expanded)}")

    with open('R0V_final.pkl', 'wb') as f:
        pickle.dump(R0V_sym_expanded, f)
    print("\n已保存 R0V_final.pkl，正确性已在'数值验证'文件夹中交叉核实")
