"""
排查 z3,z4 到底该用 (vx - i vy) 还是 (vx + i vy)，以及分子/分母符号是否有误
用 z1,z2 (已验证通过)的结构做类比：
  n_dot_u = ux*sqrt(1-x^2)*(1+z^2)/(2z) + uz*x   (uy=0情形)
  z1 = -(1+uz)(1+x) / [ux*sqrt(1-x^2)]
  
  对于 n_dot_v 完整版 (含uy分量类比):
  n_dot_v = sqrt(1-x^2)/(2z) * [vx(1+z^2) + i*vy(z^2-1)] + vz*x
  
  想找 z 使得 n_dot_v = -1，即
  sqrt(1-x^2)/(2z) * [vx(1+z^2) + i*vy(z^2-1)] = -1 - vz*x
  
  展开: sqrt(1-x^2)*[vx*z^2+vx + i*vy*z^2 - i*vy] = -2z(1+vz*x)
  sqrt(1-x^2)*(vx+i*vy)*z^2 + 2(1+vz*x)*z + sqrt(1-x^2)*(vx-i*vy) = 0
  
  这是关于z的二次方程！用求根公式验证
"""
import sympy as sp
from sympy import I, sqrt, symbols, simplify, expand, solve, sin, cos

x = sp.symbols('x', real=True)
z = sp.symbols('z')
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

n_dot_v = sqrt(1-x**2)/(2*z)*(vx*(1+z**2) + I*vy*(z**2-1)) + vz*x
eq = sp.Eq(n_dot_v, -1)
# 转化为关于z的多项式方程 (两边乘 2z)
lhs_poly = sp.expand(2*z*(n_dot_v+1))
print("多项式方程 (应为0):", lhs_poly, "= 0")

sol = sp.solve(sp.Eq(lhs_poly, 0), z)
print("\n直接用sympy solve得到的两个根:")
for s in sol:
    print(" ", sp.simplify(s))
