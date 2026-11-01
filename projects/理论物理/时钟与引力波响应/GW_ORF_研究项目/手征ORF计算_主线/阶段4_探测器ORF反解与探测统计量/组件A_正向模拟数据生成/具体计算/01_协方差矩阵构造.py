"""
组件A 具体计算 01: 协方差矩阵构造

从阶段3的 Γ^I_ij(f), Γ^V_ij(f) + 假设的 I(f), V(f) + 噪声模型，
构造完整的协方差矩阵 C_ij(f)。

C_ij(f) = 0.5 * [Γ^I_ij(f) * I(f) + Γ^V_ij(f) * V(f)] + δ_ij * S_n^(i)(f)

用法:
    from cov_matrix import build_covariance
    C = build_covariance(Gamma_I, Gamma_V, I_spec, V_spec, S_noise, freqs)
"""

import numpy as np


def build_covariance(Gamma_I, Gamma_V, I_spec, V_spec, S_noise, freqs):
    """
    构造协方差矩阵。

    Parameters
    ----------
    Gamma_I : ndarray, shape (N_det, N_det, N_freq)
        强度 ORF 张量 Γ^I_ij(f)
    Gamma_V : ndarray, shape (N_det, N_det, N_freq)
        手征 ORF 张量 Γ^V_ij(f)（纯虚数）
    I_spec : ndarray, shape (N_freq,)
        强度功率谱密度 I(f)
    V_spec : ndarray, shape (N_freq,)
        手征功率谱密度 V(f)
    S_noise : ndarray, shape (N_det, N_freq)
        各探测器噪声功率谱 S_n^(i)(f)
    freqs : ndarray, shape (N_freq,)
        频率轴

    Returns
    -------
    C : ndarray, shape (N_freq, N_det, N_det)
        协方差矩阵 C(f)，C[f, i, j] = <s_i(f) s_j*(f)>
    """
    N_det = Gamma_I.shape[0]
    N_freq = len(freqs)

    # 信号部分: 0.5 * [Γ^I * I + Γ^V * V]
    signal = 0.5 * (Gamma_I * I_spec[np.newaxis, np.newaxis, :] +
                    Gamma_V * V_spec[np.newaxis, np.newaxis, :])

    # 噪声部分: δ_ij * S_n^(i)(f)
    noise = np.zeros((N_det, N_det, N_freq), dtype=complex)
    for i in range(N_det):
        noise[i, i, :] = S_noise[i, :]

    # 总协方差
    C = signal + noise

    # 转置为 (N_freq, N_det, N_det)
    C = C.transpose(2, 0, 1)

    return C


def sample_from_covariance(C, n_realizations=1000, rng=None):
    """
    从协方差矩阵采样高斯随机变量。

    对每个频率 bin f_k，C[f_k] 是一个复对称矩阵。
    用 Cholesky 分解: C = L L†, 则 s = L z, z ~ CN(0, I)。

    Parameters
    ----------
    C : ndarray, shape (N_freq, N_det, N_det)
    n_realizations : int
    rng : np.random.Generator

    Returns
    -------
    s : ndarray, shape (n_realizations, N_freq, N_det)
        模拟的探测器数据流（频率域）
    """
    if rng is None:
        rng = np.random.default_rng()

    N_freq, N_det, _ = C.shape
    s = np.zeros((n_realizations, N_freq, N_det), dtype=complex)

    for k in range(N_freq):
        Ck = C[k]
        # 确保 Hermitian
        Ck = 0.5 * (Ck + Ck.conj().T)
        # Cholesky
        try:
            L = np.linalg.cholesky(Ck)
        except np.linalg.LinAlgError:
            # 加小正则化
            L = np.linalg.cholesky(Ck + 1e-15 * np.eye(N_det))
        # 采样: s = L z, z ~ CN(0, I)
        for r in range(n_realizations):
            z = rng.standard_normal(N_det) + 1j * rng.standard_normal(N_det)
            z /= np.sqrt(2)  # 归一化使 Var(z) = 1
            s[r, k, :] = L @ z

    return s


if __name__ == "__main__":
    # 简单测试: 2 探测器, 3 频率 bin
    N_det, N_freq = 2, 3
    freqs = np.array([1e-4, 1e-3, 1e-2])

    # 假想 Γ^I (Hellings-Downs 风格)
    Gamma_I = np.zeros((N_det, N_det, N_freq))
    Gamma_I[0, 0, :] = 1.0
    Gamma_I[1, 1, :] = 1.0
    Gamma_I[0, 1, :] = 0.5
    Gamma_I[1, 0, :] = 0.5

    # 假想 Γ^V (纯虚)
    Gamma_V = np.zeros((N_det, N_det, N_freq), dtype=complex)
    Gamma_V[0, 1, :] = 0.1j
    Gamma_V[1, 0, :] = -0.1j

    # 信号谱
    I_spec = np.ones(N_freq) * 1e-40
    V_spec = np.ones(N_freq) * 1e-42

    # 噪声
    S_noise = np.ones((N_det, N_freq)) * 1e-40

    C = build_covariance(Gamma_I, Gamma_V, I_spec, V_spec, S_noise, freqs)
    print(f"Covariance matrix shape: {C.shape}")
    print(f"C[0] =\n{C[0]}")

    s = sample_from_covariance(C, n_realizations=100)
    print(f"\nSampled data shape: {s.shape}")
    print(f"Mean of s[0,0,:] over realizations: {np.mean(s[:, 0, 0]):.2e} (should be ~0)")
    print(f"Var of s[0,0,:] over realizations: {np.var(s[:, 0, 0]):.2e} (should be ~Re(C[0,0,0]))")
