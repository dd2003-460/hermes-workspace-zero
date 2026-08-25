"""
Step 1: 在 sympy 中定义几何量，严格复现 PRD 论文附录 A 的坐标变换公式
参考: Hu, Wang, Tan, Shao, PRD 111, 084065 (2025), Appendix A, Eq. (A2)-(A6)
"""
import sympy as sp
from sympy import I, sqrt, symbols, simplify, expand, Rational, nsimplify

# 符号定义
x, z = symbols('x z')                    # x = cos(theta), z = exp(i*phi)
ux, uz = symbols('u_x u_z', real=True)    # u_hat = (ux, 0, uz)  在计算坐标系中 uy=0
vx, vy, vz = symbols('v_x v_y v_z', real=True)  # v_hat = (vx, vy, vz)

# ---- PRD 论文附录A 式(A6): 内积在 (x,z) 坐标下的显式表达式 ----
# theta_hat . u_hat
theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*sqrt(1-x**2)
# phi_hat . u_hat
phi_dot_u   = I*ux*(z**2-1)/(2*z)
# theta_hat . v_hat
theta_dot_v = vx*x*(1+z**2)/(2*z) + I*vy*x*(z**2-1)/(2*z) - vz*sqrt(1-x**2)
# phi_hat . v_hat
phi_dot_v   = I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
# n_hat . u_hat  (对应传递函数分母 1+n.u 中的 n.u)
n_dot_u = ux*sqrt(1-x**2)*(1+z**2)/(2*z) + uz*x
# n_hat . v_hat
n_dot_v = sqrt(1-x**2)/(2*z)*(vx*(1+z**2) + I*vy*(z**2-1)) + vz*x

print("theta_dot_u =", theta_dot_u)
print("phi_dot_u   =", phi_dot_u)
print("theta_dot_v =", theta_dot_v)
print("phi_dot_v   =", phi_dot_v)
print("n_dot_u     =", n_dot_u)
print("n_dot_v     =", n_dot_v)
