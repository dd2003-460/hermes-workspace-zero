"""
组件A 数值验证 01: 互相关矩阵验证

检查生成的模拟数据的互相关是否匹配理论预测。

方法:
    用 n_realizations 次独立采样，计算经验互相关
    <s_i(f) s_j*(f)>_empirical = (1/N) Σ_r s_i^r(f) s_j^{r*}(f)
    与理论值 C_ij(f) 比对。

判据:
    |empirical - theory| / |theory| < 5% (n=10000 时)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '具体计算'))
import importlib.util
spec = importlib.util.spec_from_file_location("cov_matrix", os.path.join(os.path.dirname(__file__), '..', '具体计算', '01_协方差矩阵构造.py'))
cov_matrix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cov_matrix)
build_covariance = cov_matrix.build_covariance
sample_from_covariance = cov_matrix.sample_from_covariance
import numpy as np


def verify_cross_correlation(Gamma_I, Gamma_V, I_spec, V_spec, S_noise, freqs,
                             n_realizations=10000, tol=0.05, seed=42):
    """
    验证经验互相关是否匹配理论协方差。

    Returns
    -------
    max_rel_err : float
        最大相对误差
    details : list of str
        每个频率 bin 的详情
    """
    rng = np.random.default_rng(seed)
    N_freq, N_det = len(freqs), Gamma_I.shape[0]

    # 理论协方差
    C_theory = build_covariance(Gamma_I, Gamma_V, I_spec, V_spec, S_noise, freqs)

    # 采样
    s = sample_from_covariance(C_theory, n_realizations=n_realizations, rng=rng)

    # 经验互相关
    max_rel_err = 0.0
    details = []

    for k in range(N_freq):
        for i in range(N_det):
            for j in range(N_det):
                empirical = np.mean(s[:, k, i] * np.conj(s[:, k, j]))
                theory = C_theory[k, i, j]

                if abs(theory) > 1e-50:
                    rel_err = abs(empirical - theory) / abs(theory)
                else:
                    rel_err = abs(empirical - theory)

                if rel_err > max_rel_err:
                    max_rel_err = rel_err

                if i == j or (i != j and k == 0):
                    details.append(
                        f"f={freqs[k]:.1e} Hz, ({i},{j}): "
                        f"emp={empirical:.3e}, theory={theory:.3e}, "
                        f"rel_err={rel_err:.2%}"
                    )

    return max_rel_err, details


if __name__ == "__main__":
    # 测试: 2 探测器, 3 频率 bin
    N_det, N_freq = 2, 3
    freqs = np.array([1e-4, 1e-3, 1e-2])

    Gamma_I = np.zeros((N_det, N_det, N_freq))
    Gamma_I[0, 0, :] = 1.0
    Gamma_I[1, 1, :] = 1.0
    Gamma_I[0, 1, :] = 0.5
    Gamma_I[1, 0, :] = 0.5

    Gamma_V = np.zeros((N_det, N_det, N_freq), dtype=complex)
    Gamma_V[0, 1, :] = 0.1j
    Gamma_V[1, 0, :] = -0.1j

    I_spec = np.ones(N_freq) * 1e-40
    V_spec = np.ones(N_freq) * 1e-42
    S_noise = np.ones((N_det, N_freq)) * 1e-40

    print("Running cross-correlation verification (n=10000)...")
    max_err, details = verify_cross_correlation(
        Gamma_I, Gamma_V, I_spec, V_spec, S_noise, freqs,
        n_realizations=10000
    )

    print("\nDetails:")
    for d in details:
        print(f"  {d}")
    print(f"\nMax relative error: {max_err:.2%}")
    print(f"Pass criterion (<5%): {'PASS' if max_err < 0.05 else 'FAIL'}")
