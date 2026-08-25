"""
最终组装:
R1^V = Res_{z=z1} f_V(z)
     = numerator_V(z1) * 2 / [i * (ux*s) * (z1-z2) * one_plus_nv(z1)]

已知:
  numerator_V(z1) = num_reduced / (s^4 * ux^2)     [来自 numV_z1_reduced.pkl]
  z1 - z2 = 2(x+uz)/(ux*s)                          [韦达定理，已验证]
  one_plus_nv(z1) = [ux*vz*x + ux - uz*vx*x - i*uz*vy - vx - i*vy*x] / ux
"""
import sympy as sp
import pickle, time

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

with open('/home/user/chiral_orf_calc/numV_z1_reduced.pkl','rb') as f:
    d = pickle.load(f)
num_reduced, den_reduced = d['num'], d['den']   # den_reduced = s^4 * ux^2
print("den_reduced (numerator_V的分母部分) =", den_reduced)

with open('/home/user/chiral_orf_calc/onv_z1.pkl','rb') as f:
    onv_z1 = pickle.load(f)

z1_minus_z2 = 2*(x+uz)/(ux*s)

# R1V = [num_reduced/den_reduced] * 2 / [i * ux*s * z1_minus_z2 * onv_z1]
t0=time.time()
denom_total = sp.I * ux * s * z1_minus_z2 * onv_z1
denom_total = sp.together(denom_total)
print("denom_total built:", time.time()-t0)
print("denom_total =", denom_total)

R1V = (num_reduced/den_reduced) * 2 / denom_total
R1V = sp.together(R1V)
print("\nR1V (未化简) 组装完成, ops=", sp.count_ops(R1V))

t0 = time.time()
num_R1V, den_R1V = sp.fraction(R1V)
num_R1V = sp.expand(num_R1V)
den_R1V = sp.expand(den_R1V)
print("fraction+expand done:", time.time()-t0)
print("num ops:", sp.count_ops(num_R1V), " den ops:", sp.count_ops(den_R1V))

# 再次用约束降幂化简
for _ in range(6):
    num_R1V = sp.expand(num_R1V.subs(ux**2, 1-uz**2))
    den_R1V = sp.expand(den_R1V.subs(ux**2, 1-uz**2))
for _ in range(6):
    num_R1V = sp.expand(num_R1V.subs(s**2, 1-x**2))
    den_R1V = sp.expand(den_R1V.subs(s**2, 1-x**2))

R1V_reduced = sp.cancel(num_R1V/den_R1V)
print("\nR1V_reduced =")
sp.pprint(R1V_reduced)

with open('/home/user/chiral_orf_calc/R1V_FINAL.pkl','wb') as f:
    pickle.dump(R1V_reduced, f)
