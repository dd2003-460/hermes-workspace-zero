"""
组件C 具体计算 01: Fisher 信息矩阵 + 灵敏度曲线

核心：分离原理下 Fisher 信息是对角阵。
I_min(f) = z_alpha / sqrt(Fisher_II(f))
"""

import numpy as np


def fisher_information(Gamma_I, Gamma_V, S_noise, freqs):
    """
    计算每个频率 bin 的 Fisher 信息矩阵（对角）。

    Parameters
    ----------
    Gamma_I : ndarray, shape (N_det, N_det, N_freq) — 实对称
    Gamma_V : ndarray, shape (N_det, N_det, N_freq) — 纯虚反对称
    S_noise : ndarray, shape (N_det, N_freq)
    freqs : ndarray, shape (N_freq,)

    Returns
    -------
    F_II : ndarray, shape (N_freq,) — Fisher info for I
    F_VV : ndarray, shape (N_freq,) — Fisher info for V
    """
    N_det, N_freq = Gamma_I.shape[0], len(freqs)
    pairs = [(i, j) for i in range(N_det) for j in range(i+1, N_det)]

    F_II = np.zeros(N_freq)
    F_VV = np.zeros(N_freq)

    for k in range(N_freq):
        sum_II = 0.0
        sum_VV = 0.0
        for i, j in pairs:
            w = 1.0 / (S_noise[i, k] * S_noise[j, k])
            dI = 0.5 * Gamma_I[i, j, k]
            dV = 0.5 * np.imag(Gamma_V[i, j, k])
            sum_II += w * dI**2
            sum_VV += w * dV**2
        F_II[k] = sum_II
        F_VV[k] = sum_VV

    return F_II, F_VV


def sensitivity_curve(F_II, F_VV, z=1.645):
    """
    最小可探测信号强度 (单侧 95% by default).

    Returns
    -------
    I_min : ndarray — minimum detectable I(f)
    V_min : ndarray — minimum detectable V(f)
    """
    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        I_min = z / np.sqrt(F_II)
        V_min = z / np.sqrt(F_VV)
    # Where Fisher info is 0, sensitivity is infinite
    I_min[F_II <= 0] = np.inf
    V_min[F_VV <= 0] = np.inf
    return I_min, V_min


def snr_curve(I_signal, V_signal, F_II, F_VV):
    """
    Signal-to-noise ratio at each frequency.
    SNR_I = I_signal * sqrt(F_II)
    SNR_V = V_signal * sqrt(F_VV)
    Combined (orthogonal params): SNR = sqrt(SNR_I^2 + SNR_V^2)
    """
    snr_I = I_signal * np.sqrt(F_II)
    snr_V = V_signal * np.sqrt(F_VV)
    snr_total = np.sqrt(snr_I**2 + snr_V**2)
    return snr_I, snr_V, snr_total


if __name__ == "__main__":
    N_det, N_freq = 3, 50
    freqs = np.logspace(-5, -1, N_freq)

    # Realistic-ish ORF (frequency-dependent, like Hellings-Downs)
    f_ref = 1e-4
    Gamma_I = np.zeros((N_det, N_det, N_freq))
    for i in range(N_det):
        for j in range(N_det):
            if i != j:
                # Simple model: ~ f/f_ref at low freq, saturates at high
                x = freqs / f_ref
                Gamma_I[i, j, :] = 0.5 * (x / (1 + x**2)) ** 0.5
            else:
                Gamma_I[i, i, :] = 1.0

    Gamma_V = np.zeros((N_det, N_det, N_freq), dtype=complex)
    for i in range(N_det):
        for j in range(i+1, N_det):
            x = freqs / f_ref
            Gamma_V[i, j, :] = 0.1j * (x / (1 + x**2)) ** 0.5
            Gamma_V[j, i, :] = -Gamma_V[i, j, :]

    # LISA-like noise: ~ 1e-40 with frequency dependence
    S_noise = np.ones((N_det, N_freq)) * 1e-40
    # Add some frequency structure
    S_noise[:, :] *= (1 + 10 * (freqs / 1e-3)**2)

    F_II, F_VV = fisher_information(Gamma_I, Gamma_V, S_noise, freqs)
    I_min, V_min = sensitivity_curve(F_II, F_VV, z=1.645)

    print("=== Sensitivity Curve (95% one-sided) ===")
    print(f"{'f [Hz]':>10} | {'F_II':>12} | {'I_min':>12} | {'F_VV':>12} | {'V_min':>12}")
    print("-" * 70)
    for k in range(0, N_freq, 10):
        print(f"{freqs[k]:10.2e} | {F_II[k]:12.3e} | {I_min[k]:12.3e} | {F_VV[k]:12.3e} | {V_min[k]:12.3e}")

    # Best sensitivity (minimum I_min)
    best_k = np.argmin(I_min[np.isfinite(I_min)])
    print(f"\nBest I sensitivity: f={freqs[best_k]:.2e} Hz, I_min={I_min[best_k]:.3e}")
    best_v = np.argmin(V_min[np.isfinite(V_min)])
    print(f"Best V sensitivity: f={freqs[best_v]:.2e} Hz, V_min={V_min[best_v]:.3e}")

    # SNR for a hypothetical signal
    I_sig = np.ones(N_freq) * 1e-40
    V_sig = np.ones(N_freq) * 1e-40
    snr_I, snr_V, snr_tot = snr_curve(I_sig, V_sig, F_II, F_VV)
    print(f"\nSNR for I=V=1e-40: max total SNR = {np.max(snr_tot):.2f} at f={freqs[np.argmax(snr_tot)]:.2e} Hz")
    print(f"Detection threshold (SNR>3): {np.sum(snr_tot > 3)} of {N_freq} bins")
