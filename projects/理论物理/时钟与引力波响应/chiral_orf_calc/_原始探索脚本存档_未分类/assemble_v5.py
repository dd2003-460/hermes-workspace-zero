import sympy as sp
import time, pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

ePlus_uu  = 2*uz**2/s**2 + 4*uz*x/s**2 + 2*x**2/s**2
eCross_uu = 2*sp.I*uz**2/s**2 + 4*sp.I*uz*x/s**2 + 2*sp.I*x**2/s**2

with open('/home/user/chiral_orf_calc/vv_terms.pkl','rb') as f:
    vv = pickle.load(f)
ePlus_vv, eCross_vv = vv['ePlus_vv'], vv['eCross_vv']

t0=time.time()
term1 = sp.expand(ePlus_uu * eCross_vv)
print("term1 = ePlus_uu*eCross_vv built:", time.time()-t0, "ops=", sp.count_ops(term1))

t0=time.time()
term2 = sp.expand(eCross_uu * ePlus_vv)
print("term2 = eCross_uu*ePlus_vv built:", time.time()-t0, "ops=", sp.count_ops(term2))

t0=time.time()
numerator_V_z1 = sp.expand(term1 - term2)
print("numerator_V(z1) = term1-term2 built:", time.time()-t0, "ops=", sp.count_ops(numerator_V_z1))
print()
print("numerator_V(z1) =")
sp.pprint(numerator_V_z1)

with open('/home/user/chiral_orf_calc/numV_z1_expanded.pkl','wb') as f:
    pickle.dump(numerator_V_z1, f)
