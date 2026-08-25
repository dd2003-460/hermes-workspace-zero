"""
计算 one_plus_nv(z1) = 1 + n.v |_{z=z1}, 用 expand 而非 factor
"""
import sympy as sp
import time, pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

z1 = -(1+uz)*(1+x) / (ux*s)
one_plus_nv = s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x + 1

t0=time.time()
onv_z1 = one_plus_nv.subs(z, z1)
onv_z1 = sp.together(onv_z1)
num, den = sp.fraction(onv_z1)
num = sp.expand(num)
den = sp.expand(den)
print("onv_z1 num/den built:", time.time()-t0)
print("den =", den)

# 用约束降幂
for _ in range(6):
    num = sp.expand(num.subs(ux**2, 1-uz**2))
    den = sp.expand(den.subs(ux**2, 1-uz**2))
for _ in range(6):
    num = sp.expand(num.subs(s**2, 1-x**2))
    den = sp.expand(den.subs(s**2, 1-x**2))

onv_z1_reduced = sp.cancel(num/den)
print("\none_plus_nv(z1) (化简) =")
sp.pprint(onv_z1_reduced)

with open('/home/user/chiral_orf_calc/onv_z1.pkl','wb') as f:
    pickle.dump(onv_z1_reduced, f)
