"""
组件D 04: 真实 LISA-Taiji ORF 注入-恢复验证

动机：组件C 的 MC 验证用的是 toy Γ（常数矩阵），只证明了方法正确。
本脚本把**真实 C2 算出的 LISA-Taiji ORF** 接入完整 A→B→C pipeline，
回答：用真实几何的 Γ，能不能从噪声数据中恢复出注入的信号？

流程：
1. 从 C2 asm 模块计算 X 通道 Γ^I(f), Γ^V(f)（3个卫星对 → n_pairs=3）
2. 注入已知 I_true(f), V_true(f) + 噪声 → 生成数据
3. 用分离估计量反解 → I_hat, V_hat
4. 对比 I_hat vs I_true, V_hat vs V_true
5. 多次重复统计偏差和方差
"""

import numpy as np
from importlib import util
import os, time

def load_module(name, path):
    spec = util.spec_from_file_location(name, path)
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# Load modules
_c2_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..', '..', '阶段3_具体探测器ORF',
                       '组件C2_天基SbLI_TDI正确组装', '具体计算')
asm = load_module("asm", os.path.join(_c2_dir, "01_TDI通道用单向链路Gamma_one正确组装.py"))

_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
cov_matrix = load_module("cov_matrix", os.path.join(_base, '组件A_正向模拟数据生成', '具体计算', '01_协方差矩阵构造.py'))
estimator = load_module("estimator", os.path.join(_base, '组件B_反解估计量', '具体计算', '01_互相关最优估计量.py'))


def lisa_like_constellation(center, L, n_hat, phase=0.0):
    if abs(n_hat[2]) < 0.99:
        ref = np.array([0., 0., 1.])
    else:
        ref = np.array([1., 0., 0.])
    e1 = np.cross(n_hat, ref)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(n_hat, e1)
    r = []
    for k in range(3):
        angle = phase + 2 * np.pi * k / 3
        pos = center + L * (np.cos(angle) * e1 + np.sin(angle) * e2)
        r.append(pos)
    return r


def get_x_channel_terms(r_sat, L, f):
    """X channel TDI terms for a single constellation (same as C2)."""
    links = []
    for k in range(3):
        i, j = k, (k + 1) % 3
        delta_r = r_sat[j] - r_sat[i]
        d = delta_r / np.linalg.norm(delta_r)
        links.append({"r": r_sat[i].copy(), "d": d, "L": L})
    
    k_wave = 2 * np.pi * f / asm.C_LIGHT
    delay_phase = np.exp(-1j * k_wave * L)
    
    # X channel: standard TDI-X (all 3 links contribute with specific weights)
    # For the cross-correlation between two constellations, we need
    # terms from BOTH constellations
    terms = []
    for k in range(3):
        link = links[k]
        w = delay_phase  # same delay factor for all links in simplified model
        terms.append({
            "r": link["r"],
            "d": link["d"],
            "L": L,
            "w": w
        })
    return terms


def compute_real_orf(rL, rT, L_LISA, L_TAIJI, f):
    """Compute real LISA-Taiji X-channel ORF at frequency f."""
    tL = get_x_channel_terms(rL, L_LISA, f)
    tT = get_x_channel_terms(rT, L_TAIJI, f)
    gI = asm.gamma_TDI_channels(tL, tT, f, kind="I")
    gV = asm.gamma_TDI_channels(tL, tT, f, kind="V")
    return gI, gV


