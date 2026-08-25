"""
对已经expand好的 numerator_V(z1) ，手动提取公因子 1/(s^4 * ux^2)，
并对分子多项式用约束反复替代降幂，最后尝试 factor (此时规模应该已经大幅减小)
"""
import sympy as sp
import time, pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

with open('/home/user/chiral_orf_calc/numV_z1_expanded.pkl','rb') as f:
    numV = pickle.load(f)

t0=time.time()
numV_together = sp.together(numV)
print("together done:", time.time()-t0)
num, den = sp.fraction(numV_together)
print("den =", den)
print("num ops (before reduction):", sp.count_ops(num))

# 反复用约束降幂: ux^2 -> 1-uz^2,  s^2 -> 1-x^2
num_reduced = sp.expand(num)
t0=time.time()
for _ in range(6):
    num_reduced = sp.expand(num_reduced.subs(ux**2, 1-uz**2))
for _ in range(6):
    num_reduced = sp.expand(num_reduced.subs(s**2, 1-x**2))
print("reduction done:", time.time()-t0, "ops now:", sp.count_ops(num_reduced))

print("\nnum_reduced =")
sp.pprint(num_reduced)

with open('/home/user/chiral_orf_calc/numV_z1_reduced.pkl','wb') as f:
    pickle.dump(dict(num=num_reduced, den=den), f)
