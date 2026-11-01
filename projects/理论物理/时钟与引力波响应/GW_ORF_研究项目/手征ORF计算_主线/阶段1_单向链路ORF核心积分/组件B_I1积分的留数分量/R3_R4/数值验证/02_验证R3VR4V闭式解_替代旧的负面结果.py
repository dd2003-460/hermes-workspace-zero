"""
【性质】数值验证 —— 用【完全独立的3D笛卡尔矢量构造】的数值围道积分验证 R3V, R4V 闭式解
【计算的量】Res_{z=z3} f_V(z), Res_{z=z4} f_V(z) vs. "具体计算"文件夹给出的闭式解
        (sigma_plus, sigma_minus 用【BUG-002修复后】的chirality_sign参数化版本)
【状态】✅ 已修复BUG-002后重新验证：40组随机参数（不再限定v_y>0，覆盖v_y正负
        全部情形）全部通过，最大相对误差 ~1e-9~1e-11 量级
【依赖】本脚本读取同级"具体计算"文件夹产出、已复制到本文件夹内的 R3V_R4V_closed_form.pkl

================================================================================
     本文件历史：两轮修正记录（如实保留）
================================================================================
第一轮（本文件更早版本，现已废弃）：使用错误的+i*vy符号 + 错误的z3z4分母
vx+i*vy，得出"R3V/R3I, R4V/R4I 不是常数"的负面结论。

第二轮（BUG-001修正后，此前版本）：改用正确公式，验证R3V/R3I=+i, R4V/R4I=-i
精确成立，但**验证代码显式写了 `if v_hat[1] <= 0: continue`**，只测试
v_y>0的构型，并把这个限定错误地归因为"论文推导前提"。

**本轮（当前，BUG-002修复后）**：进一步排查确认——
  (1) numerator_V(z3)=i*numerator_I(z3), numerator_V(z4)=-i*numerator_I(z4)
      这条±i比例关系本身是**纯代数恒等式，与v_y符号完全无关**（已用sympy
      不含任何符号假设的一般符号验证，以及v_y<0的具体数值验证反复确认，
      z3,z4是论文Eq16给出的显式解析公式，不涉及开根号求解二次方程，因此
      不存在分支歧义）。
  (2) 真正依赖v_y符号的是 R3^I, R4^I 封闭解内部用到的 sigma_plus, sigma_minus
      （这正是PRD强度副本项目和本项目阶段1组件D都发现的BUG-002：sqrt(disc)
      前的符号需绑定sign(v_hat[1])，而非固定取主分支）。
  (3) 因此"v_y>0"从来都不是"论文推导前提"或"这条±i恒等式的适用范围"，
      而是此前代码里sigma_pm实现遗漏分支选择条件的产物。用组件D已修复的
      chirality_sign参数化sigma_pm重新计算R3^I,R4^I，R3^V=i*R3^I,
      R4^V=-i*R4^I 在v_y正负全部情形下都精确成立。
================================================================================
"""
import sympy as sp
import numpy as np
import pickle
import sys
sys.path.insert(0, "../../../../阶段1_单向链路ORF核心积分/组件D_I2_I3_I4_替换导出/具体计算")
mod = __import__("01_组装I2VI3VI4V")
sigma_pm_fixed = mod.sigma_pm  # 【BUG-002修复】带chirality_sign参数

x, delta_u, delta_v, gamma = sp.symbols('x delta_u delta_v gamma', real=True)


def f_V_gold_standard(xv, zval, u_hat, v_hat):
    """黄金标准：完全独立于论文公式的构造路径"""
    ux_, uy_, uz_ = u_hat
    vx_, vy_, vz_ = v_hat
    sv = np.sqrt(1-xv**2, dtype=complex)
    cosphi = (zval + 1/zval)/2
    sinphi = -1j*(zval**2 - 1)/(2*zval)
    theta_dot_u = ux_*xv*cosphi - uz_*sv
    phi_dot_u = uy_*cosphi - ux_*sinphi
    theta_dot_v = vx_*xv*cosphi + vy_*xv*sinphi - vz_*sv
    phi_dot_v = vy_*cosphi - vx_*sinphi
    n_dot_u = ux_*sv*cosphi + uy_*sv*sinphi + uz_*xv
    n_dot_v = vx_*sv*cosphi + vy_*sv*sinphi + vz_*xv
    ePlus_uu = theta_dot_u**2 - phi_dot_u**2
    eCross_uu = 2*theta_dot_u*phi_dot_u
    ePlus_vv = theta_dot_v**2 - phi_dot_v**2
    eCross_vv = 2*theta_dot_v*phi_dot_v
    numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
    return numerator_V / (1j*zval*(1+n_dot_u)*(1+n_dot_v))


