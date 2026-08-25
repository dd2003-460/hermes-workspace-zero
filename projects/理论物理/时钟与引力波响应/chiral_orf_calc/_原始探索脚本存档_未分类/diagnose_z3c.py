import sympy as sp
import time, sys

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

z3 = -(1+vz)*(1+x) / ((vx + sp.I*vy)*s)

def sub_reduce_verbose(expr, zk, label):
    print(f"--- {label} ---"); sys.stdout.flush()
    t0=time.time()
    val = sp.together(expr.subs(z, zk))
    print(f"  together: {time.time()-t0:.3f}s"); sys.stdout.flush()
    t0=time.time()
    num, den = sp.fraction(val)
    num = sp.expand(num); den = sp.expand(den)
    print(f"  expand num/den: {time.time()-t0:.3f}s  num_ops={sp.count_ops(num)} den_ops={sp.count_ops(den)}"); sys.stdout.flush()
    t0=time.time()
    for _ in range(6):
        num = sp.expand(num.subs(ux**2, 1-uz**2)); den = sp.expand(den.subs(ux**2, 1-uz**2))
    print(f"  ux reduce: {time.time()-t0:.3f}s"); sys.stdout.flush()
    t0=time.time()
    for _ in range(6):
        num = sp.expand(num.subs(s**2, 1-x**2)); den = sp.expand(den.subs(s**2, 1-x**2))
    print(f"  s reduce: {time.time()-t0:.3f}s"); sys.stdout.flush()
    t0=time.time()
    result = sp.cancel(num/den)
    print(f"  cancel: {time.time()-t0:.3f}s"); sys.stdout.flush()
    return result

theta_dot_u_expr = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u_expr   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v_expr = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v_expr   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

r1 = sub_reduce_verbose(theta_dot_u_expr, z3, "theta.u at z3")
r2 = sub_reduce_verbose(phi_dot_u_expr, z3, "phi.u at z3")
r3 = sub_reduce_verbose(theta_dot_v_expr, z3, "theta.v at z3")
r4 = sub_reduce_verbose(phi_dot_v_expr, z3, "phi.v at z3")
print("\nALL DONE")
