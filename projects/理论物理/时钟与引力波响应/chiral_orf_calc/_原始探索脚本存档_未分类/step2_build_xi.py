"""
Step 2: 构造对称核 xi_I (校验用) 和反对称核 xi_V (目标)
参考: PRD论文 Appendix A Eq.(A2): 
  xi(n) = [4(th.u)(ph.u)(th.v)(ph.v) + ((th.u)^2-(ph.u)^2)((th.v)^2-(ph.v)^2)] / [(1+n.u)(1+n.v)]
这是通过 e+_ab u^a u^b = (th.u)^2-(ph.u)^2,  e×_ab u^a u^b = 2(th.u)(ph.u) 代入对称求和 e+e+ + e×e× 得到的。

我们现在构造反对称版本 (e+ 配 e×  減  e× 配 e+)：
  numerator_V = [(th.u)^2-(ph.u)^2] * 2(th.v)(ph.v)  -  2(th.u)(ph.u) * [(th.v)^2-(ph.v)^2]
"""
import sympy as sp
from sympy import I, sqrt, symbols, simplify, expand, factor, together, cancel, fraction

x, z = symbols('x z')
ux, uz = symbols('u_x u_z', real=True)
vx, vy, vz = symbols('v_x v_y v_z', real=True)

theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*sqrt(1-x**2)
phi_dot_u   = I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + I*vy*x*(z**2-1)/(2*z) - vz*sqrt(1-x**2)
phi_dot_v   = I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
n_dot_u = ux*sqrt(1-x**2)*(1+z**2)/(2*z) + uz*x
n_dot_v = sqrt(1-x**2)/(2*z)*(vx*(1+z**2) + I*vy*(z**2-1)) + vz*x

# e^A_ab u^a u^b 的两个分量 (A=+,x)
ePlus_uu  = theta_dot_u**2 - phi_dot_u**2      # e+_ab u^a u^b
eCross_uu = 2*theta_dot_u*phi_dot_u            # e×_ab u^a u^b
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2      # e+_cd v^c v^d
eCross_vv = 2*theta_dot_v*phi_dot_v            # e×_cd v^c v^d

# ---- 校验: 对称核 xi_I 的分子应该等于论文 Eq.(A2) 给出的形式 ----
numerator_I_direct = 4*theta_dot_u*phi_dot_u*theta_dot_v*phi_dot_v + \
                      (theta_dot_u**2-phi_dot_u**2)*(theta_dot_v**2-phi_dot_v**2)
numerator_I_fromAB = ePlus_uu*ePlus_vv + eCross_uu*eCross_vv
check_I = simplify(expand(numerator_I_direct - numerator_I_fromAB))
print("校验: 两种写法算出的 xi_I 分子之差 (应为0) =", check_I)

# ---- 反对称核 xi_V 的分子 ----
numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
numerator_V = expand(numerator_V)
print("\n构造完成: numerator_V (未化简) 的原始表达式长度 =", len(str(numerator_V)))

# 保存供后续步骤使用
import pickle
with open('/home/user/chiral_orf_calc/xi_data.pkl', 'wb') as f:
    pickle.dump({
        'x': x, 'z': z, 'ux': ux, 'uz': uz, 'vx': vx, 'vy': vy, 'vz': vz,
        'theta_dot_u': theta_dot_u, 'phi_dot_u': phi_dot_u,
        'theta_dot_v': theta_dot_v, 'phi_dot_v': phi_dot_v,
        'n_dot_u': n_dot_u, 'n_dot_v': n_dot_v,
        'numerator_I': numerator_I_fromAB, 'numerator_V': numerator_V
    }, f)
print("\n已保存 xi_data.pkl")
