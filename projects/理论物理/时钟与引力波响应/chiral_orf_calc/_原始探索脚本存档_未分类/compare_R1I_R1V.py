"""
用同样高效流程计算对称情形的 R1^I (强度ORF在z1处的留数)，
与已严格验证的 R1^V 做结构对比，观察奇偶项差异 (这是任务的核心科学问题)
"""
import sympy as sp
import numpy as np
import time, pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

z1 = -(1+uz)*(1+x) / (ux*s)
z2 = -(1-uz)*(1-x) / (ux*s)

theta_dot_u_expr = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u_expr   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v_expr = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v_expr   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

def sub_reduce(expr, zk):
    val = sp.together(expr.subs(z, zk))
    num, den = sp.fraction(val)
    num = sp.expand(num); den = sp.expand(den)
    for _ in range(6):
        num = sp.expand(num.subs(ux**2, 1-uz**2)); den = sp.expand(den.subs(ux**2, 1-uz**2))
    for _ in range(6):
        num = sp.expand(num.subs(s**2, 1-x**2)); den = sp.expand(den.subs(s**2, 1-x**2))
    return sp.cancel(num/den)

tdu1 = sub_reduce(theta_dot_u_expr, z1)
pdu1 = sub_reduce(phi_dot_u_expr, z1)
tdv1 = sub_reduce(theta_dot_v_expr, z1)
pdv1 = sub_reduce(phi_dot_v_expr, z1)

ePlus_uu1  = sp.expand(tdu1**2 - pdu1**2)
eCross_uu1 = sp.expand(2*tdu1*pdu1)
ePlus_vv1  = sp.expand(tdv1**2 - pdv1**2)
eCross_vv1 = sp.expand(2*tdv1*pdv1)

# --- 对称核 (强度ORF): numerator_I = ePlus_uu*ePlus_vv + eCross_uu*eCross_vv ---
numerator_I_z1 = sp.expand(ePlus_uu1*ePlus_vv1 + eCross_uu1*eCross_vv1)
numI_t = sp.together(numerator_I_z1)
numI, denI = sp.fraction(numI_t)
numI = sp.expand(numI); denI = sp.expand(denI)
for _ in range(6):
    numI = sp.expand(numI.subs(ux**2, 1-uz**2)); denI = sp.expand(denI.subs(ux**2, 1-uz**2))
for _ in range(6):
    numI = sp.expand(numI.subs(s**2, 1-x**2)); denI = sp.expand(denI.subs(s**2, 1-x**2))

print("numerator_I(z1) 分母:", denI)
print("\nnumerator_I(z1) 分子按x收集:")
numI_collected = sp.collect(numI, x)
sp.pprint(numI_collected)

# --- 反对称核 (手征ORF, 已验证): numerator_V(z1) ---
with open('/home/user/chiral_orf_calc/numV_z1_reduced.pkl','rb') as f:
    d = pickle.load(f)
numV, denV = d['num'], d['den']
print("\n" + "="*60)
print("numerator_V(z1) 分母:", denV)
print("\nnumerator_V(z1) 分子按x收集:")
numV_collected = sp.collect(numV, x)
sp.pprint(numV_collected)

# --- 比较两者关于 x 的最高次数、是否有系统性的奇偶项消去 ---
polyI = sp.Poly(numI, x)
polyV = sp.Poly(numV, x)
print("\n" + "="*60)
print("numerator_I(z1) 关于x的次数:", polyI.degree())
print("numerator_V(z1) 关于x的次数:", polyV.degree())

print("\nnumerator_I(z1) 各次幂的系数 (x^0,x^1,x^2,...):")
coeffsI = polyI.all_coeffs()[::-1]
for i,c in enumerate(coeffsI):
    nonzero = "非零" if sp.simplify(c)!=0 else "  零"
    print(f"  x^{i}: [{nonzero}]")

print("\nnumerator_V(z1) 各次幂的系数 (x^0,x^1,x^2,...):")
coeffsV = polyV.all_coeffs()[::-1]
for i,c in enumerate(coeffsV):
    nonzero = "非零" if sp.simplify(c)!=0 else "  零"
    print(f"  x^{i}: [{nonzero}]")
