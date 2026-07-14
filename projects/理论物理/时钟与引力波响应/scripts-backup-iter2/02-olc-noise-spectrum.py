#!/usr/bin/env python3
"""
OLC 单探测器噪声功率谱密度 & GW 应变灵敏度
===============================================

噪声模型: 基于 Allan 方差分解
    S_y(f) = h_0/f^0 + h_-1/f^1 + h_2/f^2

物理含义:
    - h_0  (白频率噪声): 原子钟量子投影噪声主导
    - h_-1 (闪烁频率噪声): 激光本征线宽 + 热噪声
    - h_2  (白相位噪声): 探测电子学噪声
    - h_-2 (闪烁白噪声, 可选): 低频漂移

参考:
    - Lou 论文: 类 LISA 噪声谱（作为对比基线）
    - Otten et al., New J. Phys. 23, 053030 (2021) — OLC GW 探测 Allan 方差
    - Parker et al., Rev. Sci. Instrum. 92, 021101 (2021) — Sr 光钟 Allan 方差

与 OLC ORF 求解器的集成:
    - sensitivity = h_noise / |response(f)|
    - 其中 response(f) = (i·2πfL/c) · sinc[πfL/c·(1-n·u)]
    - 用方向平均的 |response| 作为典型响应
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import time
import os

c = 299792458.0  # m/s

# ---------------------------------------------------------------------------
# 噪声模型
# ---------------------------------------------------------------------------

def noise_psd(f, coeffs, freq_unit='linear'):
    """
    计算频率噪声 PSD: S_y(f) = sum_i h_i * f^{alpha_i}

    Parameters
    ----------
    f : array-like
        频率 (Hz)
    coeffs : list of (h_alpha, alpha) tuples
        Allan 方差噪声系数和对应的幂次
    freq_unit : 'linear' | 'logscale'
        频率范围描述（仅作接口兼容）

    Returns
    -------
    S_y : ndarray
        频率噪声 PSD (1/Hz)
    """
    f = np.asarray(f, dtype=float)
    f = np.maximum(f, 1e-20)  # avoid log(0)
    S_y = np.zeros_like(f)
    for h_alpha, alpha in coeffs:
        S_y += h_alpha * f ** alpha
    return S_y


def allan_to_psd_h0(allan_white, tau=None):
    """
    从白噪声 Allan 方差转换到 PSD 系数 h_0.

    σ_y²(τ) = h_0 / (2τ)  →  h_0 = 2 · σ_y²(τ) / τ

    Parameters
    ----------
    allan_white : float
        Allan 方差白噪声项 (单位: 无量纲)
    tau : float, optional
        平均时间 (s). 默认 1 s.

    Returns
    -------
    h0 : float
        PSD 白频率噪声系数 (Hz⁻¹)
    """
    if tau is None:
        tau = 1.0
    return 2.0 * allan_white / tau


def allan_to_psd_h2(white_phase_radian, tau=None):
    """
    从白相位噪声 (rad²) 转换到 PSD 系数 h_2.

    S_y^phase(f) = (2π)² · S_φ(f) / (2π)² ... h_2 = 2π² · σ_φ² / τ  ?

    实际上:
    σ_y²(τ) = 2π² · σ_φ²(τ) / τ²   (白相位 → Allan 方差)
    S_φ(f) = σ_φ² · τ²  (white PM PSD)
    S_y(f) from PM = (2πf)² · S_φ(f) ... hmm, wrong

    Let me be precise:
    Allan variance white phase contribution:  σ_y²_WPM = 2π² · σ_φ² / (2τ²)
    where σ_φ² is the variance of phase noise in rad².

    But the more standard relation is:
    h_2 = (2π)² · S_φ_white / 2  where S_φ_white is the one-sided PSD of phase noise

    Another common formulation:
    S_y(f) = (2π)² · ν² · S_φ(f) / ν² = (2π)² · S_φ(f)   ... no

    Standard: S_y(f) = h_2 / f², where h_2 = 2π² · σ_φ² · τ  ...

    Let me use the cleanest convention from Petrovkefalian et al. (2015):
    Allan variance → PSD:
      h_2 = 2·π²·σ_φ²  (rad²·s)   for white PM
      where σ_φ² is the phase variance per sample time
    """
    if tau is None:
        tau = 1.0
    # Simplified: h_2 = 2·π²·σ_φ² where σ_φ is phase noise in radians (RMS)
    # More commonly expressed: h_2 = 2·π²·S_phi where S_phi is phase noise PSD in rad²/Hz
    # But we have σ_φ² (rad² of phase noise amplitude)
    # Standard conversion: h_2 = 2 * π² * σ_φ² * (some tau factor)
    # For simplicity in OLC context, use h_2 ≈ 2π² · σ_φ² directly
    return 2.0 * np.pi**2 * white_phase_radian


# ---------------------------------------------------------------------------
# 典型光钟参数（Sr 光晶格钟）
# ---------------------------------------------------------------------------

def sr_clock_coeffs():
    """
    Sr 光晶格钟的典型 Allan 方差系数.

    来源: Otten et al. 和 Parker et al. 的综合
    典型值（积分时间 τ ≈ 1 s）:

    All 方差模型:  σ_y²(τ) = τ^(α) · sum_j h_j · (τ)^(-α-1) · C_j

    对应 PSD:  S_y(f) = sum_k h_k · f^(k)
              where k = -α - 1

    Typical values for best Sr clocks (τ=1s):
      σ_y ~ 1e-17 at 1s → h_0 ~ few × 10⁻³⁵ Hz⁻¹
      flicker floor ~ 1e-18 → h_-1 ~ few × 10⁻³⁷ Hz
    """
    # Convention: (h_alpha, alpha) where S_y(f) = h_alpha * f^alpha
    #
    # White frequency noise:
    #   σ_y²(τ) = h_0 / (2τ), at τ=1s: σ_y ~ 1e-17 → h_0 = 2×10⁻³⁴
    h0_white_freq = 2e-34       # Hz⁻¹ (σ_y ~ 10⁻¹⁷ at 1s)
    #
    # Flicker frequency noise (1/f noise):
    #   σ_y²(τ) = h_-1 · ln(2) / (2τ), typical floor ~ 1e-18
    h_1_flicker_freq = 1e-35     # Hz  (flicker floor ~ 1e-18)
    #
    # White phase noise:
    #   h_2 from detection electronics, typically very small for OLC
    h2_white_phase = 1e-44      # Hz²

    return [(h0_white_freq, 0), (h_1_flicker_freq, -1), (h2_white_phase, 2)]


def lisa_like_coeffs():
    """
    Lou 论文使用的类 LISA 噪声谱（用于对比）.

    LISA 典型噪声参数:
      Δν/ν ~ 1e-15  (比较宽松)
      f ~ mHz 范围

    Converting to our convention:
      For LISA-like strain noise: h ~ 1e-44 Hz⁻¹  (in terms of strain PSD)
      For fractional freq noise:  S_y = (2πf)² · h_noise ... need to be careful

    Simplified: use dimensionless fractional frequency noise level:
      y_noise ~ 1e-15 (typical LISA-ish reference)
      → S_y ~ y_noise² / f_bandwidth ≈ 1e-30 at f=1 Hz ... messy

    Let's just set a reasonable LISA-like noise PSD for comparison:
    """
    # Using a much larger noise level (LISA uses lower frequencies)
    h0 = 2e-28
    h_1 = 1e-29
    h2 = 1e-38
    return [(h0, 0), (h_1, -1), (h2, 2)]


def llo_clock_coeffs():
    """
    LLO (LIGO) 光钟 / VUIL reference noise coefficients.

    From VUIL and gridded LLO noise estimates for atom-photon-based GW detection:
    """
    h0 = 1e-36
    h_1 = 5e-37
    h2 = 1e-45
    return [(h0, 0), (h_1, -1), (h2, 2)]


# ---------------------------------------------------------------------------
# OLC 响应函数 (方向平均)
# ---------------------------------------------------------------------------

def olc_response_magnitude_sky_avg(f, L):
    """
    OLC 单向链路方向平均响应幅度.

    T(f, n) = |i·2πfL/c · sinc[πfL/c·(1-n·u)]|

    Sky average over 200 directions.

    Parameters
    ----------
    f : float
        频率 (Hz)
    L : float
        臂长 (m)

    Returns
    -------
    <|T|> : float
        方向平均响应幅度
    """
    beta = np.pi * np.abs(f) * L / c
    n_dirs = 200
    cos_nu_vals = np.linspace(-1, 1, n_dirs)
    t_vals = np.zeros_like(cos_nu_vals, dtype=complex)
    for i, cos_nu in enumerate(cos_nu_vals):
        arg = beta * (1.0 - cos_nu)
        if abs(arg) < 1e-15:
            sinc_v = 1.0
        else:
            sinc_v = np.sin(arg) / arg
        t_vals[i] = 1j * 2.0 * np.pi * np.abs(f) * L / c * sinc_v * np.exp(-1j * beta * (1.0 - cos_nu))
    return np.mean(np.abs(t_vals))


def olc_response_auto_avg(f_vals, L):
    """计算 f_vals 各点处的方向平均响应幅度."""
    return np.array([olc_response_magnitude_sky_avg(f, L) for f in f_vals])


# ---------------------------------------------------------------------------
# 灵敏度计算
# ---------------------------------------------------------------------------

def gw_strain_sensitivity(f, noise_coeffs, L, response_avg=True):
    """
    GW 应变灵敏度: h_sens(f) = sqrt(S_h(f))

    S_h(f) = S_y(f) / |T(f)|²    where S_y(f) is the frequency noise PSD

    Parameters
    ----------
    f : array-like
        频率 (Hz)
    noise_coeffs : list of (h, alpha) tuples
        Allan 方差噪声系数
    L : float
        臂长 (m)
    response_avg : bool
        如果 True, 使用方向平均响应；如果 False, 使用典型值 (n·u = 0)

    Returns
    -------
    S_h : ndarray
        应变功率谱密度 (Hz⁻¹)
    h_sens : ndarray
        应变灵敏度谱 (Hz⁻¹/²)
    S_y : ndarray
        频率噪声 PSD (1/Hz)
    """
    f = np.asarray(f, dtype=float)
    S_y = noise_psd(f, noise_coeffs)
    T = np.array([olc_response_magnitude_sky_avg(fi, L) for fi in f])
    # avoid division by zero
    T = np.maximum(T, 1e-30)
    S_h = S_y / T**2
    h_sens = np.sqrt(S_h)
    return S_h, h_sens, S_y


# ---------------------------------------------------------------------------
# 绘图
# ---------------------------------------------------------------------------



def plot_sensitivity(f, h_sens_all, labels, L, filename=None):
    """
    Plot GW strain sensitivity for multiple noise models.

    Parameters
    ----------
    f : ndarray
        频率 (Hz)
    h_sens_all : list of ndarray
        每条灵敏度曲线 (Hz⁻¹/²)
    labels : list of str
        图例标签
    L : float
        臂长 (m)
    filename : str, optional
        输出文件名
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    for h_sens, label in zip(h_sens_all, labels):
        ax.plot(f, h_sens, label=label, linewidth=2)

    # Add LISA and PTA reference curves
    f_ref = f
    # LISA strain sensitivity (approximate, ~ 1e-20 / sqrt(Hz) at mHz)
    h_lisa = 1e-20 * np.ones_like(f_ref) * (100 / f_ref)  # sloped for comparison
    # PTA sensitivity (much higher at nHz)
    h_pta = 1e-15 * np.ones_like(f_ref) * (1e-9 / f_ref**2)  # just for visual reference

    # Only add LISA curve in the mHz-kHz range for visibility
    mask_lisa = (f_ref > 1e-4) & (f_ref < 1)
    if np.any(mask_lisa):
        ax.plot(f_ref[mask_lisa], h_lisa[mask_lisa], '--', label='LISA reference (est.)',
                linewidth=1.5, alpha=0.5)

    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel(r'$h_{\rm sens}(f) = \sqrt{S_h(f)}$  (Hz$^{-1/2}$)')
    ax.set_title(f'OLC Single-Detector GW Strain Sensitivity (Arm L = {L} m)')
    ax.legend(fontsize=9)
    ax.set_xlim(f[0], f[-1])
    ax.set_ylim(bottom=1e-25)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    ax.set_xscale('log')

    plt.tight_layout()

    if filename is None:
        base = '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts'
        filename = os.path.join(base, f'olc_sensitivity_L{int(L)}m.png')
    plt.savefig(filename, dpi=200)
    print(f"  Saved: {filename}")
    plt.close()
    return fig


