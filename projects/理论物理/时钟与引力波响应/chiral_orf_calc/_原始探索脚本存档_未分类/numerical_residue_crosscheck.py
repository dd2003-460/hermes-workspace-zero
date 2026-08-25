"""
用直接数值方法计算 Res_{z=z1} f_V(z)（对小圆做数值围道积分），
与前面符号计算得到的 R1V_expr（未完全化简但代数正确）做交叉验证。
这是独立于 sympy 化简能力的"金标准"检验。
"""
import numpy as np
import sympy as sp
import pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

# 重新构造完整的 f_V(z) (符号形式，用于生成数值函数)
theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
eCross_uu = 2*theta_dot_u*phi_dot_u
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
eCross_vv = 2*theta_dot_v*phi_dot_v

numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
n_dot_u = ux*s*(1+z**2)/(2*z) + uz*x
n_dot_v = s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x
f_V = numerator_V / (sp.I*z*(1+n_dot_u)*(1+n_dot_v))

f_V_func = sp.lambdify((x, s, ux, uz, vx, vy, vz, z), f_V, modules='numpy')

def numerical_residue(z1_val, params, radius=1e-4, N=4000):
    """在 z1_val 附近做小圆围道积分: Res = (1/2pi i) * oint f(z) dz"""
    xv, sv, uxv, uzv, vxv, vyv, vzv = params
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = z1_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = f_V_func(xv, sv, uxv, uzv, vxv, vyv, vzv, zs)
    integral = np.sum(vals*dz)
    return integral/(2j*np.pi)

# 选一组随机测试参数
np.random.seed(2024)
xv = 0.37
sv = np.sqrt(1-xv**2)
duv = 1.1  # delta_u
uxv, uzv = np.sin(duv), np.cos(duv)
vvec = np.array([0.3, -0.5, np.sqrt(1-0.3**2-0.5**2)])
vxv, vyv, vzv = vvec

z1_val = -(1+uzv)*(1+xv) / (uxv*sv)
print("z1 数值 =", z1_val)

res_numeric = numerical_residue(z1_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
print("数值围道积分得到的 Res_z1 f_V =", res_numeric)

# 用前面符号计算的未化简 R1V 表达式代入同样数值，比较
with open('/home/user/chiral_orf_calc/numV_z1_reduced.pkl','rb') as f:
    d = pickle.load(f)
num_reduced, den_reduced = d['num'], d['den']
numV_z1_expr = num_reduced/den_reduced   # = numerator_V(z1)

with open('/home/user/chiral_orf_calc/onv_z1.pkl','rb') as f:
    onv_z1_expr = pickle.load(f)

z1_minus_z2_expr = 2*(x+uz)/(ux*s)

R1V_expr = (numV_z1_expr * 2) / (sp.I * ux*s * z1_minus_z2_expr * onv_z1_expr)

R1V_func = sp.lambdify((x,s,ux,uz,vx,vy,vz), R1V_expr, modules='numpy')
res_symbolic = R1V_func(xv,sv,uxv,uzv,vxv,vyv,vzv)
print("符号表达式(未化简)代入数值得到的 R1V =", res_symbolic)

print("\n两者相对误差 =", abs(res_numeric-res_symbolic)/abs(res_symbolic))

print("\n" + "="*60)
print("修正符号后对比 (加负号):")
print("数值:", res_numeric)
print("符号(加负号):", -res_symbolic)
print("相对误差:", abs(res_numeric - (-res_symbolic))/abs(res_symbolic))
