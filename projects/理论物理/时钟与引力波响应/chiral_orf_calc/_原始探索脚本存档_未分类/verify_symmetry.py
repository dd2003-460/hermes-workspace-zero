"""
验证关键对称性: xi_V(u,v) = - xi_V(v,u)  (交换u,v整体反号)
如果成立，则 R3^V(u,v) = -R1^V(v,u), R4^V(u,v) = -R2^V(v,u)，
可以只算 R0,R1,R2 ，再用对称性得到 R3,R4，节省一半算力。
"""
import sympy as sp
import random

x = sp.symbols('x', real=True)
z = sp.symbols('z')
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

def build_numerator_V(UX,UZ,VX,VY,VZ):
    theta_dot_u = UX*x*(1+z**2)/(2*z) - UZ*sp.sqrt(1-x**2)
    phi_dot_u   = sp.I*UX*(z**2-1)/(2*z)
    theta_dot_v = VX*x*(1+z**2)/(2*z) + sp.I*VY*x*(z**2-1)/(2*z) - VZ*sp.sqrt(1-x**2)
    phi_dot_v   = sp.I*VX*(z**2-1)/(2*z) + VY*(1+z**2)/(2*z)
    ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
    eCross_uu = 2*theta_dot_u*phi_dot_u
    ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
    eCross_vv = 2*theta_dot_v*phi_dot_v
    return ePlus_uu*eCross_vv - eCross_uu*ePlus_vv

numV_uv = build_numerator_V(ux,uz,vx,vy,vz)
numV_vu = build_numerator_V(vx,vz,ux,uy:=sp.Symbol('u_y_dummy'),uz)  # placeholder, fix below
