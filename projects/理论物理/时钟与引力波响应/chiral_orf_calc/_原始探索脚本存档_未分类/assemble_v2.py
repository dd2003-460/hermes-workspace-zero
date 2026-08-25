"""
把 sqrt(1-x)*sqrt(1+x) 统一替换回单一符号 s (s=sqrt(1-x^2))，避免sympy处理两个独立根式的组合爆炸
"""
import sympy as sp
import time

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

# 直接手写化简后的内积表达式（对照上一步结果，把 sqrt(1-x)*sqrt(1+x) 替换为 s）
tdu = -(uz+x)/s
pdu = -sp.I*(uz+x)/s
tdv = (ux*vz*x**2 - ux*vz - uz*vx*x**2 - sp.I*uz*vy*x - vx*x - sp.I*vy*x**2) / (ux*s)
pdv = -(sp.I*uz*vx + uz*vy*x + sp.I*vx*x + vy) / (ux*s)

t0=time.time()
ePlus_uu  = sp.expand(tdu**2 - pdu**2)
eCross_uu = sp.expand(2*tdu*pdu)
print("ePlus_uu, eCross_uu built:", time.time()-t0)
print("  ePlus_uu =", ePlus_uu)
print("  eCross_uu =", eCross_uu)

t0=time.time()
ePlus_vv  = sp.expand(tdv**2 - pdv**2)
eCross_vv = sp.expand(2*tdv*pdv)
print("\nePlus_vv, eCross_vv built:", time.time()-t0, " ops=", sp.count_ops(ePlus_vv), sp.count_ops(eCross_vv))

t0=time.time()
numerator_V_z1 = sp.expand(ePlus_uu*eCross_vv - eCross_uu*ePlus_vv)
print("\nnumerator_V(z1) built:", time.time()-t0, "ops=", sp.count_ops(numerator_V_z1))

t0=time.time()
numerator_V_z1_factored = sp.factor(numerator_V_z1)
print("factor done:", time.time()-t0)
print("\nnumerator_V(z1) factored =")
sp.pprint(numerator_V_z1_factored)

import pickle
with open('/home/user/chiral_orf_calc/numV_z1_v2.pkl','wb') as f:
    pickle.dump(numerator_V_z1_factored, f)
