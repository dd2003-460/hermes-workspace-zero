"""
高效策略: 
1. 先分别算出 theta.u, phi.u, theta.v, phi.v 在 z=z1 处的值，并逐一化简（表达式更小，化简更快）
2. 用这些化简后的小表达式组装 ePlus_uu, eCross_uu 等，此时应该会自然出现大量相消
3. 最后才相乘组装 numerator_V，此时表达式应该已经不再是天文数字
"""
import sympy as sp
import time, sys

x, s = sp.symbols('x s', real=True, positive=True)
z = sp.symbols('z')
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

z1 = -(1+uz)*(1+x) / (ux*s)

def sub_and_simplify(expr, label):
    t0=time.time()
    val = expr.subs(z, z1)
    val = sp.together(val)
    val = sp.cancel(val)
    print(f"  {label}: ops={sp.count_ops(val)}  time={time.time()-t0:.2f}s")
    return val

theta_dot_u_expr = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u_expr   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v_expr = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v_expr   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

print("Step 1: 逐一代入z1并cancel")
tdu = sub_and_simplify(theta_dot_u_expr, "theta.u")
pdu = sub_and_simplify(phi_dot_u_expr, "phi.u")
tdv = sub_and_simplify(theta_dot_v_expr, "theta.v")
pdv = sub_and_simplify(phi_dot_v_expr, "phi.v")

print("\n结果打印:")
print("theta.u|z1 =", tdu)
print("phi.u|z1   =", pdu)
print("theta.v|z1 =", tdv)
print("phi.v|z1   =", pdv)

import pickle
with open('/home/user/chiral_orf_calc/inner_products_at_z1.pkl','wb') as f:
    pickle.dump(dict(tdu=tdu, pdu=pdu, tdv=tdv, pdv=pdv), f)
