"""
验证 -i 比例关系是否在 z2 也成立: numerator_V(z2) = -i * numerator_I(z2) ?
复用之前 compute_R2_R0.py 里已经算好的 tdu2,pdu2,tdv2,pdv2 逻辑
"""
import sympy as sp
import time

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

z2 = -(1-uz)*(1-x) / (ux*s)

def sub_reduce(expr, zk):
    val = sp.together(expr.subs(z, zk))
    num, den = sp.fraction(val)
    num = sp.expand(num); den = sp.expand(den)
    for _ in range(6):
        num = sp.expand(num.subs(ux**2, 1-uz**2)); den = sp.expand(den.subs(ux**2, 1-uz**2))
    for _ in range(6):
        num = sp.expand(num.subs(s**2, 1-x**2)); den = sp.expand(den.subs(s**2, 1-x**2))
    return sp.cancel(num/den)

theta_dot_u_expr = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u_expr   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v_expr = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v_expr   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

t0=time.time()
tdu2 = sub_reduce(theta_dot_u_expr, z2)
pdu2 = sub_reduce(phi_dot_u_expr, z2)
tdv2 = sub_reduce(theta_dot_v_expr, z2)
pdv2 = sub_reduce(phi_dot_v_expr, z2)
print("z2内积计算完毕:", time.time()-t0)

# 关键检查: phi.u / theta.u 在 z2 处的比值(对照z1处是 i)
ratio_u = sp.simplify(pdu2/tdu2)
print("phi.u / theta.u at z2 =", ratio_u)

ePlus_uu2  = sp.expand(tdu2**2 - pdu2**2)
eCross_uu2 = sp.expand(2*tdu2*pdu2)
ePlus_vv2  = sp.expand(tdv2**2 - pdv2**2)
eCross_vv2 = sp.expand(2*tdv2*pdv2)

ratio_uu = sp.simplify(eCross_uu2/ePlus_uu2)
print("eCross_uu2 / ePlus_uu2 =", ratio_uu)

numerator_I_z2 = sp.expand(ePlus_uu2*ePlus_vv2 + eCross_uu2*eCross_vv2)
numerator_V_z2 = sp.expand(ePlus_uu2*eCross_vv2 - eCross_uu2*ePlus_vv2)

diff = sp.expand(numerator_V_z2 - (-sp.I)*numerator_I_z2)
print("\nnumerator_V(z2) - (-i)*numerator_I(z2) =", diff)
print("是否恒等于0:", sp.simplify(diff) == 0)

# 如果不是-i，看看是不是+i (因为z2对应n.u=-1的另一支，可能符号相反)
diff2 = sp.expand(numerator_V_z2 - (sp.I)*numerator_I_z2)
print("\n备选检查 numerator_V(z2) - (+i)*numerator_I(z2) =", diff2)
print("是否恒等于0:", sp.simplify(diff2) == 0)
