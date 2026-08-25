import sympy as sp
from sympy import I, sqrt, sin, cos, symbols, simplify, expand, exp, re, im, nsimplify
import pickle

with open('/home/user/chiral_orf_calc/poles.pkl', 'rb') as f:
    d = pickle.load(f)

x, z = d['x'], d['z']
ux, uz, vx, vy, vz = d['ux'], d['uz'], d['vx'], d['vy'], d['vz']
n_dot_v = d['n_dot_v']
z3, z4 = d['z3'], d['z4']

one_plus_nv = 1 + n_dot_v
du, dv, psi = symbols('delta_u delta_v psi', real=True)
subs_u = {ux: sin(du), uz: cos(du)}
subs_v = {vx: sin(dv)*cos(psi), vy: sin(dv)*sin(psi), vz: cos(dv)}

expr3 = one_plus_nv.subs(z, z3).subs(subs_v).subs(subs_u)
expr3_simpl = sp.nsimplify(sp.simplify(sp.expand_complex(expr3)))
print("z3 check =", expr3_simpl)

expr4 = one_plus_nv.subs(z, z4).subs(subs_v).subs(subs_u)
expr4_simpl = sp.nsimplify(sp.simplify(sp.expand_complex(expr4)))
print("z4 check =", expr4_simpl)