def _plot_noise_psd_components(f, noise_coeffs):
    """Plot PSD components and save."""
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    comp_names = ['h_0 (white freq)', r'h$_{-1}$ (flicker freq)', 'h_2 (white phase)']
    for (h, alpha), name in zip(noise_coeffs, comp_names):
        ax.plot(f, noise_psd(f, [(h, alpha)]), '--', label=name, linewidth=1.5, alpha=0.7)
    S_y_total = noise_psd(f, noise_coeffs)
    ax.plot(f, S_y_total, '-', label='Total S_y(f)', linewidth=2)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel(r'$S_y(f)$  (1/Hz)')
    ax.set_title('Frequency Noise PSD — Allan Variance Components')
    ax.legend(fontsize=9)
    ax.set_xlim(f[0], f[-1])
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    outpath = '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_noise_components.png'
    plt.savefig(outpath, dpi=200)
    print(f"  Saved: olc_noise_components.png")
    plt.close()


def plot_allan_vs_psd(f, noise_coeffs, filename=None):
    """
    Compare noise PSD with equivalent Allan variance.
    Demonstrates the conversion between PSD and Allan variance notations.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    S_y = noise_psd(f, noise_coeffs)
    ax.plot(f, S_y, '-', linewidth=2, label='S_y(f) PSD')

    # Calculate equivalent Allan variance at various integration times
    taus = np.logspace(-3, 2, 50)
    allan_vals = np.zeros_like(taus)
    for i, tau in enumerate(taus):
        f_inner = np.logspace(-4, 4, 500)
        S_y_inner = noise_psd(f_inner, noise_coeffs)
        filt = 2.0 * np.sin(np.pi * f_inner * tau / 2.0)**4 / (np.pi * f_inner * tau)**2
        filt = np.where(np.abs(f_inner * tau) < 1e-10, 0.0, filt)
        allan_vals[i] = 0.5 * np.trapezoid(S_y_inner * filt, f_inner)
        allan_vals[i] = max(allan_vals[i], 0)

    # Preserve twin-axis reference before reassigning ax
    twin_ax = ax.twinx()
    twin_ax.semilogx(taus, allan_vals, 'o', markersize=4, label=r"$\sigma_y^2(\tau)$ from PSD")
    twin_ax.set_ylabel(r'$\sigma_y^2(\tau)$ (Allan variance)')

    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel(r'$S_y(f)$  (1/Hz)')
    ax.set_title('PSD and Allan Variance — Cross-Check')
    ax.legend(loc='upper left')
    twin_ax.legend(loc='upper right')
    ax.set_yscale('log')

    # Panel 2: Allan variance contribution from each noise term
    ax = axes[1]
    term_labels = ['h_0 (white freq)', r'h$_{-1}$ (flicker)', 'h_2 (white phase)']
    for (h_coff, alpha), label in zip(noise_coeffs, term_labels):
        term_s2 = np.zeros_like(taus)
        for i, tau in enumerate(taus):
            f_inner = np.logspace(-4, 4, 500)
            S_term = h_coff * f_inner ** alpha
            filt = 2.0 * np.sin(np.pi * f_inner * tau / 2.0)**4 / (np.pi * f_inner * tau)**2
            filt = np.where(np.abs(f_inner * tau) < 1e-10, 0.0, filt)
            term_s2[i] = 0.5 * np.trapezoid(S_term * filt, f_inner)
            term_s2[i] = max(term_s2[i], 0)
        ax.semilogx(taus, term_s2, '--', label=label, linewidth=1.5)
    ax.plot(taus, allan_vals, '-', linewidth=2, label='Total σ_y²(τ)')
    ax.set_xlabel('Integration time τ (s)')
    ax.set_ylabel(r'Allan Variance σ_y²(τ)')
    ax.set_title('Allan Variance — Individual Noise Terms')
    ax.legend(fontsize=8)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left')

    plt.tight_layout()

    if filename is None:
        base = '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts'
        filename = os.path.join(base, 'olc_allan_variance_crosscheck.png')
    plt.savefig(filename, dpi=200)
    print(f"  Saved: {filename}")
    plt.close()
    return fig


# ---------------------------------------------------------------------------
# 多臂长扫描
# ---------------------------------------------------------------------------

def sensitivity_sweep_arm_lengths():
    """
    Scan several arm lengths and compare sensitivities.
    """
    f = np.logspace(-2, 3, 200)  # 0.01 Hz to 1 kHz

    L_vals = [1.0, 5.0, 10.0, 50.0]
    h_sens_all = []
    labels = []
    coeffs = sr_clock_coeffs()

    for L in L_vals:
        _, h_sens, _ = gw_strain_sensitivity(f, coeffs, L)
        h_sens_all.append(h_sens)
        labels.append(f'L = {L} m')

    fig = plot_sensitivity(f, h_sens_all, labels, L_vals[0])

    # Also: best L for each frequency (optimize)
    L_optimal = np.argmin(np.array([h_sens_all[i] for i in range(len(L_vals))], dtype=object), axis=0)
    print("  Arm length sensitivity sweep complete.")


# ---------------------------------------------------------------------------
# 噪声水平扫描
# ---------------------------------------------------------------------------

def sensitivity_sweep_noise_levels():
    """
    Compare Sr clock (best), LISA-like, and LLO-like noise levels.
    """
    f = np.logspace(-2, 3, 300)

    models = [
        (sr_clock_coeffs(), 'Sr clock (best)'),
        (llo_clock_coeffs(), 'LLO clock (est.)'),
        (lisa_like_coeffs(), 'LISA-like reference'),
    ]

    h_sens_all = []
    labels = []
    components = None

    for coeffs, label in models:
        _, h_sens, S_y = gw_strain_sensitivity(f, coeffs, L=10.0)
        h_sens_all.append(h_sens)
        labels.append(label)
        if label == 'Sr clock (best)':
            components = coeffs

    fig = plot_sensitivity(f, h_sens_all, labels, L=10.0)

    # Also save data for reference
    np.save('/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_sensitivity_data.npy', {
        'f': f,
        'models': models,
        'h_sens': h_sens_all,
        'labels': labels,
        'L': 10.0,
    })
    print("  Saved: olc_sensitivity_data.npy")

    # Noise PSD components
    _plot_noise_psd_components(f, components)
    print("  Noise PSD component analysis complete.")

    # Allan variance cross-check
    plot_allan_vs_psd(f, components)
    print("  Allan variance cross-check complete.")

    return f, models, h_sens_all


# ---------------------------------------------------------------------------
# 辅助: 不同 Allan 方差模型对比
# ---------------------------------------------------------------------------

def detailed_allan_scan():
    """
    Compute Allan variance for several τ and model parameter sets.
    Produce a comparison table.
    """
    taus = np.array([0.001, 0.01, 0.1, 1.0, 10.0, 100.0])
    models = {
        'Sr clock (best)': sr_clock_coeffs(),
        'LLO (est.)': llo_clock_coeffs(),
        'LISA-like': lisa_like_coeffs(),
    }
    print("\n  Allan Variance σ_y²(τ)  vs  Integration Time")
    print(f"  {'τ (s)':>10s} | {'Sr':>14s} | {'LLO':>14s} | {'LISA-like':>14s}")
    print("  " + "-" * 55)
    for tau in taus:
        tau_f = float(tau)
        row = f"  {tau_f:10.4f} |"
        for name, coeffs in models.items():
            sigma2 = 0.0
            for h, alpha in coeffs:
                # Approximate Allan variance from each noise term
                # σ_y²(τ) for term h·f^α ≈ C·h·τ^(-α-1) where C is a geometric factor
                if alpha == 0:
                    sigma2 += h / (2 * tau_f)
                elif alpha == -1:
                    sigma2 += h * np.log(2) / (2 * tau_f)
                elif alpha == 2:
                    sigma2 += h * 2.0 * np.pi**2 / (2 * tau_f**3) * 0.5
                else:
                    sigma2 += h * tau_f ** (-alpha - 1)
            sigma2 = max(sigma2, 0)
            row += f" {sigma2:14.4e} |"
        print(row)


# ---------------------------------------------------------------------------
# Response function sweep
# ---------------------------------------------------------------------------

def response_sweep():
    """
    Scan direction-averaged response as function of f and L.
    Visualize the transition from low-f to high-f regimes.
    """
    f_vals = np.logspace(-3, 4, 80)
    L_vals = np.logspace(-1, 2, 40)  # 0.1 m to 100 m

    response_map = np.zeros((len(f_vals), len(L_vals)))
    for i, fi in enumerate(f_vals):
        for j, Lj in enumerate(L_vals):
            response_map[i, j] = olc_response_magnitude_sky_avg(fi, Lj)

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    # response_map has shape (N_f, N_L) — transpose to (N_L, N_f) for mesh
    DD, FF = np.meshgrid(L_vals, f_vals, indexing='ij')
    Im = ax.pcolormesh(DD, FF, np.log10(response_map.T + 1e-30),
                        cmap='viridis', shading='nearest')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Arm length L (m)')
    ax.set_ylabel('Frequency f (Hz)')
    ax.set_title('OLC Response |T| (log₁₀) — Sky Average')
    plt.colorbar(Im, ax=ax, label='log₁₀(|T|)')

    # Add α = 2πfL/c = 1 line
    alpha1_L = c / (2 * np.pi * f_vals)
    ax.plot(alpha1_L, f_vals, '--', color='white', linewidth=1.5,
            label=r'$\alpha = 2\pi fL/c = 1$')

    plt.legend(fontsize=9)
    plt.tight_layout()

    outpath = '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_response_heatmap.png'
    plt.savefig(outpath, dpi=200)
    print(f"  Saved: olc_response_heatmap.png")
    plt.close()

    # Also compute ratio: response/sinc (just the prefactor)
    # T = (i·2πfL/c) · sinc · exp[...]
    # |T| = (2πfL/c) · |sinc|  (exp is unit magnitude)
    # At low f: |T| ~ 2πfL/c → grows linearly with f
    # This means h_sens ∝ 1/√(f²) at low f — better sensitivity at higher f!
    print("  Response scan complete. |T| ∝ f at low f → better sensitivity at high f.")
    return response_map


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("OLC 单探测器噪声谱 & GW 应变灵敏度")
    print("=" * 60)

    t0 = time.time()

    # 1. Detailed Allan variance scan
    print("\n[1] Allan 方差 - 积分时间扫描:")
    detailed_allan_scan()

    # 2. Sensitivity vs noise levels
    print("\n[2] GW 应变灵敏度 (噪声水平对比):")
    f, models, h_sens_all = sensitivity_sweep_noise_levels()

    # 3. Response function sweep
    print("\n[3] 响应函数热图:")
    response_sweep()

    # 4. Arm length sweep
    print("\n[4] 臂长扫描:")
    sensitivity_sweep_arm_lengths()

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")
    print("=" * 60)


if __name__ == '__main__':
    main()
