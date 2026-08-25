"""
用正确符号 (vx + i*vy) 重新定义 z3, z4，并严格验证
"""
import sympy as sp
from sympy import I, sqrt, symbols, simplify, expand, sin, cos

x = sp.symbols('x', real=True)
z = sp.symbols('z')
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

n_dot_v = sqrt(1-x**2)/(2*z)*(vx*(1+z**2) + I*vy*(z**2-1)) + vz*x

z3_fixed = -(1+vz)*(1+x) / ((vx + I*vy)*sqrt(1-x**2))
z4_fixed = -(1-vz)*(1-x) / ((vx + I*vy)*sqrt(1-x**2))

one_plus_nv = 1 + n_dot_v

du, dv, psi = sp.symbols('delta_u delta_v psi', real=True)
subs_v = {vx: sin(dv)*cos(psi), vy: sin(dv)*sin(psi), vz: cos(dv)}

expr3 = one_plus_nv.subs(z, z3_fixed).subs(subs_v)
expr4 = one_plus_nv.subs(z, z4_fixed).subs(subs_v)

val3 = sp.simplify(sp.expand_complex(expr3))
val4 = sp.simplify(sp.expand_complex(expr4))
print("修正后 (1+n.v) at z3_fixed =", val3)
print("修正后 (1+n.v) at z4_fixed =", val4)

# 数值再次抽查
import random
random.seed(7)
print("\n数值抽查:")
for trial in range(5):
    xv  = random.uniform(-0.9, 0.9)
    dvv = random.uniform(0.1, 3.0)
    psiv = random.uniform(0.1, 6.0)
    v3 = complex(expr3.subs({x:xv, dv:dvv, psi:psiv}).evalf())
    v4 = complex(expr4.subs({x:xv, dv:dvv, psi:psiv}).evalf())
    print(f"  x={xv:.3f} dv={dvv:.3f} psi={psiv:.3f}  (1+n.v)|z3={v3:.3e}  (1+n.v)|z4={v4:.3e}")
