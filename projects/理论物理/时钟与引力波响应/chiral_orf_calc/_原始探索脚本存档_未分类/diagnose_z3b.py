import sympy as sp
import time, sys

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

z3 = -(1+vz)*(1+x) / ((vx + sp.I*vy)*s)
theta_dot_v_expr = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
val = theta_dot_v_expr.subs(z, z3)
val_t = sp.together(val)
num, den = sp.fraction(val_t)
num_e = sp.expand(num)
den_e = sp.expand(den)

print("尝试用 ux^2 -> 1-uz^2 降幂 (这个应该无操作,因为表达式不含ux)")
t0=time.time()
for i in range(6):
    num_e = sp.expand(num_e.subs(ux**2, 1-uz**2))
print("ux约束循环完成:", time.time()-t0); sys.stdout.flush()

print("尝试用 s^2 -> 1-x^2 降幂")
t0=time.time()
for i in range(6):
    num_e2 = sp.expand(num_e.subs(s**2, 1-x**2))
    print(f"  iter{i}: ops={sp.count_ops(num_e2)} time={time.time()-t0:.3f}")
    num_e = num_e2
print("s约束循环完成:", time.time()-t0)
