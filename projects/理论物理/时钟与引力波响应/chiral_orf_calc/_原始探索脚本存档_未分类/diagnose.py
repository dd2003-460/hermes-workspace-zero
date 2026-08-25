import sympy as sp
import time

x, s = sp.symbols('x s', real=True)
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

one_plus_nv = s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x + 1
z1 = -(1+uz)*(1+x) / (ux*s)

t0=time.time()
numV_at = numerator_V.subs(z, z1)
print("subs numV done", time.time()-t0)
print("size before expand:", sp.count_ops(numV_at))

t0=time.time()
numV_at_expanded = sp.expand(numV_at)
print("expand done", time.time()-t0, "size:", sp.count_ops(numV_at_expanded))
