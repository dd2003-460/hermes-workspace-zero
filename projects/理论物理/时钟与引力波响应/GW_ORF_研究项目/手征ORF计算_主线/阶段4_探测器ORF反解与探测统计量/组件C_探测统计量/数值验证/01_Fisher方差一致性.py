"""
组件C 数值验证 01: Fisher 信息 vs 实际估计量方差

检验：Var(I_hat)_MC ≈ 1/Fisher_II（大样本渐近）
偏差来源：n_pairs=3 太少，有限样本修正。
"""

import numpy as np
from importlib import util
import os


def load_module(name, path):
    spec = util.spec_from_file_location(name, path)
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
cov_matrix = load_module("cov_matrix", os.path.join(base_dir, '组件A_正向模拟数据生成', '具体计算', '01_协方差矩阵构造.py'))
estimator = load_module("estimator", os.path.join(base_dir, '组件B_反解估计量', '具体计算', '01_互相关最优估计量.py'))
fisher_mod = load_module("fisher", os.path.join(base_dir, '组件C_探测统计量', '具体计算', '01_Fisher信息与灵敏度.py'))


if __name__ == "__main__":
    N_det, N_freq = 3, 5
    freqs = np.logspace(-4, -1, N_freq)

    Gamma_I = np.zeros((N_det, N_det, N_freq))
    for i in range(N_det):
        for j in range(N_det):
            if i != j:
                Gamma_I[i, j, :] = 0.3 + 0.1 * (i + j)
            else:
                Gamma_I[i, i, :] = 1.0

    Gamma_V = np.zeros((N_det, N_det, N_freq), dtype=complex)
    for i in range(N_det):
        for j in range(i+1, N_det):
            Gamma_V[i, j, :] = (0.05 + 0.02 * i) * 1j
            Gamma_V[j, i, :] = -Gamma_V[i, j, :]

    S_noise = np.ones((N_det, N_freq)) * 1e-40

    F_II, F_VV = fisher_mod.fisher_information(Gamma_I, Gamma_V, S_noise, freqs)
    var_asymptotic_I = 1.0 / F_II
    var_asymptotic_V = 1.0 / F_VV

    # MC variance estimate
    n_mc = 500
    n_real = 5000
    rng = np.random.default_rng(99)
    
    C = cov_matrix.build_covariance(Gamma_I, Gamma_V, np.zeros(N_freq), np.zeros(N_freq), S_noise, freqs)
    
    I_mc = np.zeros((n_mc, N_freq))
    V_mc = np.zeros((n_mc, N_freq))
    for mc in range(n_mc):
        s_mc = cov_matrix.sample_from_covariance(C, n_realizations=n_real, rng=rng)
        I_mc[mc], V_mc[mc], _, _ = estimator.estimate_signal_separated(s_mc, Gamma_I, Gamma_V, S_noise, freqs)
    
    var_mc_I = np.var(I_mc, axis=0)
    var_mc_V = np.var(V_mc, axis=0)

    print("=== Fisher Info vs MC Variance ===")
    print(f"{'f [Hz]':>10} | {'1/F_II':>12} | {'Var_MC_I':>12} | {'ratio':>7} | {'1/F_VV':>12} | {'Var_MC_V':>12} | {'ratio':>7}")
    print("-" * 100)
    for k in range(N_freq):
        rI = var_mc_I[k] / var_asymptotic_I[k]
        rV = var_mc_V[k] / var_asymptotic_V[k]
        print(f"{freqs[k]:10.2e} | {var_asymptotic_I[k]:12.3e} | {var_mc_I[k]:12.3e} | {rI:7.2f} | "
              f"{var_asymptotic_V[k]:12.3e} | {var_mc_V[k]:12.3e} | {rV:7.2f}")
    
    mean_ratio_I = np.mean(var_mc_I / var_asymptotic_I)
    mean_ratio_V = np.mean(var_mc_V / var_asymptotic_V)
    print(f"\nMean ratio (MC/asymptotic): I={mean_ratio_I:.2f}, V={mean_ratio_V:.2f}")
    print("Ratio ~1.0 → Fisher info correctly predicts estimator variance")
    print("Ratio >1 → finite-sample variance larger than asymptotic (expected with n_pairs=3)")
