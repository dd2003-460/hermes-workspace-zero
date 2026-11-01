"""
组件D 02: LISA-Taiji 三通道 (X+Y+Z) 联合 Fisher 灵敏度

动机：单 X 通道 Γ^V ≪ Γ^I（4-6 orders），不足以探测手征信号。
三通道联合 Fisher 矩阵可以组合三个通道的信息，可能提升 V 通道灵敏度。

方法：
1. 从 C2 asm 模块获取 X/Y/Z 三通道的 Γ^I, Γ^V（每个频率点）
2. 构造 2×3 Fisher 矩阵（参数 I,V × 通道 X,Y,Z）
3. 对角化得到 I_min, V_min
4. 对比单通道 vs 三通道灵敏度增益
"""

import numpy as np
from importlib import util
import os, sys, time

def load_module(name, path):
    spec = util.spec_from_file_location(name, path)
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# Load stage 3 C2 assembly module
_c2_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..', '..', '阶段3_具体探测器ORF',
                       '组件C2_天基SbLI_TDI正确组装', '具体计算')
asm = load_module("asm", os.path.join(_c2_dir, "01_TDI通道用单向链路Gamma_one正确组装.py"))

AU = 1.495978707e8
C_LIGHT = asm.C_LIGHT


def lisa_like_constellation(center, L, n_hat, phase=0.0):
    """Generate 3 satellite positions for a LISA-like triangular constellation."""
    # Build local frame: n_hat is the plane normal
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


def get_channel_terms(r_sat, L, f, channel="X"):
    """
    Get TDI terms for a given channel (X, Y, Z) of a single constellation.
    
    TDI channels are defined by specific combinations of link delays.
    For an equilateral triangle with satellites 1,2,3 and links 1→2, 2→3, 3→1:
      X = s1 - s2 (one-way difference)
      Y = s2 - s3
      Z = s3 - s1
    
    In the TDI formalism, each channel is a linear combination of
    one-way link responses with specific delay weights.
    
    For simplicity and consistency with C2's tdi_X_terms, we use the same
    geometric construction but with different phase offsets for Y/Z.
    """
    # The three links of the triangle
    # Link k: from sat[k] to sat[(k+1)%3], direction d_k, length L
    links = []
    for k in range(3):
        i, j = k, (k + 1) % 3
        delta_r = r_sat[j] - r_sat[i]
        d = delta_r / np.linalg.norm(delta_r)
        links.append({"r": r_sat[i].copy(), "d": d, "L": L})
    
    # TDI channel definitions (simplified: X uses links with +1/-1 weights)
    # Full TDI: X = Σ w_k * response_k where w_k are complex delay factors
    # For the ORF calculation, we need the terms that go into gamma_TDI_channels
    # which expects terms with r (receiver position), d (link direction), L, w (weight)
    
    # For X channel: standard TDI-X construction (same as C2)
    # For Y/Z: rotate the weight pattern
    k_wave = 2 * np.pi * f / C_LIGHT
    
    if channel == "X":
        # Standard: X = h(t1) - h(t2) type combination
        # In TDI language: X involves all 3 links with specific delay phases
        weights = [1.0, -1.0, 0.0]  # Simplified; full TDI has complex delay weights
    elif channel == "Y":
        weights = [0.0, 1.0, -1.0]
    elif channel == "Z":
        weights = [-1.0, 0.0, 1.0]
    
    terms = []
    for k in range(3):
        link = links[k]
        # TDI delay phase: signal travels along the link
        delay_phase = np.exp(-1j * k_wave * L)
        w = weights[k] * delay_phase
        if abs(w) > 1e-15:
            terms.append({
                "r": link["r"],
                "d": link["d"],
                "L": L,
                "w": w
            })
    
    return terms


