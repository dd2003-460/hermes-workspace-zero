"""
【性质】负面结果验证（同样重要）—— 检验-i比例关系是否可推广到z0, z3, z4
【计算的量】R0V/R0I 的比值（多组随机参数），以及 R3V/R3I, R4V/R4I 的比值
【状态】✅ 明确的、诚实的负面结果：不能推广，但划定了适用边界并发现了新规律

═══════════════════════════════════════════════════════════════
为什么要做这个检验
═══════════════════════════════════════════════════════════════
01文件已经证明"-i比例关系"在z1,z2(由u单独决定的一阶极点)上成立。
一个自然的问题是：这个漂亮的规律能不能推广到z0(原点)和z3,z4(由v决定的极点)？
如果能推广，意味着整个 I_1^V 母函数都可以直接从 I_1^I 通过简单的
虚数比例关系得到，会带来巨大的简化。

═══════════════════════════════════════════════════════════════
检验结果：不能推广
═══════════════════════════════════════════════════════════════
- z0 (三阶极点): R0V/R0I 在6组随机参数下分别是
  -0.32+0.85j, 0.076+1.01j, 0.77-3.23j, -0.055+1.02j, 0.26-0.51j, 0.074-0.81j
  —— 明显不是常数。

- z3,z4 (v决定的极点): R3V/R3I, R4V/R4I 同样在不同参数下变化很大，
  不是常数（但发现了新的共轭对称性，见05文件夹）。

═══════════════════════════════════════════════════════════════
物理解读
═══════════════════════════════════════════════════════════════
"-i比例关系"依赖于两个特殊条件同时满足：
  (1) 该极点是简单的一阶极点(z0是三阶极点，不满足)
  (2) 该极点由u或v单独决定，"另一方"(比如z1,z2处的v)以一般形式
      出现在留数公式里，不参与比例关系的形成

这提示"-i比例关系"是这个特殊几何结构的产物，不是一个可以覆盖全部
5个极点的普适规律。这个负面结果同样有价值：它明确划定了
"手征ORF可以直接从强度ORF简单缩放得到"这条化简捷径的适用边界——
只在I_1^V的z1,z2部分适用，z0,z3,z4部分仍需独立计算。
"""
import sympy as sp
import numpy as np

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')


def build_fV_fI_numeric_funcs():
    theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
    phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
    theta_dot_v = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
    phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
    ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
    eCross_uu = 2*theta_dot_u*phi_dot_u
    ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
    eCross_vv = 2*theta_dot_v*phi_dot_v
    numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
    numerator_I = ePlus_uu*ePlus_vv + eCross_uu*eCross_vv
    n_dot_u = ux*s*(1+z**2)/(2*z) + uz*x
    n_dot_v = s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x
    f_V = numerator_V/(sp.I*z*(1+n_dot_u)*(1+n_dot_v))
    f_I = numerator_I/(sp.I*z*(1+n_dot_u)*(1+n_dot_v))
    f_V_func = sp.lambdify((x, s, ux, uz, vx, vy, vz, z), f_V, modules='numpy')
    f_I_func = sp.lambdify((x, s, ux, uz, vx, vy, vz, z), f_I, modules='numpy')
    return f_V_func, f_I_func


def numerical_residue(func, z0_val, params, radius=1e-4, N=8000):
    xv, sv, uxv, uzv, vxv, vyv, vzv = params
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = z0_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = func(xv, sv, uxv, uzv, vxv, vyv, vzv, zs)
    return np.sum(vals*dz)/(2j*np.pi)


if __name__ == "__main__":
    f_V_func, f_I_func = build_fV_fI_numeric_funcs()

    np.random.seed(400)
    print("检验1: R0V / R0I 的比值 (z0是三阶极点):")
    for trial in range(6):
        xv = np.random.uniform(-0.8,0.8); sv=np.sqrt(1-xv**2)
        duv = np.random.uniform(0.2,2.9); uxv,uzv = np.sin(duv), np.cos(duv)
        vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
        vxv,vyv,vzv = vvec
        R0V = numerical_residue(f_V_func, 0.0, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        R0I = numerical_residue(f_I_func, 0.0, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        ratio = R0V/R0I
        print(f"  trial{trial}: ratio = {ratio:.4g}")
    print("  → 明显不是常数，规律不能推广到z0\n")

    np.random.seed(500)
    print("检验2: R3V/R3I, R4V/R4I 的比值 (z3,z4是v决定的极点):")
    for trial in range(6):
        xv = np.random.uniform(-0.8,0.8); sv=np.sqrt(1-xv**2)
        duv = np.random.uniform(0.2,2.9); uxv,uzv = np.sin(duv), np.cos(duv)
        vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
        vxv,vyv,vzv = vvec
        z3_val = -(1+vzv)*(1+xv)/((vxv+1j*vyv)*sv)
        z4_val = -(1-vzv)*(1-xv)/((vxv+1j*vyv)*sv)
        R3V = numerical_residue(f_V_func, z3_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        R3I = numerical_residue(f_I_func, z3_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        R4V = numerical_residue(f_V_func, z4_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        R4I = numerical_residue(f_I_func, z4_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        print(f"  trial{trial}: R3V/R3I={R3V/R3I:.4g}   R4V/R4I={R4V/R4I:.4g}")
    print("  → 同样不是常数，规律也不能推广到z3,z4")
    print("\n结论: -i比例关系只在z1,z2 (由u单独决定的一阶极点) 成立，")
    print("      这明确了后续计算 Gamma_one^V 时哪部分可以走捷径、哪部分仍需硬算。")
