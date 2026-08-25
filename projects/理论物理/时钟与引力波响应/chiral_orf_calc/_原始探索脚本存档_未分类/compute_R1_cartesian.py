"""
回到笛卡尔分量 (ux,uz,vx,vy,vz 独立符号，不代入三角参数化，避免嵌套根式)
用之前诊断过的高效路径: 
  R1V = numerator_V(z1) * 2 / [i * ux*s * (z1-z2) * one_plus_nv(z1)]
分步 cancel/together，避免过早 expand。
"""
import sympy as sp
import time

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

one_plus_nv = s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x + 1

z1 = -(1+uz)*(1+x) / (ux*s)
z2 = -(1-uz)*(1-x) / (ux*s)

print("Step A: 代入 z1 到 numerator_V (不展开，只 together)")
t0=time.time()
numV_z1 = numerator_V.subs(z, z1)
numV_z1 = sp.together(numV_z1)
print("  done", time.time()-t0, "ops:", sp.count_ops(numV_z1))
numV_num, numV_den = sp.fraction(numV_z1)
print("  numerator ops:", sp.count_ops(numV_num), " denominator ops:", sp.count_ops(numV_den))

print("Step B: cancel numV_z1 (约分，而不是simplify)")
t0=time.time()
numV_z1_c = sp.cancel(numV_z1)
print("  done", time.time()-t0, "ops:", sp.count_ops(numV_z1_c))

print("Step C: 代入 z1 到 one_plus_nv")
t0=time.time()
onv_z1 = sp.cancel(sp.together(one_plus_nv.subs(z, z1)))
print("  done", time.time()-t0)
print("  onv_z1 =", onv_z1)

print("Step D: 组装 R1V_raw = numV_z1_c * 2 / (i*ux*s*(z1-z2)*onv_z1)")
t0=time.time()
z1_minus_z2 = sp.cancel(z1 - z2)
print("  z1-z2 =", z1_minus_z2)
denom_total = sp.I*ux*s*z1_minus_z2*onv_z1
R1V_raw = numV_z1_c / denom_total
R1V_raw = sp.cancel(R1V_raw)
print("  done", time.time()-t0, "ops:", sp.count_ops(R1V_raw))
print("\nR1V_raw (未进一步化简) =")
sp.pprint(R1V_raw)

import pickle
with open('/home/user/chiral_orf_calc/R1V_raw.pkl','wb') as f:
    pickle.dump(dict(R1V_raw=R1V_raw), f)
