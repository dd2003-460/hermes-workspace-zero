"""
把 ux^2 -> 1-uz^2,  s^2 -> 1-x^2 代入前面算出的四个内积表达式，用 factor 提取公因式
"""
import sympy as sp
import pickle

with open('/home/user/chiral_orf_calc/inner_products_at_z1.pkl','rb') as f:
    d = pickle.load(f)

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

def reduce_expr(expr):
    """反复代入 ux^2->1-uz^2, s^2->1-x^2 直到不再含这两项的高次幂，再factor"""
    e = sp.together(expr)
    num, den = sp.fraction(e)
    num = sp.expand(num)
    den = sp.expand(den)
    # 消去 ux^2 (可能有ux^4等更高次)
    for _ in range(4):
        num = sp.expand(num.subs(ux**2, 1-uz**2))
        den = sp.expand(den.subs(ux**2, 1-uz**2))
    for _ in range(4):
        num = sp.expand(num.subs(s**2, 1-x**2))
        den = sp.expand(den.subs(s**2, 1-x**2))
    result = sp.cancel(num/den)
    return sp.factor(result)

tdu_r = reduce_expr(d['tdu'])
pdu_r = reduce_expr(d['pdu'])
tdv_r = reduce_expr(d['tdv'])
pdv_r = reduce_expr(d['pdv'])

print("theta.u|z1 (化简后) =")
sp.pprint(tdu_r)
print("\nphi.u|z1 (化简后) =")
sp.pprint(pdu_r)
print("\ntheta.v|z1 (化简后) =")
sp.pprint(tdv_r)
print("\nphi.v|z1 (化简后) =")
sp.pprint(pdv_r)

with open('/home/user/chiral_orf_calc/inner_products_reduced.pkl','wb') as f:
    pickle.dump(dict(tdu=tdu_r, pdu=pdu_r, tdv=tdv_r, pdv=pdv_r), f)
