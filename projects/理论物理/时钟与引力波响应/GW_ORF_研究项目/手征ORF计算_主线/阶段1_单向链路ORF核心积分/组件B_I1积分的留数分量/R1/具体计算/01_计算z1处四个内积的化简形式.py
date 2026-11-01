"""
【性质】具体计算 —— 化简 theta.u, phi.u, theta.v, phi.v 四个内积在极点 z1 处的取值
【计算的量】theta.u|z1, phi.u|z1, theta.v|z1, phi.v|z1
【状态】✅ 成功（已应用 BUG-001 修正，重新计算并通过黄金标准验证）
【依赖】无（自包含，仅用 sympy 基础功能）

================================================================================
                    ⚠️ BUG-001 修正说明 ⚠️
================================================================================
本文件此前版本使用了论文Eq(A6)打印的 theta_dot_v, n_dot_v 公式（vy项系数+I），
经确认这是印刷错误，正确应为 -I。本文件已用修正后的公式重新计算全部四个
内积在z1处的化简结果，并在文件末尾新增了针对"黄金标准"(纯3D笛卡尔构造，
完全独立于(x,z)代数变换)的数值交叉验证。

详见 `00_总览与汇报/重大问题修正记录/关于PRD论文附录A公式A6的符号错误_详细推导说明.md`
================================================================================

【方法说明】
虽然理论上可以先把整个 numerator_V(z) 表达式代入 z1 再化简，但实测发现
sympy 的 factor/cancel 在处理这种含 5 个独立笛卡尔分量、6次方的大表达式时
会系统性卡死（90秒以上无响应）。

解决方案：先对 theta.u, phi.u, theta.v, phi.v 这四个"小内积"分别在 z1 处
代入化简（每个 < 1秒），得到干净的化简结果后，再组装成 numerator_V(z1)。
"""
import sympy as sp
from sympy import I, sqrt, symbols
import time

x, z = symbols('x z')
ux, uz = symbols('u_x u_z', real=True)
vx, vy, vz = symbols('v_x v_y v_z', real=True)
s = symbols('s', real=True, positive=True)   # s = sqrt(1-x^2)，独立符号加速计算

# ---- 修正后的内积公式 (BUG-001: theta_dot_v 的 vy 项为 -I，原论文/上版代码为 +I) ----
theta_dot_u_expr = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u_expr   = I*ux*(z**2-1)/(2*z)
theta_dot_v_expr = vx*x*(1+z**2)/(2*z) - I*vy*x*(z**2-1)/(2*z) - vz*s   # <- 修正: -I
phi_dot_v_expr   = I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

# z1 极点 (论文原文公式，未改动，本身正确)
z1 = -(1+uz)*(1+x) / (ux*s)


def sub_and_simplify(expr, zval, label):
    """代入极点值后化简：together消去分母嵌套，expand展开，
    再用约束 ux^2=1-uz^2, s^2=1-x^2 反复降幂，最后factor成最简形式"""
    t0 = time.time()
    e = sp.cancel(sp.together(expr.subs(z, zval)))
    e = sp.expand(e)
    e = e.subs(ux**2, 1-uz**2)
    e = sp.expand(e)
    e = e.subs(s**2, 1-x**2)
    e = sp.expand(e)
    e = sp.factor(e)
    print(f"  {label} 化简完成, 用时 {time.time()-t0:.2f}s: {e}")
    return e


if __name__ == "__main__":
    print("在 z1 处代入并化简四个内积 (BUG-001修正后):")
    tdu = sub_and_simplify(theta_dot_u_expr, z1, "theta.u@z1")
    pdu = sub_and_simplify(phi_dot_u_expr, z1, "phi.u@z1")
    tdv = sub_and_simplify(theta_dot_v_expr, z1, "theta.v@z1")
    pdv = sub_and_simplify(phi_dot_v_expr, z1, "phi.v@z1")

    print("\n关键代数关系检查:")
    print("  phi.u@z1 / theta.u@z1 =", sp.simplify(pdu/tdu), " (预期应为纯虚数比例, 体现e^A_uu的手征结构)")

    # ---- 黄金标准数值交叉验证 (完全独立于上面的(x,z)代数路径) ----
    import numpy as np
    print("\n" + "="*70)
    print("黄金标准验证: 用纯3D笛卡尔矢量点积直接算 theta.v, phi.v 在 z1 对应的")
    print("(theta,phi)点上的值 —— 但注意z1一般不在单位圆上，所以这里验证的是")
    print("(x,z)公式本身在|z|=1圆上与3D点积吻合，间接确认解析延拓的正确性")
    print("="*70)
    np.random.seed(2024)
    tdu_f = sp.lambdify((x, s, ux, uz), theta_dot_u_expr.subs(z, sp.Symbol('zz')).subs(sp.Symbol('zz'), z), 'numpy')
    max_err = 0
    for trial in range(5):
        theta_n = np.random.uniform(0.3, 2.8)
        phi_n = np.random.uniform(0.1, 6.0)
        xv, sv = np.cos(theta_n), np.sin(theta_n)
        zv = np.exp(1j*phi_n)
        du = np.random.uniform(0.3, 2.7)
        uxv, uzv = np.sin(du), np.cos(du)
        dv, psi = np.random.uniform(0.3, 2.7), np.random.uniform(0.1, 6.0)
        vxv, vyv, vzv = np.sin(dv)*np.cos(psi), np.sin(dv)*np.sin(psi), np.cos(dv)

        that = np.array([np.cos(theta_n)*np.cos(phi_n), np.cos(theta_n)*np.sin(phi_n), -np.sin(theta_n)])
        phat = np.array([-np.sin(phi_n), np.cos(phi_n), 0])
        uvec = np.array([uxv, 0, uzv]); vvec = np.array([vxv, vyv, vzv])
        true_tu, true_pu = that@uvec, phat@uvec
        true_tv, true_pv = that@vvec, phat@vvec

        f_tu = (uxv*xv*(1+zv**2)/(2*zv) - uzv*sv)
        f_pu = (1j*uxv*(zv**2-1)/(2*zv))
        f_tv = (vxv*xv*(1+zv**2)/(2*zv) - 1j*vyv*xv*(zv**2-1)/(2*zv) - vzv*sv)
        f_pv = (1j*vxv*(zv**2-1)/(2*zv) + vyv*(1+zv**2)/(2*zv))

        err = max(abs(true_tu-f_tu), abs(true_pu-f_pu), abs(true_tv-f_tv), abs(true_pv-f_pv))
        max_err = max(max_err, err)
        print(f"  trial{trial}: max|diff| = {err:.2e}")
    print(f"\n最大误差 = {max_err:.2e} (机器精度即通过)")
