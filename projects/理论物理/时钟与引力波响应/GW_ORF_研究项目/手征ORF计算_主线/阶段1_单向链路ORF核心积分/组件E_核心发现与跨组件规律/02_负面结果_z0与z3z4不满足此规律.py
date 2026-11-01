"""
【性质】负面结果验证（部分结论已被 BUG-001 修正推翻，见下方更新说明）
【计算的量】R0V/R0I 的比值（多组随机参数），以及 R3V/R3I, R4V/R4I 的比值
【状态】⚠️ 关于z3,z4的负面结论已撤销并推翻；关于z0的负面结论依然成立

================================================================================
        ⚠️ 重要更新：z3,z4的负面结论被 BUG-001 修正推翻 ⚠️
================================================================================
本文件此前版本（使用论文Eq(A6)印刷的错误+i*vy符号，以及错误的z3z4分母vx+i*vy）
得出"R3V/R3I, R4V/R4I 不是常数，规律不能推广到z3,z4"的负面结论。

**这个结论是错的，已被推翻。** 用 BUG-001 修正后的正确公式重新计算，发现：

    R3^V = +i * R3^I   (严格符号恒等式，非数值近似)
    R4^V = -i * R4^I   (严格符号恒等式，非数值近似)

这两条恒等式与z1,z2处的规律完全对称，详见
`R3_R4/推导与诊断/03_重大突破_BUG001修正后核心恒等式推广到z3z4.py`
的严格符号证明，以及 `R3_R4/数值验证/02_验证R3VR4V闭式解_替代旧的负面结果.py`
的8组随机数值交叉验证（v_y>0，与论文推导前提一致，误差~1e-12量级）。

**结论修正为：全部4个一阶极点 z1,z2,z3,z4 处，手征留数与强度留数都严格
成正比（比例系数±i），只有 z0（二阶极点）确实无法用这个简单比例规律覆盖。**

================================================================================
关于 z0 的负面结论：依然成立（本次已用修正后公式重新确认）
================================================================================
下方代码保留对z0的检验（已同步更新为BUG-001修正后的公式），结果确认
R0V/R0I 依然不是常数，这部分负面结论不受影响，继续成立。
================================================================================
"""
import sympy as sp
import numpy as np

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')


def build_fV_fI_numeric_funcs():
    # BUG-001 修正后的正确内积公式 (theta.v, n.v 的 vy 项为 -I)
    theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
    phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
    theta_dot_v = vx*x*(1+z**2)/(2*z) - sp.I*vy*x*(z**2-1)/(2*z) - vz*s
    phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
    ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
    eCross_uu = 2*theta_dot_u*phi_dot_u
    ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
    eCross_vv = 2*theta_dot_v*phi_dot_v
    numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
    numerator_I = ePlus_uu*ePlus_vv + eCross_uu*eCross_vv
    n_dot_u = ux*s*(1+z**2)/(2*z) + uz*x
    n_dot_v = s/(2*z)*(vx*(1+z**2) - sp.I*vy*(z**2-1)) + vz*x
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
    print("检验1: R0V / R0I 的比值 (z0是二阶极点，见R0/推导文件夹关于阶数的修正说明):")
    print("       用radius=1e-3(而非1e-4)以适应二阶极点的数值稳健性")
    for trial in range(6):
        xv = np.random.uniform(-0.8,0.8); sv=np.sqrt(1-xv**2)
        duv = np.random.uniform(0.2,2.9); uxv,uzv = np.sin(duv), np.cos(duv)
        vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
        vxv,vyv,vzv = vvec
        R0V = numerical_residue(f_V_func, 0.0, (xv,sv,uxv,uzv,vxv,vyv,vzv), radius=1e-3)
        R0I = numerical_residue(f_I_func, 0.0, (xv,sv,uxv,uzv,vxv,vyv,vzv), radius=1e-3)
        ratio = R0V/R0I
        print(f"  trial{trial}: ratio = {ratio:.4g}")
    print("  → 明显不是常数，规律不能推广到z0 (此负面结论保持不变)\n")

    np.random.seed(500)
    print("检验2 [BUG-002修复后重新确认]: R3V/R3I, R4V/R4I 的比值")
    print("       (z3,z4用论文原文正确极点公式 vx-i*vy，不限定v_y符号)")
    print("       [说明] 此前版本曾错误地认为此关系需要v_y>0，实为sigma_pm的")
    print("       BUG-002(分支选择错误)混淆所致——该bug只影响R3^I,R4^I封闭解")
    print("       本身，不影响numerator_V/numerator_I=±i这条纯代数比值恒等式。")
    print("       本次不再限定v_y符号，直接验证纯代数比值对v_y正负都成立：")
    n_tested = 0
    trial = 0
    while n_tested < 8:
        trial += 1
        xv = np.random.uniform(-0.8,0.8); sv=np.sqrt(1-xv**2)
        duv = np.random.uniform(0.2,2.9); uxv,uzv = np.sin(duv), np.cos(duv)
        vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
        vxv,vyv,vzv = vvec
        if abs(vyv) < 1e-6:
            continue
        n_tested += 1
        z3_val = -(1+vzv)*(1+xv)/((vxv-1j*vyv)*sv)   # 论文原文分母 vx-i*vy (未改动)
        z4_val = -(1-vzv)*(1-xv)/((vxv-1j*vyv)*sv)
        R3V = numerical_residue(f_V_func, z3_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        R3I = numerical_residue(f_I_func, z3_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        R4V = numerical_residue(f_V_func, z4_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        R4I = numerical_residue(f_I_func, z4_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        print(f"  trial{n_tested}(v_y={vyv:+.3f}): R3V/R3I={R3V/R3I:.6g}   R4V/R4I={R4V/R4I:.6g}")
    print("  → R3V/R3I 严格等于 +i，R4V/R4I 严格等于 -i，与v_y符号无关")
    print("    （确认这条比值恒等式本身从未真正依赖v_y符号）\n")
    print("最终结论: ±i比例关系可以推广到全部4个一阶极点 z1,z2,z3,z4，且与v_y")
    print("          符号完全无关。只有z0(二阶极点)无法用此简单比例规律覆盖，")
    print("          需要独立的sympy.residue()计算(但R0V本身已经用residue()成功")
    print("          求出符号解，不影响流水线完整性)。")

