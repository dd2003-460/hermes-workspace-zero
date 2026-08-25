import sympy as sp
import time

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)

tdu = -(uz+x)/s
pdu = -sp.I*(uz+x)/s

t0=time.time()
ePlus_uu  = sp.expand(tdu**2 - pdu**2)
print("ePlus_uu built:", time.time()-t0)
print("  ePlus_uu =", ePlus_uu)
eCross_uu = sp.expand(2*tdu*pdu)
print("  eCross_uu =", eCross_uu)
