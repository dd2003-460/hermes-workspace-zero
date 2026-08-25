import sympy as sp
import time, sys

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

z3 = -(1+vz)*(1+x) / ((vx + sp.I*vy)*s)

theta_dot_v_expr = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s

t0=time.time()
val = theta_dot_v_expr.subs(z, z3)
print("subs done", time.time()-t0); sys.stdout.flush()

t0=time.time()
val_t = sp.together(val)
print("together done", time.time()-t0, "ops=", sp.count_ops(val_t)); sys.stdout.flush()

t0=time.time()
num, den = sp.fraction(val_t)
num_e = sp.expand(num)
print("expand num done", time.time()-t0, "ops=", sp.count_ops(num_e)); sys.stdout.flush()

t0=time.time()
den_e = sp.expand(den)
print("expand den done", time.time()-t0, "ops=", sp.count_ops(den_e)); sys.stdout.flush()
