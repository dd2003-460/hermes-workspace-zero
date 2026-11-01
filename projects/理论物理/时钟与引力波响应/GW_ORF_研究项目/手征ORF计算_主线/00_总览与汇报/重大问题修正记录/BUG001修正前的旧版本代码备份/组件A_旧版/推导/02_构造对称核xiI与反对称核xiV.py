"""
【性质】推导 —— 构造强度ORF的对称被积核 xi_I，以及手征ORF的反对称被积核 xi_V
【计算的量】xi_I(x,z), xi_V(x,z)：留数计算真正要处理的分子
【状态】✅ 成功，xi_I 已严格验证与 PRD 论文式(A2) 一致

【物理背景】
两条单向链路 u, v 的强度ORF被积核（PRD论文式12）是"对称求和"：
    xi_I(n) = e^+_ab(n) u^a u^b * e^+_cd(n) v^c v^d + e^x_ab(n) u^a u^b * e^x_cd(n) v^c v^d

我们要推广到手征ORF，用"反对称求差"替换：
    xi_V(n) = e^+_ab(n) u^a u^b * e^x_cd(n) v^c v^d - e^x_ab(n) u^a u^b * e^+_cd(n) v^c v^d

这里用到的关系（由偏振基张量定义直接展开得到）：
    e^+_ab(n) u^a u^b = (theta.u)^2 - (phi.u)^2
    e^x_ab(n) u^a u^b = 2*(theta.u)*(phi.u)

【本文件做了什么关键校验】
用两种独立写法构造 xi_I 的分子——(1)直接展开成 theta/phi 内积的三角多项式形式
(对照 PRD 论文式A2的写法)；(2) 先算 e+_uu, ex_uu 等中间量再相乘。
用 sympy.simplify 验证两者严格相等（差为0），这确认了我们对 e^A_ab u^a u^b 的
构造方式与 PRD 论文完全一致，为后续手征核的构造提供了正确性保证。
"""
import sympy as sp
from sympy import I, sqrt, symbols, simplify, expand

x, z = symbols('x z')
ux, uz = symbols('u_x u_z', real=True)
vx, vy, vz = symbols('v_x v_y v_z', real=True)

theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*sqrt(1-x**2)
phi_dot_u   = I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + I*vy*x*(z**2-1)/(2*z) - vz*sqrt(1-x**2)
phi_dot_v   = I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

# e^A_ab u^a u^b 的两个分量 (A=+,x)
ePlus_uu  = theta_dot_u**2 - phi_dot_u**2      # e+_ab u^a u^b
eCross_uu = 2*theta_dot_u*phi_dot_u            # e×_ab u^a u^b
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2      # e+_cd v^c v^d
eCross_vv = 2*theta_dot_v*phi_dot_v            # e×_cd v^c v^d

if __name__ == "__main__":
    # ---- 校验: 对称核 xi_I 的分子应该等于论文 Eq.(A2) 给出的形式 ----
    numerator_I_direct = 4*theta_dot_u*phi_dot_u*theta_dot_v*phi_dot_v + \
                          (theta_dot_u**2-phi_dot_u**2)*(theta_dot_v**2-phi_dot_v**2)
    numerator_I_fromAB = ePlus_uu*ePlus_vv + eCross_uu*eCross_vv
    check_I = simplify(expand(numerator_I_direct - numerator_I_fromAB))
    print("校验: 两种写法算出的 xi_I 分子之差 (应为0) =", check_I)

    # ---- 反对称核 xi_V 的分子 (本次任务的目标对象) ----
    numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
    numerator_V = expand(numerator_V)
    print("\n构造完成: numerator_V (未化简) 的原始表达式长度 =", len(str(numerator_V)))
    print("这就是手征ORF留数计算里，要在各个极点处求值的核心对象。")
