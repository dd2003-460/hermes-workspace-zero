import sympy as sp
import time

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

tdv = (ux*vz*x**2 - ux*vz - uz*vx*x**2 - sp.I*uz*vy*x - vx*x - sp.I*vy*x**2) / (ux*s)
pdv = -(sp.I*uz*vx + uz*vy*x + sp.I*vx*x + vy) / (ux*s)

t0=time.time()
tdv2 = sp.expand(tdv**2)
print("tdv^2 built:", time.time()-t0, "ops=", sp.count_ops(tdv2))
t0=time.time()
pdv2 = sp.expand(pdv**2)
print("pdv^2 built:", time.time()-t0, "ops=", sp.count_ops(pdv2))

t0=time.time()
ePlus_vv = sp.expand(tdv2 - pdv2)
print("ePlus_vv = tdv^2-pdv^2 built:", time.time()-t0, "ops=", sp.count_ops(ePlus_vv))

t0=time.time()
eCross_vv = sp.expand(2*tdv*pdv)
print("eCross_vv built:", time.time()-t0, "ops=", sp.count_ops(eCross_vv))

import pickle
with open('/home/user/chiral_orf_calc/vv_terms.pkl','wb') as f:
    pickle.dump(dict(ePlus_vv=ePlus_vv, eCross_vv=eCross_vv), f)
print("saved")
