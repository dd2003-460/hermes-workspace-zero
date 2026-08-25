import sympy as sp
import time, sys

x, s = sp.symbols('x s', real=True, positive=True)
z = sp.symbols('z')
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
eCross_uu = 2*theta_dot_u*phi_dot_u
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
eCross_vv = 2*theta_dot_v*phi_dot_v

numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv

z1 = -(1+uz)*(1+x) / (ux*s)
numV_z1 = numerator_V.subs(z, z1)
print("numV_z1 built, ops=", sp.count_ops(numV_z1)); sys.stdout.flush()

print("trying cancel() directly on un-expanded form (timeout risk)..."); sys.stdout.flush()
t0=time.time()
try:
    res = sp.cancel(numV_z1)
    print("cancel done:", time.time()-t0, "ops=", sp.count_ops(res))
except Exception as e:
    print("failed:", e)
