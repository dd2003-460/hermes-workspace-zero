"""
用 series 展开代替 limit 来求 R0^V = Res_{z=0} f_V(z) = 系数 of z^0 in (z*f_V(z)) 的展开
"""
import sympy as sp
import numpy as np
import time

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
eCross_uu = 2*theta_dot_u*phi_dot_u
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
eCross_vv = 2*theta_dot_v*phi_dot_v
numerator_V = sp.expand(ePlus_uu*eCross_vv - eCross_uu*ePlus_vv)
n_dot_u = ux*s*(1+z**2)/(2*z) + uz*x
n_dot_v = s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x
one_plus_nu = sp.expand(1+n_dot_u)
one_plus_nv = sp.expand(1+n_dot_v)

# 直接用留数定义: Res_{z=0} f(z) = 分子分母同乘z后的洛朗级数展开中 z^0 系数
# f_V(z) = numerator_V(z) / [i*z*(1+n.u)*(1+n.v)]
# 由于分母含 1/z 项 (来自 (1+z^2)/(2z) 结构), 需要先通分成纯多项式/z^k 形式

# 通分: numerator_V, one_plus_nu, one_plus_nv 各自乘 (2z) 的幂次消掉分母
t0=time.time()
numV_poly = sp.expand(numerator_V * (2*z)**2)   # numerator_V 含 (1/z)^0~2 项(因为是两个二次内积乘积)
onu_poly  = sp.expand(one_plus_nu * (2*z))
onv_poly  = sp.expand(one_plus_nv * (2*z))
print("通分完成:", time.time()-t0)

# f_V(z) = numV_poly / (2z)^2  /  [i*z* onu_poly/(2z) * onv_poly/(2z)]
#        = numV_poly*(2z)^2 / [i*z*(2z)^2*onu_poly*onv_poly] ... 重新代数一下
# f_V(z) = numerator_V/(i*z*one_plus_nu*one_plus_nv)
#        = [numV_poly/(2z)^2] / (i*z* [onu_poly/(2z)] * [onv_poly/(2z)] )
#        = numV_poly/(2z)^2 * (2z)^2/(i*z*onu_poly*onv_poly)
#        = numV_poly / (i*z*onu_poly*onv_poly)
f_V_rational = numV_poly / (sp.I*z*onu_poly*onv_poly)
f_V_rational = sp.together(f_V_rational)
num_r, den_r = sp.fraction(f_V_rational)
num_r = sp.expand(num_r)
den_r = sp.expand(den_r)
print("f_V(z) 化为纯多项式之比: 分子ops=", sp.count_ops(num_r), " 分母ops=", sp.count_ops(den_r))

den_r_poly = sp.Poly(den_r, z)
print("den_r 是否在 z=0 有单重零点? den_r(0)=", den_r_poly.eval(0))
print("d(den_r)/dz|0 =", sp.diff(den_r,z).subs(z,0))

# 用留数公式: Res = num_r(0)/den_r'(0)  (若den_r(0)=0且是单根)
num_r_at0 = num_r.subs(z,0)
den_r_prime_at0 = sp.diff(den_r, z).subs(z, 0)
print("num_r(0) =", num_r_at0)
print("den_r'(0) =", den_r_prime_at0)

if sp.simplify(num_r_at0)==0 and False:
    pass
R0V_formula = num_r_at0/den_r_prime_at0
R0V_formula = sp.simplify(R0V_formula) if sp.count_ops(R0V_formula)<50 else R0V_formula
print("\nR0V (通过 num(0)/den'(0)) =", R0V_formula)

# 数值验证
R0V_func = sp.lambdify((x,s,ux,uz,vx,vy,vz), R0V_formula, modules='numpy')
xv=0.37; sv=np.sqrt(1-xv**2)
duv=1.1; uxv,uzv=np.sin(duv),np.cos(duv)
vxv,vyv,vzv=0.3,-0.5,np.sqrt(1-0.3**2-0.5**2)
val = R0V_func(xv,sv,uxv,uzv,vxv,vyv,vzv)
print("\n数值代入结果:", val)
print("(应与数值围道积分 9.632298+8.940529j 一致)")
