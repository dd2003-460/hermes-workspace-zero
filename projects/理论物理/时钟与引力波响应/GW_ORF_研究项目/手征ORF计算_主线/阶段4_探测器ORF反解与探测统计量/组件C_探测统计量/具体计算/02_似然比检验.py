"""
组件C 具体计算 02: 探测显著性 + Monte Carlo 验证

核心方法：
  Z_I(f) = I_hat(f) / σ_I(f)  其中 σ_I = sqrt(Var(I_hat))
  Z_V(f) = V_hat(f) / σ_V(f)  其中 σ_V = sqrt(Var(V_hat))

  单参数: |Z| > 1.645 → 95% 显著
  双参数: Z_I² + Z_V² > χ²₂(0.95)=5.99 → 联合 95% 显著

σ_I 从 Fisher 信息获得: σ_I = 1/sqrt(F_II)（大样本渐近）
但实际 MC 方差可能偏离渐近值（小 n_pairs 时），所以用 MC 直接估计。
"""

import numpy as np
from scipy import stats
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


def detection_significance(s_data, Gamma_I, Gamma_V, S_noise, freqs,
                           n_mc=500, seed=42):
    """
    Compute Z-scores and p-values for detection.
    
    Returns dict with: I_hat, V_hat, Z_I, Z_V, p_I, p_V, p_joint, detected
    """
    N_freq = len(freqs)
    
    # Point estimates from full dataset
    I_hat, V_hat, I_var, V_var = estimator.estimate_signal_separated(
        s_data, Gamma_I, Gamma_V, S_noise, freqs)
    
    # MC estimate of actual variance (more reliable than asymptotic)
    rng = np.random.default_rng(seed)
    N_det = Gamma_I.shape[0]
    n_real = s_data.shape[0]
    
    I_mc = np.zeros((n_mc, N_freq))
    V_mc = np.zeros((n_mc, N_freq))
    
    C = cov_matrix.build_covariance(Gamma_I, Gamma_V, 
                                     np.zeros(N_freq), np.zeros(N_freq), 
                                     S_noise, freqs)
    for mc in range(n_mc):
        s_mc = cov_matrix.sample_from_covariance(C, n_realizations=n_real, rng=rng)
        I_mc[mc], V_mc[mc], _, _ = estimator.estimate_signal_separated(
            s_mc, Gamma_I, Gamma_V, S_noise, freqs)
    
    sigma_I = np.std(I_mc, axis=0)
    sigma_V = np.std(V_mc, axis=0)
    
    # Z-scores (using H0 null distribution std)
    Z_I = I_hat / sigma_I
    Z_V = V_hat / sigma_V
    
    # P-values (two-sided for individual, joint for combined)
    p_I = 2 * (1 - stats.norm.cdf(np.abs(Z_I)))
    p_V = 2 * (1 - stats.norm.cdf(np.abs(Z_V)))
    chi2_stat = Z_I**2 + Z_V**2
    p_joint = 1 - stats.chi2.cdf(chi2_stat, df=2)
    
    detected_95 = p_joint < 0.05
    
    return {
        'I_hat': I_hat, 'V_hat': V_hat,
        'sigma_I': sigma_I, 'sigma_V': sigma_V,
        'Z_I': Z_I, 'Z_V': Z_V,
        'p_I': p_I, 'p_V': p_V,
        'chi2': chi2_stat, 'p_joint': p_joint,
        'detected_95': detected_95,
    }


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
    n_real = 5000

    print("=== Detection Significance Test ===")
    print(f"{'Scenario':<22} | {'f [Hz]':>8} | {'Z_I':>7} | {'Z_V':>7} | {'χ²':>7} | {'p_joint':>8} | {'Det?':>4}")
    print("-" * 85)
    
    scenarios = [
        ("H0: no signal", np.zeros(N_freq), np.zeros(N_freq)),
        ("Signal: I=V=1e-40", np.full(N_freq, 1e-40), np.full(N_freq, 1e-40)),
        ("Strong: I=V=5e-40", np.full(N_freq, 5e-40), np.full(N_freq, 5e-40)),
    ]
    
    for name, I_t, V_t in scenarios:
        C = cov_matrix.build_covariance(Gamma_I, Gamma_V, I_t, V_t, S_noise, freqs)
        rng = np.random.default_rng(123)
        s_data = cov_matrix.sample_from_covariance(C, n_realizations=n_real, rng=rng)
        
        res = detection_significance(s_data, Gamma_I, Gamma_V, S_noise, freqs, n_mc=200, seed=55)
        
        for k in range(N_freq):
            det = "YES" if res['detected_95'][k] else "no"
            print(f"{name:<22} | {freqs[k]:8.1e} | {res['Z_I'][k]:7.2f} | {res['Z_V'][k]:7.2f} | "
                  f"{res['chi2'][k]:7.2f} | {res['p_joint'][k]:8.4f} | {det:>4}")
        print()
    
    # Summary
    print("Expected: H0 → all p > 0.05; Signal → some p < 0.05; Strong → most p < 0.05")