if __name__ == "__main__":
    # Constellation setup (same as C2/D-01)
    AU = 1.495978707e8
    L_LISA = 3.0e6
    L_TAIJI = 3.0e6
    
    n_lisa = np.array([0.0, 0.0, 1.0])
    theta_t = np.deg2rad(70.0)
    n_taiji = np.array([np.sin(theta_t), 0.0, np.cos(theta_t)])
    c_lisa = np.array([-0.4 * AU, 0.0, 0.0])
    c_taiji = np.array([0.4 * AU * np.cos(np.deg2rad(40)),
                        0.4 * AU * np.sin(np.deg2rad(40)), 0.0])
    
    rL = lisa_like_constellation(c_lisa, L_LISA, n_lisa, phase=0.0)
    rT = lisa_like_constellation(c_taiji, L_TAIJI, n_taiji, phase=0.3)
    
    print("=" * 70)
    print("真实 LISA-Taiji ORF 注入-恢复验证")
    print("=" * 70)
    
    # Frequency grid (valid range: β_L < 1)
    N_freq = 5
    freqs = np.logspace(-4, np.log10(4e-3), N_freq)
    
    # Compute real ORF
    print("\n计算真实 ORF...")
    Gamma_I = np.zeros(N_freq)  # scalar per frequency (single channel pair)
    Gamma_V = np.zeros(N_freq, dtype=complex)
    
    for idx, f in enumerate(freqs):
        beta = 2 * np.pi * f * L_LISA / asm.C_LIGHT
        gI, gV = compute_real_orf(rL, rT, L_LISA, L_TAIJI, f)
        Gamma_I[idx] = gI.real  # Γ^I is real
        Gamma_V[idx] = gV       # Γ^V is complex (pure imaginary antisymmetric)
        print(f"  f={f:.2e} Hz (β={beta:.4f}): Γ^I={gI.real:+.4e}, Γ^V={gV:.4e}")
    
    # The estimator expects Gamma as (N_det, N_det, N_freq) with off-diagonal pairs.
    # TDI X channel = cross-correlation between LISA and Taiji → N_det=2, n_pairs=1
    # Gamma[0,1] = Gamma[1,0] = Γ^I (real, symmetric)
    # Gamma[0,1] = Γ^V (complex, antisymmetric: Gamma[1,0] = -Gamma[0,1])
    N_det = 2
    Gamma_I_mat = np.zeros((N_det, N_det, N_freq))
    Gamma_V_mat = np.zeros((N_det, N_det, N_freq), dtype=complex)
    for idx in range(N_freq):
        Gamma_I_mat[0, 1, idx] = Gamma_I[idx]
        Gamma_I_mat[1, 0, idx] = Gamma_I[idx]  # symmetric
        Gamma_V_mat[0, 1, idx] = Gamma_V[idx]
        Gamma_V_mat[1, 0, idx] = -Gamma_V[idx]  # antisymmetric
    
    # Noise model
    S_n = 1e-45  # flat ASD
    S_noise = np.full(N_freq, S_n)
    
    # Injection signal (scaled up so SNR > 1 at high frequencies)
    # At f=4 mHz: |Γ^I|~2e-4, so signal_cov ~ 2e-4 * I_true
    # For SNR~1: signal_cov ~ S_n → I_true ~ S_n/|Γ^I| ~ 1e-45/2e-4 ~ 5e-42
    I_true = np.full(N_freq, 5e-42)   # isotropic background (SNR~1 at 4 mHz)
    V_true = np.full(N_freq, 5e-43)   # chiral component (10x smaller than I)
    
    print(f"\n注入信号: I_true={I_true[0]:.1e}, V_true={V_true[0]:.1e}")
    print(f"噪声: S_n={S_n:.1e} Hz^-1 (flat)")
    
    # Run injection-recovery multiple times
    n_trials = 100
    rng = np.random.default_rng(123)
    
    I_recovered = np.zeros((n_trials, N_freq))
    V_recovered = np.zeros((n_trials, N_freq))
    
    print(f"\n运行 {n_trials} 次注入-恢复...")
    for trial in range(n_trials):
        # Generate data: s = signal + noise
        # Signal covariance: 0.5 * (Γ^I * I + Γ^V * V)
        # For n_det=1: C_signal = 0.5 * (Γ^I * I + Γ^V * V)
        C_sig = 0.5 * (Gamma_I_mat[0, 0, :] * I_true + 
                       Gamma_V_mat[0, 0, :] * V_true)
        C_total = C_sig + S_noise
        
        # s_data shape: (n_realizations, N_freq, N_det) — matches estimator expectation
        n_real = 500
        s_data = np.zeros((n_real, N_freq, N_det), dtype=complex)
        for i in range(N_det):
            for k in range(N_freq):
                var = max(S_noise[k], 1e-100)
                s_data[:, k, i] = np.sqrt(var) * (rng.standard_normal(n_real) + 
                                                   1j * rng.standard_normal(n_real)) / np.sqrt(2)
        # Add correlated signal: <s_0(k) s_1*(k)> = 0.5*(Γ^I*I + Γ^V*V)
        for k in range(N_freq):
            cov_sig = 0.5 * (Gamma_I_mat[0,1,k] * I_true[k] + Gamma_V_mat[0,1,k] * V_true[k])
            cov_real = cov_sig.real  # for Re(x_ij)
            if abs(cov_real) > 1e-100:
                common = np.sqrt(abs(cov_real)) * (rng.standard_normal(n_real) + 
                                                    1j * rng.standard_normal(n_real)) / np.sqrt(2)
                if cov_real > 0:
                    s_data[:, k, 0] += common
                    s_data[:, k, 1] += common
                else:
                    s_data[:, k, 0] -= common
                    s_data[:, k, 1] += common
            cov_imag = cov_sig.imag  # for Im(x_ij) → V channel
            if abs(cov_imag) > 1e-100:
                common_v = np.sqrt(abs(cov_imag)) * (rng.standard_normal(n_real) + 
                                                      1j * rng.standard_normal(n_real)) / np.sqrt(2)
                if cov_imag > 0:
                    s_data[:, k, 0] += 1j * common_v
                    s_data[:, k, 1] -= 1j * common_v
                else:
                    s_data[:, k, 0] -= 1j * common_v
                    s_data[:, k, 1] += 1j * common_v
        
        # Estimate
        # S_noise must be (N_det, N_freq) for the estimator's weight calculation
        S_noise_2d = np.tile(S_noise.reshape(1, -1), (N_det, 1))
        I_hat, V_hat, _, _ = estimator.estimate_signal_separated(
            s_data, Gamma_I_mat, Gamma_V_mat, S_noise_2d, freqs)
        
        I_recovered[trial] = I_hat.real
        V_recovered[trial] = V_hat.real
    
    # Statistics
    print("\n" + "=" * 70)
    print("注入-恢复结果（50 trials × 5 freq bins）")
    print("=" * 70)
    print(f"{'f [Hz]':>10} {'Γ^I':>12} {'|Γ^V|':>12} | {'I_true':>10} {'I_hat_mean':>12} {'I_bias%':>8} {'I_std/I_true':>12} | {'V_true':>10} {'V_hat_mean':>12} {'V_bias%':>8} {'V_std/V_true':>12}")
    print("-" * 160)
    
    for idx, f in enumerate(freqs):
        I_mean = np.mean(I_recovered[:, idx])
        I_std = np.std(I_recovered[:, idx])
        V_mean = np.mean(V_recovered[:, idx])
        V_std = np.std(V_recovered[:, idx])
        
        I_bias = (I_mean - I_true[idx]) / I_true[idx] * 100
        V_bias = (V_mean - V_true[idx]) / V_true[idx] * 100 if V_true[idx] != 0 else float('nan')
        I_rel_err = I_std / I_true[idx]
        V_rel_err = V_std / V_true[idx] if V_true[idx] != 0 else float('nan')
        
        print(f"{f:10.2e} {Gamma_I[idx]:+12.4e} {abs(Gamma_V[idx]):12.4e} | "
              f"{I_true[idx]:10.1e} {I_mean:12.4e} {I_bias:8.2f} {I_rel_err:12.2e} | "
              f"{V_true[idx]:10.1e} {V_mean:12.4e} {V_bias:8.2f} {V_rel_err:12.2e}")
    
    print("\n解读:")
    print("- I_bias 应接近 0%（无偏估计）；若系统性偏离 → 估计量有偏")
    print("- I_std/I_true = 相对不确定度；越小越好")
    print("- V 通道的相对误差预期比 I 大很多（因为 |Γ^V| ≪ |Γ^I|）")
    print("- 如果 I_std/I_true > 1 → 该频率下信噪比不足，无法可靠探测")
