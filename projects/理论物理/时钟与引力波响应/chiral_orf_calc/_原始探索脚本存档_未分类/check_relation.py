"""
验证观察到的关系: numerator_V(z1) = -i * numerator_I(z1) ？
"""
import sympy as sp
import pickle
import time

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

theta_dot_u_expr = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u_expr   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v_expr = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v_expr   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

z1 = -(1+uz)*(1+x) / (ux*s)

def sub_reduce(expr, zk):
    val = sp.together(expr.subs(z, zk))
    num, den = sp.fraction(val)
    num = sp.expand(num); den = sp.expand(den)
    for _ in range(6):
        num = sp.expand(num.subs(ux**2, 1-uz**2)); den = sp.expand(den.subs(ux**2, 1-uz**2))
    for _ in range(6):
        num = sp.expand(num.subs(s**2, 1-x**2)); den = sp.expand(den.subs(s**2, 1-x**2))
    return sp.cancel(num/den)

tdu1 = sub_reduce(theta_dot_u_expr, z1)
pdu1 = sub_reduce(phi_dot_u_expr, z1)
tdv1 = sub_reduce(theta_dot_v_expr, z1)
pdv1 = sub_reduce(phi_dot_v_expr, z1)

ePlus_uu1  = sp.expand(tdu1**2 - pdu1**2)
eCross_uu1 = sp.expand(2*tdu1*pdu1)
ePlus_vv1  = sp.expand(tdv1**2 - pdv1**2)
eCross_vv1 = sp.expand(2*tdv1*pdv1)

numerator_I_z1 = sp.expand(ePlus_uu1*ePlus_vv1 + eCross_uu1*eCross_vv1)
numerator_V_z1 = sp.expand(ePlus_uu1*eCross_vv1 - eCross_uu1*ePlus_vv1)

diff = sp.expand(numerator_V_z1 - (-sp.I)*numerator_I_z1)
print("numerator_V(z1) - (-i)*numerator_I(z1) =", diff)
print("\n是否恒等于0:", sp.simplify(diff)==0)

# 这背后的原因: e×_uu = i * e+_uu (对z1这个特定极点上u的分量退化关系,前面已观察到 tdu1 = -i*pdu1 亦即 pdu1 = i*tdu1... 检查)
print("\n检查根源: eCross_uu1 与 ePlus_uu1 的关系:")
ratio = sp.simplify(eCross_uu1/ePlus_uu1)
print("eCross_uu1 / ePlus_uu1 =", ratio)
