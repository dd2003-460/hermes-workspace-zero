"""
【性质】推导 —— 复现 PRD 论文附录 A 的坐标变换公式，构造强度对称核 xi_I
【计算的量】theta.u, phi.u, theta.v, phi.v, n.u, n.v 六个基础内积；对称核 xi_I 的分子
【状态】✅ 成功，与主线组件A完全一致（本副本只用强度部分，不涉及手征）
【依赖】无（自包含，直接复用主线已验证的坐标系构造方法）

【背景】
本文件直接复用手征主线项目 `../../../../手征ORF计算_主线/阶段1_单向链路ORF核心积分/
组件A_基础设施_坐标系与被积核/推导/01_坐标变换公式_PRD附录A复现.py` 中已经过三层独立
验证的六个内积公式（含 BUG-001 修正：theta.v, n.v 的 vy 项符号为 -i）。
按"下游只调用上游已验证产出"的原则，这里直接抄一份自包含代码，而非用相对路径
跨项目引用（保证本副本项目可以独立运行）。

xi_I（强度对称核）本身的构造方式与手征无关，用哪个符号约定的theta.v/n.v结果一样
（因为 numerator_I = ePlus_uu*ePlus_vv + eCross_uu*eCross_vv 对vy符号翻转不敏感——
翻转vy只改变phi.v的一部分符号，但ePlus_vv, eCross_vv整体经过平方/乘积后规律地抵消）。
不过为保持与主线代码一致，这里同样使用修正后的正确符号。
"""
import sympy as sp
from sympy import I, sqrt, symbols

# ---- 符号定义 (与主线完全一致) ----
x, z = symbols('x z')
ux, uz = symbols('u_x u_z', real=True)
vx, vy, vz = symbols('v_x v_y v_z', real=True)

# ---- 六个基础内积 (与主线BUG-001修正后完全一致) ----
theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*sqrt(1-x**2)
phi_dot_u   = I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) - I*vy*x*(z**2-1)/(2*z) - vz*sqrt(1-x**2)
phi_dot_v   = I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
n_dot_u = ux*sqrt(1-x**2)*(1+z**2)/(2*z) + uz*x
n_dot_v = sqrt(1-x**2)/(2*z)*(vx*(1+z**2) - I*vy*(z**2-1)) + vz*x

# ---- e^A_ab u^a u^b 的两个分量 ----
ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
eCross_uu = 2*theta_dot_u*phi_dot_u
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
eCross_vv = 2*theta_dot_v*phi_dot_v

# ---- 强度对称核 xi_I 的分子 (本副本项目的核心对象) ----
numerator_I = ePlus_uu*ePlus_vv + eCross_uu*eCross_vv

if __name__ == "__main__":
    print("theta_dot_u =", theta_dot_u)
    print("phi_dot_u   =", phi_dot_u)
    print("theta_dot_v =", theta_dot_v)
    print("phi_dot_v   =", phi_dot_v)
    print("n_dot_u     =", n_dot_u)
    print("n_dot_v     =", n_dot_v)

    # ---- 校验: 对照PRD论文式(A2)的展开形式，确认构造方式一致 ----
    numerator_I_direct = sp.expand(4*theta_dot_u*phi_dot_u*theta_dot_v*phi_dot_v +
                                    (theta_dot_u**2-phi_dot_u**2)*(theta_dot_v**2-phi_dot_v**2))
    numerator_I_fromAB = sp.expand(ePlus_uu*ePlus_vv + eCross_uu*eCross_vv)
    check = sp.simplify(numerator_I_direct - numerator_I_fromAB)
    print("\n校验: 两种写法算出的 xi_I 分子之差 (应为0) =", check)

    print("\nnumerator_I (未化简) 的表达式长度 =", len(str(sp.expand(numerator_I))))

    # ---- 黄金标准数值交叉验证 ----
    import numpy as np
    print("\n" + "="*70)
    print("黄金标准验证: 3D笛卡尔矢量点积 vs (x,z)代数公式")
    print("="*70)
    np.random.seed(2024)
    max_err = 0
    for trial in range(6):
        theta_n = np.random.uniform(0.2, 2.9)
        phi_n = np.random.uniform(0.1, 6.0)
        xv, sv = np.cos(theta_n), np.sin(theta_n)
        zv = np.exp(1j*phi_n)
        du = np.random.uniform(0.2, 2.9)
        uxv, uzv = np.sin(du), np.cos(du)
        dv, psi = np.random.uniform(0.2, 2.9), np.random.uniform(0.1, 6.0)
        vxv, vyv, vzv = np.sin(dv)*np.cos(psi), np.sin(dv)*np.sin(psi), np.cos(dv)

        that = np.array([np.cos(theta_n)*np.cos(phi_n), np.cos(theta_n)*np.sin(phi_n), -np.sin(theta_n)])
        phat = np.array([-np.sin(phi_n), np.cos(phi_n), 0])
        nhat = np.array([sv*np.cos(phi_n), sv*np.sin(phi_n), xv])
        uvec = np.array([uxv, 0, uzv]); vvec = np.array([vxv, vyv, vzv])

        true_tu, true_pu, true_nu = that@uvec, phat@uvec, nhat@uvec
        true_tv, true_pv, true_nv = that@vvec, phat@vvec, nhat@vvec

        f_tu = uxv*xv*(1+zv**2)/(2*zv) - uzv*sv
        f_pu = 1j*uxv*(zv**2-1)/(2*zv)
        f_nu = uxv*sv*(1+zv**2)/(2*zv) + uzv*xv
        f_tv = vxv*xv*(1+zv**2)/(2*zv) - 1j*vyv*xv*(zv**2-1)/(2*zv) - vzv*sv
        f_pv = 1j*vxv*(zv**2-1)/(2*zv) + vyv*(1+zv**2)/(2*zv)
        f_nv = sv/(2*zv)*(vxv*(1+zv**2) - 1j*vyv*(zv**2-1)) + vzv*xv

        err = max(abs(true_tu-f_tu), abs(true_pu-f_pu), abs(true_nu-f_nu),
                  abs(true_tv-f_tv), abs(true_pv-f_pv), abs(true_nv-f_nv))
        max_err = max(max_err, err)
        print(f"  trial{trial}: max|diff| = {err:.2e}")
    print(f"\n最大误差 = {max_err:.2e} (机器精度即通过)")
