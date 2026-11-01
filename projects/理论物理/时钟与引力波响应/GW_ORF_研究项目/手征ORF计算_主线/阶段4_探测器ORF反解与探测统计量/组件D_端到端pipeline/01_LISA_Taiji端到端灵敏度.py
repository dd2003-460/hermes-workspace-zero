"""
组件D 01: LISA-Taiji 端到端灵敏度

用阶段3 C2 的真实 ORF（asm.gamma_TDI_channels）+ 文献噪声模型，
计算 I/V 通道的 Fisher 信息和最小可探测信号。

注意：C2 的 ORF 是单通道（X channel）的 Γ^I, Γ^V，不是 3×3 矩阵。
这里把它当作 n_pairs=1 的特例处理（两个 TDI 通道互相关）。
"""

import numpy as np
from importlib import util
import os, sys


def load_module(name, path):
    spec = util.spec_from_file_location(name, path)
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Load stage 3 C2 modules
_c2_dir = os.path.join(os.path.dirname(__file__), '..', '..', '阶段3_具体探测器ORF', '组件C2_天基SbLI_TDI正确组装', '具体计算')
lisa_taiji = load_module("lisa_taiji", os.path.join(_c2_dir, "02_真实LISA_Taiji网络手征ORF全频率计算.py"))
asm = lisa_taiji.asm

# LISA + Taiji noise models (literature values, simplified)
def S_noise_LISA(f):
    """LISA single-link noise ASD [Hz^-1], ~1e-45 at mHz band."""
    # Simplified: flat 1e-45 in 1e-4 to 1e-2 Hz, rising at low/high
    S = np.ones_like(f) * 1e-45
    S *= 1.0 + 10 * (f / 1e-3)**(-2)  # rises below mHz
    S *= 1.0 + 10 * (f / 1e-1)**2     # rises above 100 mHz
    return S

def S_noise_Taiji(f):
    """Taiji single-link noise ASD [Hz^-1], similar to LISA but slightly worse."""
    S = np.ones_like(f) * 2e-45
    S *= 1.0 + 10 * (f / 1e-3)**(-2)
    S *= 1.0 + 10 * (f / 1e-1)**2
    return S


if __name__ == "__main__":
    # Reproduce the constellation from C2 main()
    AU = 1.495978707e8
    C = asm.C_LIGHT
    L_LISA = 3.0e6
    L_TAIJI = 3.0e6
    
    n_lisa = np.array([0.0, 0.0, 1.0])
    theta_t = np.deg2rad(70.0)
    n_taiji = np.array([np.sin(theta_t), 0.0, np.cos(theta_t)])
    c_lisa = np.array([-0.4 * AU, 0.0, 0.0])
    c_taiji = np.array([0.4 * AU * np.cos(np.deg2rad(40)),
                        0.4 * AU * np.sin(np.deg2rad(40)), 0.0])
    
    rL = lisa_taiji.lisa_like_constellation(c_lisa, L_LISA, n_lisa, phase=0.0)
    rT = lisa_taiji.lisa_like_constellation(c_taiji, L_TAIJI, n_taiji, phase=0.3)
    
    print(f"LISA-Taiji network: ΔL = {np.linalg.norm(c_taiji - c_lisa)/AU:.3f} AU")
    print(f"Tilt angle: {np.rad2deg(np.arccos(np.clip(n_lisa@n_taiji,-1,1))):.1f}°")
    
    # Frequency scan
    fs = np.logspace(-4, -1.5, 10)
    
    print(f"\n{'f [Hz]':>10} | {'Γ^I_X':>12} | {'|Γ^V_X|':>12} | {'SNR_I(1e-45)':>13} | {'SNR_V(1e-45)':>13}")
    print("-" * 80)
    
    for f in fs:
        tL = asm.tdi_X_terms(*rL, L_LISA, f)
        tT = asm.tdi_X_terms(*rT, L_TAIJI, f)
        gI = asm.gamma_TDI_channels(tL, tT, f, kind="I")
        gV = asm.gamma_TDI_channels(tL, tT, f, kind="V")
        
        gamma_I_val = gI.real
        gamma_V_val = abs(gV.imag)
        
        # For single pair (2 TDI channels): Fisher info = Γ²/(4*S_n1*S_n2)
        Sn1 = S_noise_LISA(np.array([f]))[0]
        Sn2 = S_noise_Taiji(np.array([f]))[0]
        
        F_II = gamma_I_val**2 / (4 * Sn1 * Sn2)
        F_VV = gamma_V_val**2 / (4 * Sn1 * Sn2)
        
        # SNR for a signal of amplitude A: SNR = A * sqrt(F)
        A_test = 1e-45  # test signal level
        snr_I = A_test * np.sqrt(max(F_II, 0))
        snr_V = A_test * np.sqrt(max(F_VV, 0))
        
        print(f"{f:10.2e} | {gamma_I_val:+12.4e} | {gamma_V_val:12.4e} | {snr_I:13.3e} | {snr_V:13.3e}")
    
    print("\nNote: SNR shown for A=1e-45 (dimensionless strain amplitude).")
    print("Detection threshold: SNR > 3 (95% one-sided).")
    print("Minimum detectable: A_min = 3/sqrt(Fisher)")
