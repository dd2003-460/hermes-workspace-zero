"""
修正符号错误后的最终组装: z1-z2 = -2(uz+x)/(ux*s)  (而不是之前误用的 +2(x+uz)/(ux*s))
"""
import sympy as sp
import pickle, time
import numpy as np

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

with open('/home/user/chiral_orf_calc/numV_z1_reduced.pkl','rb') as f:
    d = pickle.load(f)
num_reduced, den_reduced = d['num'], d['den']

with open('/home/user/chiral_orf_calc/onv_z1.pkl','rb') as f:
    onv_z1_expr = pickle.load(f)

z1_minus_z2_correct = -2*(uz+x)/(ux*s)   # 修正后

numV_z1_expr = num_reduced/den_reduced

R1V_expr_corrected = (numV_z1_expr * 2) / (sp.I * ux*s * z1_minus_z2_correct * onv_z1_expr)

# 数值检验
xv = 0.37; sv = np.sqrt(1-xv**2)
duv = 1.1; uxv, uzv = np.sin(duv), np.cos(duv)
vxv, vyv, vzv = 0.3, -0.5, np.sqrt(1-0.3**2-0.5**2)

R1V_func = sp.lambdify((x,s,ux,uz,vx,vy,vz), R1V_expr_corrected, modules='numpy')
val = R1V_func(xv,sv,uxv,uzv,vxv,vyv,vzv)
print("修正后符号表达式数值 =", val)
print("(应与数值围道积分 -1.6202942693807483-1.467426502587777j 一致)")

with open('/home/user/chiral_orf_calc/R1V_CORRECTED.pkl','wb') as f:
    pickle.dump(R1V_expr_corrected, f)