def compute_orf_pair(rL, rT, L_LISA, L_TAIJI, f, channel="X"):
    """Compute Γ^I and Γ^V for a pair of constellations on a given channel."""
    tL = get_channel_terms(rL, L_LISA, f, channel)
    tT = get_channel_terms(rT, L_TAIJI, f, channel)
    
    if not tL or not tT:
        return 0.0 + 0.0j, 0.0 + 0.0j
    
    gI = asm.gamma_TDI_channels(tL, tT, f, kind="I")
    gV = asm.gamma_TDI_channels(tL, tT, f, kind="V")
    return gI, gV


def fisher_information_multi_channel(Gamma_I, Gamma_V, S_noise, n_channels=3):
    """
    Joint Fisher information matrix for parameters (I, V) using multiple channels.
    
    Parameters
    ----------
    Gamma_I : list of complex, one per channel — Γ^I for each TDI channel
    Gamma_V : list of complex, one per channel — Γ^V for each TDI channel
    S_noise : float — noise ASD (assumed same for all channels, simplified)
    
    Returns
    -------
    F : 2x2 array — Fisher information matrix [[F_II, F_IV], [F_VI, F_VV]]
    """
    F_II = 0.0
    F_IV = 0.0
    F_VV = 0.0
    
    for c in range(n_channels):
        GI = Gamma_I[c]
        GV = Gamma_V[c]
        
        # For each channel, the observable is x_c = 0.5*(Γ^I_c * I + Γ^V_c * V) + noise
        # Re(x_c) = 0.5 * Re(Γ^I_c) * I + 0.5 * Re(Γ^V_c) * V  → but Γ^V is pure imaginary
        # Im(x_c) = 0.5 * Im(Γ^I_c) * I + 0.5 * Im(Γ^V_c) * V  → but Γ^I is real
        
        # Since Γ^I is real-symmetric and Γ^V is pure-imaginary-antisymmetric:
        # Re(x_c) = 0.5 * Γ^I_c * I  (only I contributes to real part)
        # Im(x_c) = 0.5 * Im(Γ^V_c) * V  (only V contributes to imag part)
        
        # Fisher for I from real part:
        F_II += (0.5 * GI.real) ** 2 / S_noise
        # Fisher for V from imag part:
        F_VV += (0.5 * GV.imag) ** 2 / S_noise
        # Cross term (zero due to separation principle):
        F_IV += 0.0
    
    return np.array([[F_II, F_IV], [F_IV, F_VV]])


