"""
用化简后的四个内积表达式，组装 numerator_V|z=z1 = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
"""
import sympy as sp
import pickle

with open('/home/user/chiral_orf_calc/inner_products_reduced.pkl','rb') as f:
    d = pickle.load(f)

x = sp.symbols('x', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

tdu, pdu, tdv, pdv = d['tdu'], d['pdu'], d['tdv'], d['pdv']

ePlus_uu  = sp.factor(tdu**2 - pdu**2)
eCross_uu = sp.factor(2*tdu*pdu)
ePlus_vv  = sp.factor(tdv**2 - pdv**2)
eCross_vv = sp.factor(2*tdv*pdv)

print("e+_ab u^a u^b |z1 =")
sp.pprint(ePlus_uu)
print("\ne×_ab u^a u^b |z1 =")
sp.pprint(eCross_uu)
print("\ne+_cd v^c v^d |z1 =")
sp.pprint(ePlus_vv)
print("\ne×_cd v^c v^d |z1 =")
sp.pprint(eCross_vv)

numerator_V_z1 = sp.together(ePlus_uu*eCross_vv - eCross_uu*ePlus_vv)
numerator_V_z1 = sp.cancel(numerator_V_z1)
numerator_V_z1 = sp.factor(numerator_V_z1)
print("\n" + "="*50)
print("numerator_V(z1) = e+_uu * e×_vv - e×_uu * e+_vv =")
sp.pprint(numerator_V_z1)

with open('/home/user/chiral_orf_calc/numV_z1_final.pkl','wb') as f:
    pickle.dump(numerator_V_z1, f)
