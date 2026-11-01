"""
组件B 数值验证 01: 注入-恢复测试

用组件A生成数据（注入已知 I, V）→ 组件B反解 → 比对真值。
同时做无信号均值检验。
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


def run_injection_recovery(N_det=3, N_freq=5, n_real=10000, seed=42):
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

    # Test 1: Signal injection
    I_true = np.ones(N_freq) * 1e-40
    V_true = np.ones(N_freq) * 1e-40

    C = cov_matrix.build_covariance(Gamma_I, Gamma_V, I_true, V_true, S_noise, freqs)
    rng = np.random.default_rng(seed)
    s_data = cov_matrix.sample_from_covariance(C, n_realizations=n_real, rng=rng)

    I_hat, V_hat, I_var, V_var = estimator.estimate_signal_separated(
        s_data, Gamma_I, Gamma_V, S_noise, freqs)

    I_err = np.abs(I_hat - I_true) / I_true
    V_err = np.abs(V_hat - V_true) / V_true

    print("=== Test 1: Injection-Recovery ===")
    print(f"I: max_err={np.max(I_err):.1%}, mean_err={np.mean(I_err):.1%}")
    print(f"V: max_err={np.max(V_err):.1%}, mean_err={np.mean(V_err):.1%}, median={np.median(V_err):.1%}")

    # Test 2: No signal (I=0, V=0)
    C0 = cov_matrix.build_covariance(Gamma_I, Gamma_V, np.zeros(N_freq), np.zeros(N_freq), S_noise, freqs)
    s0 = cov_matrix.sample_from_covariance(C0, n_realizations=n_real, rng=np.random.default_rng(seed+1))
    I0_hat, V0_hat, _, _ = estimator.estimate_signal_separated(s0, Gamma_I, Gamma_V, S_noise, freqs)

    # Should be ~0 within noise
    I0_std = np.std(I0_hat)
    V0_std = np.std(V0_hat)
    I0_mean = np.mean(np.abs(I0_hat))
    V0_mean = np.mean(np.abs(V0_hat))

    print(f"\n=== Test 2: No-signal baseline ===")
    print(f"I_hat: mean|val|={I0_mean:.2e} (should be ~S_n level)")
    print(f"V_hat: mean|val|={V0_mean:.2e}")
    print(f"Signal-to-noise ratio: I={np.mean(np.abs(I_hat))/I0_mean:.1f}x, V={np.mean(np.abs(V_hat))/V0_mean:.1f}x")

    passed = (np.max(I_err) < 0.2 and np.median(V_err) < 0.2)
    print(f"\nOverall: {'PASS' if passed else 'FAIL'}")
    return passed


if __name__ == "__main__":
    run_injection_recovery()