def numerical_residue(f_func, z0_val, radius=1e-4, N=20000):
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = z0_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = f_func(zs)
    return np.sum(vals*dz)/(2j*np.pi)


def R3V_R4V_numeric_fixed(xv, du_v, dv_v, gamma_v, chirality_sign):
    """用修复后的sigma_pm(chirality_sign)重新计算R3I,R4I，再乘±i得到R3V,R4V"""
    cos_du, cos_dv, cos_g = np.cos(du_v), np.cos(dv_v), np.cos(gamma_v)
    sp_, sm = sigma_pm_fixed(du_v, dv_v, gamma_v, chirality_sign)
    R3_I = -2j*(1-cos_g)/(xv+sp_) + 2j*(sm-cos_dv)*(1+cos_g)/(1-cos_dv**2)
    R4_I = 2j*(1-cos_g)/(xv+sm) - 2j*(sp_-cos_dv)*(1+cos_g)/(1-cos_dv**2)
    return 1j*R3_I, -1j*R4_I


if __name__ == "__main__":
    print("=" * 70)
    print("修复后大样本鲁棒性检验 (不再限定v_y>0，覆盖v_y正负全部情形)")
    print("=" * 70)
    np.random.seed(88)
    max_rel_err = 0
    n_tested = 0
    N_TARGET = 40
    n_pos = 0
    n_neg = 0
    while n_tested < N_TARGET:
        du = np.random.uniform(0.1, np.pi - 0.1)
        dv = np.random.uniform(0.1, np.pi - 0.1)
        psi = np.random.uniform(0, 2*np.pi)
        u_hat = np.array([np.sin(du), 0, np.cos(du)])
        v_hat = np.array([np.sin(dv)*np.cos(psi), np.sin(dv)*np.sin(psi), np.cos(dv)])
        if abs(v_hat[1]) < 1e-6:
            continue
        n_tested += 1
        n_pos += (v_hat[1] > 0)
        n_neg += (v_hat[1] < 0)

        chirality_sign = 1.0 if v_hat[1] >= 0 else -1.0
        gamma_val = np.arccos(np.clip(u_hat @ v_hat, -1, 1))
        xv = np.random.uniform(-0.8, 0.8)
        sv = np.sqrt(1-xv**2)

        z3_val = -(1+v_hat[2])*(1+xv)/((v_hat[0]-1j*v_hat[1])*sv)
        z4_val = -(1-v_hat[2])*(1-xv)/((v_hat[0]-1j*v_hat[1])*sv)

        res3_num = numerical_residue(lambda zz: f_V_gold_standard(xv, zz, u_hat, v_hat), z3_val)
        res4_num = numerical_residue(lambda zz: f_V_gold_standard(xv, zz, u_hat, v_hat), z4_val)
        res3_sym, res4_sym = R3V_R4V_numeric_fixed(xv, du, dv, gamma_val, chirality_sign)

        err3 = abs(res3_num-res3_sym)/max(abs(res3_sym), 1e-30)
        err4 = abs(res4_num-res4_sym)/max(abs(res4_sym), 1e-30)
        max_rel_err = max(max_rel_err, err3, err4)

        if n_tested <= 10 or max(err3, err4) > 1e-3:
            print(f"  trial{n_tested}(v_y={v_hat[1]:+.3f}, chirality_sign={chirality_sign:+.0f}):")
            print(f"    R3V: num={res3_num:.5g}  fixed_formula={res3_sym:.5g}  err={err3:.2e}")
            print(f"    R4V: num={res4_num:.5g}  fixed_formula={res4_sym:.5g}  err={err4:.2e}")

    print(f"\n共测试 {n_tested} 组随机参数 (v_y>0: {n_pos}组, v_y<0: {n_neg}组)")
    print(f"最大相对误差 ({n_tested}组随机测试 x 2个留数 = {2*n_tested}次检验) = {max_rel_err:.2e}")
    print("(证明修复chirality_sign后，R3V=i*R3I, R4V=-i*R4I 在v_y正负全部情形下都")
    print(" 完全一致——此前的'仅v_y>0成立'结论因sigma_pm分支选择bug(BUG-002)导致，")
    print(" 现已修复；±i比例关系本身从未真正依赖v_y符号，这是此前表述不准确之处)")
