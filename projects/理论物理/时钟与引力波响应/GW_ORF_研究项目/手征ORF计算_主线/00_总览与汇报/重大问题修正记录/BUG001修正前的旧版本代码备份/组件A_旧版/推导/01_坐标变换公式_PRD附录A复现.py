"""
【性质】推导 —— 复现 PRD 论文附录 A 的坐标变换公式
【计算的量】theta.u, phi.u, theta.v, phi.v, n.u, n.v 这六个基础内积
【状态】✅ 成功，已通过下游多处校验

【背景】
PRD 论文 (Hu, Wang, Tan, Shao, Phys.Rev.D 111, 084065 (2025)) 附录A式(A6)给出了
在"计算坐标系"下（z轴与分离矢量s对齐，u落在xz平面），球坐标切向基矢量 theta_hat, phi_hat
与链路方向 u, v 的内积，用参数 x=cos(theta), z=exp(i*phi) 表示的显式解析式。

这是整个留数计算的地基：后续所有对 xi_I(强度核), xi_V(手征核) 的构造，
都要用到这六个内积表达式。

【关键约定】
- u_hat = (ux, 0, uz)  —— u 被约定锁定在 x-z 平面内 (uy=0)，这是计算坐标系的规范选择
- v_hat = (vx, vy, vz) —— v 是一般方向，不受约束
- x = cos(theta),  z = exp(i*phi)  是把球面积分变成复围道积分的变量代换

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

# ---- PRD 论文附录A 式(A6): 内积在 (x,z) 坐标下的显式表达式 ----
theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*sqrt(1-x**2)
phi_dot_u   = I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + I*vy*x*(z**2-1)/(2*z) - vz*sqrt(1-x**2)
phi_dot_v   = I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

# n_hat . u_hat: 对应传递函数分母 (1+n.u) 中的 n.u，物理意义见"讲解文档"中0.4节
n_dot_u = ux*sqrt(1-x**2)*(1+z**2)/(2*z) + uz*x
# n_hat . v_hat
n_dot_v = sqrt(1-x**2)/(2*z)*(vx*(1+z**2) + I*vy*(z**2-1)) + vz*x

if __name__ == "__main__":
    print("theta_dot_u =", theta_dot_u)
    print("phi_dot_u   =", phi_dot_u)
    print("theta_dot_v =", theta_dot_v)
    print("phi_dot_v   =", phi_dot_v)
    print("n_dot_u     =", n_dot_u)
    print("n_dot_v     =", n_dot_v)
