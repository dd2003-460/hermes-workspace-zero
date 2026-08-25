import sympy as sp
import time, sys

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

z3 = -(1+vz)*(1+x) / ((vx + sp.I*vy)*s)

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

tdu3 = sub_reduce(theta_dot_u_expr, z3)
pdu3 = sub_reduce(phi_dot_u_expr, z3)
tdv3 = sub_reduce(theta_dot_v_expr, z3)
pdv3 = sub_reduce(phi_dot_v_expr, z3)
print("内积计算完毕")
print("tdu3=", tdu3)
print("pdu3=", pdu3)
print("tdv3=", tdv3)
print("pdv3=", pdv3)

t0=time.time()
ePlus_uu3  = sp.expand(tdu3**2 - pdu3**2)
print("ePlus_uu3:", time.time()-t0, "ops=", sp.count_ops(ePlus_uu3)); sys.stdout.flush()

t0=time.time()
eCross_uu3 = sp.expand(2*tdu3*pdu3)
print("eCross_uu3:", time.time()-t0, "ops=", sp.count_ops(eCross_uu3)); sys.stdout.flush()

t0=time.time()
ePlus_vv3  = sp.expand(tdv3**2 - pdv3**2)
print("ePlus_vv3:", time.time()-t0, "ops=", sp.count_ops(ePlus_vv3)); sys.stdout.flush()

t0=time.time()
eCross_vv3 = sp.expand(2*tdv3*pdv3)
print("eCross_vv3:", time.time()-t0, "ops=", sp.count_ops(eCross_vv3)); sys.stdout.flush()
