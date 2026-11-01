"""
【性质】推导 —— 修复chirality_sign后，R1,R2,R3,R4与真实留数的大样本回归验证
【计算的量】60组随机(delta_u,delta_v,psi)构型下，R1/R2(取决于测试点x落在
        哪个区间)、R3/R4 与独立数值围道积分黄金标准的比对
【状态】✅ 60/60组通过（此前未修复时，同样风格的测试只有约50%通过率）
【依赖】直接复制组件D具体计算文件(01_组装I2I3I4强度版.py)的sigma_pm(已修复),
        all_R_integrals_I(已修复), f_I_gold_standard, numerical_residue
"""
import numpy as np
import sys
sys.path.insert(0, "../../../组件D_I2_I3_I4_替换导出/具体计算")
mod = __import__("01_组装I2I3I4强度版")
sigma_pm = mod.sigma_pm
f_I_gold_standard = mod.f_I_gold_standard
numerical_residue = mod.numerical_residue


def poles_of_1_plus_ndotU(x, uvec):
    ux, uy, uz = uvec
    s = np.sqrt(1 - x**2 + 0j)
    A = s * (ux - 1j*uy); B = 2*(1+uz*x); C = s*(ux + 1j*uy)
    disc = B**2 - 4*A*C
    return (-B + np.sqrt(disc))/(2*A), (-B - np.sqrt(disc))/(2*A)


def R1_formula(x, cos_du, cos_g, sp_, sm): return -2j*(1-cos_g)/(x+sm) + 2j*(sp_-cos_du)*(1+cos_g)/(1-cos_du**2)
def R2_formula(x, cos_du, cos_g, sp_, sm): return 2j*(1-cos_g)/(x+sp_) - 2j*(sm-cos_du)*(1+cos_g)/(1-cos_du**2)
def R3_formula(x, cos_dv, cos_g, sp_, sm): return -2j*(1-cos_g)/(x+sp_) + 2j*(sm-cos_dv)*(1+cos_g)/(1-cos_dv**2)
def R4_formula(x, cos_dv, cos_g, sp_, sm): return 2j*(1-cos_g)/(x+sm) - 2j*(sp_-cos_dv)*(1+cos_g)/(1-cos_dv**2)


if __name__ == "__main__":
    np.random.seed(31415)
    N = 60
    n_fail = 0
    for i in range(N):
        du_r = np.random.uniform(0.05, np.pi-0.05)
        u_hat = np.array([np.sin(du_r), 0, np.cos(du_r)])
        dv_r = np.random.uniform(0.05, np.pi-0.05)
        psi_r = np.random.uniform(0, 2*np.pi)
        v_hat = np.array([np.sin(dv_r)*np.cos(psi_r), np.sin(dv_r)*np.sin(psi_r), np.cos(dv_r)])
        gamma = np.arccos(np.clip(u_hat @ v_hat, -1, 1))
        cos_du, cos_dv, cos_g = np.cos(du_r), np.cos(dv_r), np.cos(gamma)
        chir = 1.0 if v_hat[1] >= 0 else -1.0
        sp_, sm = sigma_pm(du_r, dv_r, gamma, chir)

        xu_test = np.random.uniform(-1, -cos_du) if -1 < -cos_du else np.random.uniform(-cos_du, 1)
        z1, z2 = poles_of_1_plus_ndotU(xu_test, u_hat)
        pole_in_u = z1 if abs(z1) < 1 else z2
        actual_u = numerical_residue(lambda z: f_I_gold_standard(xu_test, z, u_hat, v_hat), pole_in_u)
        Rform = R1_formula(xu_test, cos_du, cos_g, sp_, sm) if xu_test < -cos_du else R2_formula(xu_test, cos_du, cos_g, sp_, sm)
        match_u = np.allclose(actual_u, Rform, atol=1e-4)

        xv_test = np.random.uniform(-1, -cos_dv) if -1 < -cos_dv else np.random.uniform(-cos_dv, 1)
        z3, z4 = poles_of_1_plus_ndotU(xv_test, v_hat)
        pole_in_v = z3 if abs(z3) < 1 else z4
        actual_v = numerical_residue(lambda z: f_I_gold_standard(xv_test, z, u_hat, v_hat), pole_in_v)
        Rform2 = R3_formula(xv_test, cos_dv, cos_g, sp_, sm) if xv_test < -cos_dv else R4_formula(xv_test, cos_dv, cos_g, sp_, sm)
        match_v = np.allclose(actual_v, Rform2, atol=1e-4)

        ok = match_u and match_v
        n_fail += (not ok)
        if not ok:
            print(f"FAIL trial{i}: v_y={v_hat[1]:.3f} du={du_r:.3f} dv={dv_r:.3f}")

    print(f"总测试: {N}组随机参数 (v_y正负都覆盖, delta_u/delta_v全范围[0.05,pi-0.05])")
    print(f"失败: {n_fail}/{N} 组")
    print("全部通过！" if n_fail == 0 else "存在失败，需要继续排查")