if __name__ == "__main__":
    # Setup LISA-Taiji constellation (same as C2 main())
    L_LISA = 3.0e6   # km
    L_TAIJI = 3.0e6  # km
    
    n_lisa = np.array([0.0, 0.0, 1.0])
    theta_t = np.deg2rad(70.0)
    n_taiji = np.array([np.sin(theta_t), 0.0, np.cos(theta_t)])
    c_lisa = np.array([-0.4 * AU, 0.0, 0.0])
    c_taiji = np.array([0.4 * AU * np.cos(np.deg2rad(40)),
                        0.4 * AU * np.sin(np.deg2rad(40)), 0.0])
    
    rL = lisa_like_constellation(c_lisa, L_LISA, n_lisa, phase=0.0)
    rT = lisa_like_constellation(c_taiji, L_TAIJI, n_taiji, phase=0.3)
    
    print("=" * 70)
    print("LISA-Taiji 三通道联合 Fisher 灵敏度")
    print("=" * 70)
    print(f"LISA arm={L_LISA:.2e} km, Taiji arm={L_TAIJI:.2e} km")
    print(f"Constellation separation: {np.linalg.norm(c_taiji-c_lisa)/AU:.3f} AU")
    print(f"Plane inclination: {np.rad2deg(np.arccos(np.clip(n_lisa@n_taiji,-1,1))):.1f}°")
    
    # Noise model (simplified flat)
    S_n = 1e-45  # Hz^-1
    
    # Frequency grid (valid range: β_L < 1 → f < c/(2πL) ≈ 5 mHz)
    fs = np.logspace(-4, np.log10(5e-3), 10)
    
    print(f"\n{'f [Hz]':>10} {'β_L':>8} {'Γ^I_X':>12} {'Γ^I_Y':>12} {'Γ^I_Z':>12} | "
          f"{'|Γ^V_X|':>10} {'|Γ^V_Y|':>10} {'|Γ^V_Z|':>10} | "
          f"{'SNR_I_1ch':>10} {'SNR_I_3ch':>10} {'SNR_V_1ch':>10} {'SNR_V_3ch':>10}")
    print("-" * 140)
    
    results = []
    for f in fs:
        beta_L = 2 * np.pi * f * L_LISA / C_LIGHT
        
        # Compute ORF for all 3 channels
        GI = []
        GV = []
        for ch in ["X", "Y", "Z"]:
            t0 = time.time()
            gI_c, gV_c = compute_orf_pair(rL, rT, L_LISA, L_TAIJI, f, ch)
            GI.append(gI_c)
            GV.append(gV_c)
        
        # Single-channel Fisher (X only)
        F_1ch = np.array([[(0.5*GI[0].real)**2/S_n, 0],
                          [0, (0.5*GV[0].imag)**2/S_n]])
        
        # Three-channel joint Fisher
        F_3ch = fisher_information_multi_channel(GI, GV, S_n, n_channels=3)
        
        # Sensitivity: I_min = 1.645/sqrt(F_II), V_min = 1.645/sqrt(F_VV)
        I_min_1ch = 1.645 / np.sqrt(max(F_1ch[0,0], 1e-100))
        V_min_1ch = 1.645 / np.sqrt(max(F_1ch[1,1], 1e-100))
        I_min_3ch = 1.645 / np.sqrt(max(F_3ch[0,0], 1e-100))
        V_min_3ch = 1.645 / np.sqrt(max(F_3ch[1,1], 1e-100))
        
        # SNR for a reference signal A=1e-45 (dimensionless)
        SNR_I_1ch = 1e-45 / I_min_1ch if I_min_1ch > 0 else 0
        SNR_I_3ch = 1e-45 / I_min_3ch if I_min_3ch > 0 else 0
        SNR_V_1ch = 1e-45 / V_min_1ch if V_min_1ch > 0 else 0
        SNR_V_3ch = 1e-45 / V_min_3ch if V_min_3ch > 0 else 0
        
        results.append((f, beta_L, GI, GV, I_min_1ch, I_min_3ch, V_min_1ch, V_min_3ch))
        
        print(f"{f:10.2e} {beta_L:8.4f} "
              f"{GI[0].real:+12.4e} {GI[1].real:+12.4e} {GI[2].real:+12.4e} | "
              f"{abs(GV[0].imag):10.2e} {abs(GV[1].imag):10.2e} {abs(GV[2].imag):10.2e} | "
              f"{SNR_I_1ch:10.2e} {SNR_I_3ch:10.2e} {SNR_V_1ch:10.2e} {SNR_V_3ch:10.2e}")
    
    print("\n" + "=" * 70)
    print("灵敏度增益（三通道 vs 单通道）:")
    print("=" * 70)
    print(f"{'f [Hz]':>10} {'I增益':>10} {'V增益':>10} {'说明'}")
    for f, b, GI, GV, I1, I3, V1, V3 in results:
        gain_I = I1/I3 if I3 > 0 else float('inf')
        gain_V = V1/V3 if V3 > 0 else float('inf')
        note = ""
        if gain_I > 1.5:
            note = "← 三通道显著改善"
        elif gain_I < 0.7:
            note = "← 三通道反而变差（检查！）"
        print(f"{f:10.2e} {gain_I:10.2f} {gain_V:10.2f} {note}")
    
    print("\n结论:")
    print("- 分离原理使 Fisher 矩阵严格对角（F_IV=0），I/V 独立")
    print("- 三通道增益 = sqrt(Σ_c Γ²_c / Γ²_X)（对 I 和 V 分别计算）")
    print("- 若 Y/Z 通道的 |Γ| 与 X 同量级，增益 ~sqrt(3)≈1.73")
    print("- 若 Y/Z 远小于 X（几何消去），增益接近 1（无改善）")
