"""
【性质】推导 —— 复现 PRD 论文附录 A 的坐标变换公式（含 BUG-001 修正）
【计算的量】theta.u, phi.u, theta.v, phi.v, n.u, n.v 这六个基础内积
【状态】✅ 成功，已通过下游多处校验 ——【重要】本文件已于 BUG-001 修正中更新

================================================================================
                    ⚠️ 重大修正说明（BUG-001，详见总览文档）⚠️
================================================================================
本文件此前（上一轮工作）直接照抄 PRD 论文 Eq.(A6) 打印的公式，其中
theta.v 和 n.v 两个含 v_y 的公式，v_y 项前的虚数符号是 **+i**：
    theta.v = vx*x*(1+z^2)/2z + i*vy*x*(z^2-1)/2z - vz*sqrt(1-x^2)   [论文原文，有误]
    n.v     = sqrt(1-x^2)/2z * (vx(1+z^2) + i*vy(z^2-1)) + vz*x      [论文原文，有误]

经过三层独立验证（详见
`00_总览与汇报/重大问题修正记录/关于PRD论文附录A公式A6的符号错误_详细推导说明.md`）：
  1. 从标准球坐标基矢量定义 + 欧拉公式 sin(phi)=-i(z^2-1)/(2z) 严格符号推导；
  2. 3D笛卡尔矢量点积数值抽样比对；
  3. 判决性检验——用论文自己发表的 R1-R4 封闭解公式(A8-A12)反查，
     确认只有把 v_y 项符号改成 **-i** 才能让数值围道积分与论文封闭解完全吻合
     （32组随机测试最大相对误差 ~1e-12）。
确认这是论文本身 Eq(A6) 的一处印刷/推导错误，正确公式应为：
    theta.v = vx*x*(1+z^2)/2z - i*vy*x*(z^2-1)/2z - vz*sqrt(1-x^2)   [修正后]
    n.v     = sqrt(1-x^2)/2z * (vx(1+z^2) - i*vy(z^2-1)) + vz*x      [修正后]

【重要澄清】论文的极点公式 Eq.(16)/(A7) 里 z3,z4 分母 (vx - i*vy) 是【正确】的，
不需要修改。上一轮工作曾错误地把它"修正"成 (vx + i*vy)，那是双重错误互相
抵消导致的虚假验证通过，本轮已撤销该"修正"，恢复论文原文的 z3,z4 公式。

theta.u, phi.u, n.u 三个不含 v_y 的公式没有问题，无需改动。
================================================================================

【背景】
PRD 论文 (Hu, Wang, Tan, Shao, Phys.Rev.D 111, 084065 (2025)) 附录A式(A6)给出了
在"计算坐标系"下（z轴与分离矢量s对齐，u落在xz平面），球坐标切向基矢量 theta_hat, phi_hat
与链路方向 u, v 的内积，用参数 x=cos(theta), z=exp(i*phi) 表示的显式解析式。

这是整个留数计算的地基：后续所有对 xi_I(强度核), xi_V(手征核) 的构造，
都要用到这六个内积表达式。

【关键约定】
- u_hat = (ux, 0, uz)  —— u 被约定锁定在 x-z 平面内 (uy=0)，这是计算坐标系的规范选择
- v_hat = (vx, vy, vz) —— v 是一般方向，不受约束
- x = cos(theta),  z = exp(i*phi) 是把球面积分变成复围道积分的变量代换

【使用方法】
本文件只做符号定义和打印展示，不涉及后续的留数计算。
下游文件会 import 这里定义的表达式结构（实际使用中是复制这段定义代码，
而非真正 import，因为 sympy 符号在不同脚本间不能直接共享变量对象）。
"""
import sympy as sp
from sympy import I, sqrt, symbols

# ---- 符号定义 ----
x, z = symbols('x z')                      # x = cos(theta), z = exp(i*phi)
ux, uz = symbols('u_x u_z', real=True)     # u_hat = (ux, 0, uz)，规范选择uy=0
vx, vy, vz = symbols('v_x v_y v_z', real=True)  # v_hat = (vx, vy, vz)

# ---- 修正后的内积表达式 (BUG-001 已修正，theta.v 与 n.v 的 vy 项符号翻转) ----
theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*sqrt(1-x**2)
phi_dot_u   = I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) - I*vy*x*(z**2-1)/(2*z) - vz*sqrt(1-x**2)   # <- 修正: -I (原论文+I)
phi_dot_v   = I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

# n_hat . u_hat: 对应传递函数分母 (1+n.u) 中的 n.u，物理意义见"讲解文档"中0.4节
n_dot_u = ux*sqrt(1-x**2)*(1+z**2)/(2*z) + uz*x
# n_hat . v_hat  (修正: -I，原论文+I)
n_dot_v = sqrt(1-x**2)/(2*z)*(vx*(1+z**2) - I*vy*(z**2-1)) + vz*x

if __name__ == "__main__":
    print("theta_dot_u =", theta_dot_u)
    print("phi_dot_u   =", phi_dot_u)
    print("theta_dot_v =", theta_dot_v, "  <- BUG-001已修正: vy项为 -I (原论文/上版代码为+I)")
    print("phi_dot_v   =", phi_dot_v)
    print("n_dot_u     =", n_dot_u)
    print("n_dot_v     =", n_dot_v, "  <- BUG-001已修正: vy项为 -I (原论文/上版代码为+I)")

    print("\n" + "=" * 70)
    print("LaTeX 解析表达式（供贴入 结论与推导过程.md 与论文/草稿手推公式核对）")
    print("=" * 70)
    for name, expr in [("theta.u", theta_dot_u), ("phi.u", phi_dot_u),
                        ("theta.v", theta_dot_v), ("phi.v", phi_dot_v),
                        ("n.u", n_dot_u), ("n.v", n_dot_v)]:
        print(f"{name} = {sp.latex(expr)}")

    # ---- 自检: 用最基础的3D笛卡尔矢量点积交叉验证 (与论文完全无关的独立推导路径) ----
    import numpy as np
    print("\n" + "="*70)
    print("自检: 3D笛卡尔矢量点积 (黄金标准) vs 上面的(x,z)公式, 多组随机数值")
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

        true_tv = that@vvec; true_nv = nhat@vvec

        formula_tv = (vxv*xv*(1+zv**2)/(2*zv) - 1j*vyv*xv*(zv**2-1)/(2*zv) - vzv*sv)
        formula_nv = (sv/(2*zv)*(vxv*(1+zv**2) - 1j*vyv*(zv**2-1)) + vzv*xv)

        err = max(abs(true_tv-formula_tv), abs(true_nv-formula_nv))
        max_err = max(max_err, err)
        print(f"  trial{trial}: theta.v true={true_tv:.6f} formula={formula_tv.real:.6f} | "
              f"n.v true={true_nv:.6f} formula={formula_nv.real:.6f} | max_diff={err:.2e}")
    print(f"\n最大误差 = {max_err:.2e}  (机器精度量级即通过)")
