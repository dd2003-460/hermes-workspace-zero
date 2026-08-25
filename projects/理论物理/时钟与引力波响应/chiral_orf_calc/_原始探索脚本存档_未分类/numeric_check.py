"""数值检验: z3,z4的表达式是否真的对任意 x,delta_v,psi 都恒为零"""
import sympy as sp
from sympy import I, sqrt, sin, cos
import random

x = sp.symbols('x', real=True)
z = sp.symbols('z')
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

n_dot_v = sqrt(1-x**2)/(2*z)*(vx*(1+z**2) + I*vy*(z**2-1)) + vz*x
z3 = -(1+vz)*(1+x) / ((vx - I*vy)*sqrt(1-x**2))
z4 = -(1-vz)*(1-x) / ((vx - I*vy)*sqrt(1-x**2))
one_plus_nv = 1 + n_dot_v

du, dv, psi = sp.symbols('delta_u delta_v psi', real=True)
subs_v = {vx: sin(dv)*cos(psi), vy: sin(dv)*sin(psi), vz: cos(dv)}

expr3 = one_plus_nv.subs(z, z3).subs(subs_v)
expr4 = one_plus_nv.subs(z, z4).subs(subs_v)

random.seed(42)
for trial in range(5):
    xv  = random.uniform(-0.9, 0.9)
    dvv = random.uniform(0.1, 3.0)
    psiv = random.uniform(0.1, 6.0)
    val3 = complex(expr3.subs({x:xv, dv:dvv, psi:psiv}).evalf())
    val4 = complex(expr4.subs({x:xv, dv:dvv, psi:psiv}).evalf())
    print(f"trial {trial}: x={xv:.3f} dv={dvv:.3f} psi={psiv:.3f}  -> (1+n.v)|z3={val3:.6g}   (1+n.v)|z4={val4:.6g}")
