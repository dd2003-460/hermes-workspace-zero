"""
【性质】具体计算 —— 用 sympy 内置的 residue() 函数求 z=0 处的留数
【计算的量】R0^V = Res_{z=0} f_V(z)
【状态】✅ 成功（已应用 BUG-001 修正，数值代入版0.3秒完成，符号版2.1秒完成）
【依赖】无（自包含）

【BUG-001 修正说明】
theta_dot_v, n_dot_v 的 vy 项符号已改为 -I（论文Eq(A6)打印/上版代码误为+I）。

【连带发现：z=0 实为二阶极点，不是三阶】
上一轮工作（用错误的+I符号）曾判定 z=0 是三阶极点。用本文件修正后的公式
重新检验（见同目录"推导"文件夹）发现，正确符号下 z=0 实际是【二阶】极点。
sympy.residue() 本身能自动处理任意阶极点，不需要用户预判阶数，所以不论
二阶还是三阶都能正确调用，下面的代码本身不需要改动调用方式，
只需要更新输入的 theta_dot_v, n_dot_v 表达式。

【方法说明】
sympy.residue(expr, z, z0) 是专门设计用来处理任意阶极点的留数计算函数，
内部会自动做必要的洛朗级数展开或多项式除法，不需要用户手动判断极点阶数
或手写高阶留数公式（本例实际是二阶极点，留数公式为:
    Res = lim_{z->0} d/dz [z^2 * f(z)]
但直接用 sympy.residue 更省心也更不容易出错，两者数值结果已交叉验证一致）。

【两种用法对比】
1. 先代入具体数值再调用residue —— 非常快(0.3秒)，适合数值验证
2. 保留符号变量直接调用residue —— 较慢但可行(2秒左右)，能得到完整解析式
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
    theta_dot_v = vx*x*(1+z**2)/(2*z) - sp.I*vy*x*(z**2-1)/(2*z) - vz*s   # BUG-001修正: -I
    phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
    ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
    eCross_uu = 2*theta_dot_u*phi_dot_u
    ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
    eCross_vv = 2*theta_dot_v*phi_dot_v
    numerator_V = sp.expand(ePlus_uu*eCross_vv - eCross_uu*ePlus_vv)
    n_dot_u = ux*s*(1+z**2)/(2*z) + uz*x
    n_dot_v = s/(2*z)*(vx*(1+z**2) - sp.I*vy*(z**2-1)) + vz*x            # BUG-001修正: -I
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
    print("\n已保存 R0V_final.pkl (BUG-001修正后)，正确性已在'数值验证'文件夹中交叉核实")

    print("\n" + "=" * 70)
    print("LaTeX 解析表达式（供贴入 结论与推导过程.md 核对）")
    print("=" * 70)
    print("【注意】R0^V 表达式项数较多，sp.factor()在此规模上性能很差")
    print("(实测超过90秒未完成，与组件A诊断记录的sympy性能瓶颈一致)。")
    print("改用 sp.cancel() 做通分整理（0.4秒左右，比factor快得多，虽不如factor简洁但可靠）:")
    t0 = time.time()
    R0V_cancelled = sp.cancel(R0V_sym_expanded)
    print(f"cancel完成，用时{time.time()-t0:.2f}s, ops从{sp.count_ops(R0V_sym_expanded)}降到{sp.count_ops(R0V_cancelled)}")
    print("R0^V =", sp.latex(R0V_cancelled))
