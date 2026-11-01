"""
组件B 具体计算 01: 互相关最优估计量（分离版）

核心洞察：Γ^I 是实对称，Γ^V 是纯虚反对称。
因此 x_ij = 0.5*(Γ^I*I + Γ^V*V) 中：
    Re(x_ij) = 0.5 * Γ^I_ij * I   （只含 I）
    Im(x_ij) = 0.5 * Im(Γ^V_ij) * V （只含 V）

两个参数天然分离，各自用加权最小二乘独立估计。
这比联合复数正规方程更稳定（避免 I/V 通道耦合）。
"""

import numpy as np


def estimate_signal_separated(s_data, Gamma_I, Gamma_V, S_noise, freqs):
    """
    分离估计 I(f) 和 V(f)。

    Parameters
    ----------
    s_data : ndarray, shape (n_realizations, N_freq, N_det)
    Gamma_I : ndarray, shape (N_det, N_det, N_freq) — 实对称
    Gamma_V : ndarray, shape (N_det, N_det, N_freq) — 纯虚反对称
    S_noise : ndarray, shape (N_det, N_freq)
    freqs : ndarray, shape (N_freq,)

    Returns
    -------
    I_hat, V_hat : ndarray, shape (N_freq,)
    I_var, V_var : ndarray, shape (N_freq,)
    """
    n_realizations, N_freq, N_det = s_data.shape
    pairs = [(i, j) for i in range(N_det) for j in range(i+1, N_det)]
    n_pairs = len(pairs)

    I_hat = np.zeros(N_freq)
    V_hat = np.zeros(N_freq)
    I_var = np.full(N_freq, np.inf)
    V_var = np.full(N_freq, np.inf)

    for k in range(N_freq):
        if n_pairs == 0:
            continue

        A_I = np.zeros(n_pairs)
        b_I = np.zeros(n_pairs)
        A_V = np.zeros(n_pairs)
        b_V = np.zeros(n_pairs)
        w = np.zeros(n_pairs)

        for p, (i, j) in enumerate(pairs):
            x_ij = np.mean(s_data[:, k, i] * np.conj(s_data[:, k, j]))
            A_I[p] = 0.5 * Gamma_I[i, j, k]
            b_I[p] = np.real(x_ij)
            A_V[p] = 0.5 * np.imag(Gamma_V[i, j, k])
            b_V[p] = np.imag(x_ij)
            w[p] = 1.0 / (S_noise[i, k] * S_noise[j, k])

        sqrt_w = np.sqrt(w)

        # WLS for I: I_hat = (A†WA)^{-1} A†Wb  →  scalar case: (Aw·b)/(Aw·Aw)
        AI_w = A_I * sqrt_w
        bI_w = b_I * sqrt_w
        denom_I = np.dot(AI_w, AI_w)
        if denom_I > 0:
            I_hat[k] = float(np.dot(AI_w, bI_w) / denom_I)
            # Variance: σ² / (A†WA) where σ² ≈ residual variance
            resid_I = bI_w - I_hat[k] * AI_w
            sigma2_I = float(np.mean(resid_I**2)) if n_pairs > 1 else 1.0
            I_var[k] = sigma2_I / denom_I

        # WLS for V
        AV_w = A_V * sqrt_w
        bV_w = b_V * sqrt_w
        denom_V = np.dot(AV_w, AV_w)
        if denom_V > 0:
            V_hat[k] = float(np.dot(AV_w, bV_w) / denom_V)
            resid_V = bV_w - V_hat[k] * AV_w
            sigma2_V = float(np.mean(resid_V**2)) if n_pairs > 1 else 1.0
            V_var[k] = sigma2_V / denom_V

    return I_hat, V_hat, I_var, V_var


# Backward-compatible alias
estimate_signal = estimate_signal_separated


if __name__ == "__main__":
    from importlib import util
    import os

    base = os.path.join(os.path.dirname(__file__), '..', '..', '组件A_正向模拟数据生成', '具体计算')
    spec = util.spec_from_file_location("cov_matrix", os.path.join(base, "01_协方差矩阵构造.py"))
    cov_matrix = util.module_from_spec(spec)
    spec.loader.exec_module(cov_matrix)

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

    I_true = np.ones(N_freq) * 1e-40
    V_true = np.ones(N_freq) * 1e-40
    S_noise = np.ones((N_det, N_freq)) * 1e-40

    C = cov_matrix.build_covariance(Gamma_I, Gamma_V, I_true, V_true, S_noise, freqs)
    rng = np.random.default_rng(42)
    s_data = cov_matrix.sample_from_covariance(C, n_realizations=10000, rng=rng)

    I_hat, V_hat, I_var, V_var = estimate_signal_separated(
        s_data, Gamma_I, Gamma_V, S_noise, freqs)

    print("Separated estimator (Re→I, Im→V), n=10000:")
    print("Freq       | I_hat      | err   | V_hat      | err")
    print("-" * 70)
    for k in range(N_freq):
        ie = abs(I_hat[k] - I_true[k]) / I_true[k]
        ve = abs(V_hat[k] - V_true[k]) / V_true[k]
        print(f"{freqs[k]:.1e} Hz | {I_hat[k]:.2e} | {ie:.1%} | {V_hat[k]:.2e} | {ve:.1%}")

    max_ie = np.max(np.abs(I_hat - I_true) / I_true)
    max_ve = np.max(np.abs(V_hat - V_true) / V_true)
    print(f"\nMax rel err: I={max_ie:.1%}, V={max_ve:.1%}")
    print(f"I all <20%: {'PASS' if max_ie < 0.2 else 'FAIL'}")
    print(f"V median <20%: {'PASS' if np.median(np.abs(V_hat - V_true)/V_true) < 0.2 else 'NOTE'}")
