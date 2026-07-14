#!/usr/bin/env python3
"""
Focused Chiral ORF (Gamma^V) Comparison for v17 Paper
========================================================

Compute chiral ORF values for the LISA x Taiji configuration with
inclination = pi/6, matching the v17 Section 3.5.6 table.

Uses the TDI E-variable CW-sum antenna pattern (not Michelson):
  - 3-link clockwise sum: E ~ d(1->2) + d(2->3) + d(3->1)
  - Breaks reflection symmetry => R_cross != 0 => chiral ORF possible
  - OLC transfer function per link: T = 1j * 2*pi*f*L/c * sinc(beta*(1-cos_nu)) * exp(-i*beta*(1-cos_nu))
  - Spatial phase factor per link: exp(-2*pi*i*f/c * k_hat . delta_r_ij)

Reference:
  - v17 Section 3.5.6 (paper main-paper-v17.tex lines 963-989)
  - Orlando et al. (arXiv:2011.07059) JCAP 069 (2021)
  - Multi-constellation script: 11-multi-constellation-chiral-orf.py
"""
import numpy as np
import time

c = 299792458.0


# ━━━ OLC One-Way Link Transfer Function (Lou Eq. 2-30) ━━━━━━━━━━━━━━━━━━━━━━━

def olc_transfer_function(f, L, cos_nu):
    """
    One-way link transfer function for OLC (Lou Eq. 2-30).

    T(f, cos_nu) = 1j * 2*pi*f*L/c * sinc(beta*(1-cos_nu)) * exp(-i*beta*(1-cos_nu))
    where beta = pi*f*L/c.

    Uses (1 - cos_nu) NOT (1 - |cos_nu|). Correct per Lou Eq. 2-30.
    """
    f = np.atleast_1d(f)
    scalar_in = np.isscalar(f)
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - cos_nu
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f) * L / c
    result = prefac * sinc_v * phase
    return result[0] if scalar_in else result


# ━━━ E-variable Antenna Pattern ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def antenna_pattern_e_variable(tG, pG, satellite_positions, L):
    """
    E-variable antenna pattern via clockwise (CW) link sum.

    For equilateral triangles, the E variable uses:
      R_E+ = sum_{k=CW} F_+(link_k) * T(link_k)
      R_Ex = sum_{k=CW} F_x(link_k) * T(link_k)

    where the sum is over 3 clockwise links: 0->1, 1->2, 2->0.

    Args:
        tG, pG: GW direction grid (theta, phi), shape (Ntheta, Nphi)
        satellite_positions: 3x3 array of satellite positions (m)
        L: arm length (m)

    Returns:
        R_plus, R_cross: complex antenna patterns, shape (Ntheta, Nphi)
    """
    tG_a = np.asarray(tG)
    pG_a = np.asarray(pG)

    # GW propagation direction
    nx = np.sin(tG_a) * np.cos(pG_a)
    ny = np.sin(tG_a) * np.sin(pG_a)
    nz = np.cos(tG_a)

    # Polarization basis vectors
    th = np.array([np.cos(tG_a) * np.cos(pG_a),
                    np.cos(tG_a) * np.sin(pG_a),
                    -np.sin(tG_a)])
    ph = np.array([-np.sin(pG_a),
                    np.cos(pG_a),
                    np.zeros_like(pG_a, dtype=np.float64)])

    # CW links: 0->1, 1->2, 2->0
    cw_links = [(0, 1), (1, 2), (2, 0)]

    R_plus = np.zeros_like(tG_a, dtype=np.complex128)
    R_cross = np.zeros_like(tG_a, dtype=np.complex128)

    for i, j in cw_links:
        u = satellite_positions[j] - satellite_positions[i]
        u = u / np.linalg.norm(u)

        # Antenna pattern for this link
        th_dot_u = th[0] * u[0] + th[1] * u[1] + th[2] * u[2]
        ph_dot_u = ph[0] * u[0] + ph[1] * u[1] + ph[2] * u[2]

        F_plus = th_dot_u ** 2 - ph_dot_u ** 2
        F_cross = 2.0 * th_dot_u * ph_dot_u

        # OLC transfer function
        cos_nu = nx * u[0] + ny * u[1] + nz * u[2]
        T = olc_transfer_function(np.ones_like(tG_a, dtype=np.float64), L, cos_nu)

        R_plus += F_plus * T
        R_cross += F_cross * T

    return R_plus, R_cross


# ━━━ Cross-Constellation ORF Computation ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def compute_cross_e_variable_orf(f, posA, L1, posB, L2,
                                  include_spatial_phase=True, delta_x=None,
                                  ntheta=64, nphi=128):
    """
    Compute raw chiral ORF Gamma^V and Gamma^I for E-variable detectors.

    Gamma^I = <conj(R1p)*R2p + conj(R1x)*R2x>_sky
    Gamma^V = <conj(R1p)*R2x - conj(R1x)*R2p>_sky

    where <...>_sky denotes sky average (integral over 4*pi).

    Returns: (gamma_I, gamma_V, S_A, S_B) where S_A, S_B are auto-responses
    for normalization (R^V = Gamma^V / sqrt(S_A * S_B)).
    """
    tG = np.linspace(0, np.pi, ntheta)
    pG = np.linspace(0, 2 * np.pi, nphi, endpoint=False)
    TG, PG = np.meshgrid(tG, pG, indexing='ij')
    dth = np.pi / (ntheta - 1)
    dph = 2.0 * np.pi / nphi
    dO = np.sin(TG) * dth * dph

    # E-variable antenna patterns
    R1p, R1x = antenna_pattern_e_variable(TG, PG, posA, L1)
    R2p, R2x = antenna_pattern_e_variable(TG, PG, posB, L2)

    # Spatial phase factor
    if include_spatial_phase and delta_x is not None:
        # Phase factor for inter-constellation separation
        k_hat = np.array([
            np.sin(TG) * np.cos(PG),
            np.sin(TG) * np.sin(PG),
            np.cos(TG)
        ])
        delta_x_exp = delta_x.reshape(3, 1, 1)
        k_dot_delta = np.sum(k_hat * delta_x_exp, axis=0)
        omega = 2.0 * np.pi * f
        phase = np.exp(-1j * omega / c * k_dot_delta)
    else:
        phase = np.ones_like(TG)

    # Cross-correlation (parity-even)
    cross_corr = np.conj(R1p) * R2p + np.conj(R1x) * R2x
    # Chiral correlation (parity-odd)
    chiral_corr = np.conj(R1p) * R2x - np.conj(R1x) * R2p

    # Sky integrals (average over 4*pi)
    gamma_I = np.real(np.sum(phase * cross_corr * dO)) / (4.0 * np.pi)
    gamma_V = np.real(np.sum(phase * chiral_corr * dO)) / (4.0 * np.pi)

    # Auto-responses for normalization
    S_A = np.real(np.sum((np.conj(R1p) * R1p + np.conj(R1x) * R1x) * dO)) / (4.0 * np.pi)
    S_B = np.real(np.sum((np.conj(R2p) * R2p + np.conj(R2x) * R2x) * dO)) / (4.0 * np.pi)

    return gamma_I, gamma_V, S_A, S_B


# ━━━ Constellation Builder ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def build_constellation(arm_length, inclination_deg, rotation_deg=0.0):
    """
    Build triangular constellation positions.

    Args:
        arm_length: physical arm length (m)
        inclination_deg: inclination to ecliptic (rotation about x-axis)
        rotation_deg: rotation about z-axis

    Returns:
        positions: 3x3 array of satellite positions (m)
    """
    cos_i = np.cos(np.radians(inclination_deg))
    sin_i = np.sin(np.radians(inclination_deg))
    cos_r = np.cos(np.radians(rotation_deg))
    sin_r = np.sin(np.radians(rotation_deg))

    # Equilateral triangle in xy-plane
    r0 = np.array([0.0, 0.0, 0.0])
    r1 = np.array([arm_length, 0.0, 0.0])
    r2 = np.array([arm_length / 2.0, arm_length * np.sqrt(3) / 2.0, 0.0])
    positions = np.array([r0, r1, r2])

    # Inclination: rotation about x-axis
    rotated = np.zeros_like(positions)
    rotated[:, 0] = positions[:, 0]
    rotated[:, 1] = positions[:, 1] * cos_i - positions[:, 2] * sin_i
    rotated[:, 2] = positions[:, 1] * sin_i + positions[:, 2] * cos_i
    positions = rotated

    # Rotation about z-axis
    if rotation_deg != 0:
        new_pos = np.zeros_like(positions)
        new_pos[:, 0] = positions[:, 0] * cos_r - positions[:, 1] * sin_r
        new_pos[:, 1] = positions[:, 0] * sin_r + positions[:, 1] * cos_r
        new_pos[:, 2] = positions[:, 2]
        positions = new_pos

    return positions


# ━━━ Output Formatting ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def format_latex_sci(val, prec=6):
    """Format value as LaTeX scientific notation."""
    if abs(val) < 1e-30 or val == 0:
        return "0.000000"
    exponent = int(np.floor(np.log10(abs(val))))
    mantissa = round(val / (10 ** exponent), prec)
    if abs(mantissa) >= 10.0:
        mantissa /= 10.0
        exponent += 1
    sign = "-" if mantissa < 0 else ""
    mant_str = f"{abs(mantissa):.{prec}f}"
    if exponent == 0:
        return f"{sign}{mant_str}"
    return f"{sign}{mant_str} \\\\times 10^{{{exponent}}}"


# ━━━ Main ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    print("=" * 70)
    print("Chiral ORF (Gamma^V) -- LISA x Taiji (inclination = pi/6)")
    print("TDI E-variable CW-sum antenna pattern with OLC transfer function")
    print("=" * 70)

    # Configuration
    inclination_lisa_deg = 30.0  # pi/6
    print(f"\n  LISA inclination: {inclination_lisa_deg} deg (pi/6)")
    print(f"  Taiji inclination: 0 deg (ecliptic plane)")

    # Arm lengths
    L1 = 2.5e9  # LISA: 2.5 Gm
    L2 = 3.0e9  # Taiji: 3.0 Gm

    # Build constellations
    posA = build_constellation(L1, inclination_lisa_deg, rotation_deg=0.0)
    posB = build_constellation(L2, 0.0, rotation_deg=0.0)

    # Constellation separation (1 AU in z-direction)
    au = 1.496e11
    delta_x = np.array([0.0, 0.0, au])
    print(f"  Arm lengths: LISA = {L1/1e6:.0f} Mkm, Taiji = {L2/1e6:.0f} Mkm")
    print(f"  Constellation separation: 1.0 AU in z-direction")

    # Sky grid
    ntheta, nphi = 64, 128
    print(f"\n  Sky grid: {ntheta} x {nphi} = {ntheta*nphi} points")

    frequencies = [0.001, 0.01, 0.1]  # Hz
    print(f"  GW frequencies: {[f*1000 for f in frequencies]} mHz")
    print(f"  Transfer function: OLC T = 1j*2*pi*f*L/c * sinc(beta*(1-cos_nu))")
    print(f"                     (no abs, corrected)")

    results = []

    for f in frequencies:
        print(f"\n  --- f = {f} Hz ({f*1000:.3f} mHz) ---")
        wavelength = c / f
        phase_arg = f * au / c
        print(f"    GW wavelength: {wavelength / au:.2f} AU")
        print(f"    Phase argument f*d/c: {phase_arg:.6f}")

        # WITH spatial phase
        t0 = time.time()
        gammaI_with, gammaV_with, SA, SB = compute_cross_e_variable_orf(
            f, posA, L1, posB, L2,
            include_spatial_phase=True, delta_x=delta_x,
            ntheta=ntheta, nphi=nphi)
        norm = np.sqrt(SA * SB) if SA * SB > 0 else 1.0
        rV_with = gammaV_with / norm
        rI_with = gammaI_with / norm
        print(f"    [WITH spatial phase]   Gamma^I = {gammaI_with:.8e}")
        print(f"                            Gamma^V = {gammaV_with:.8e}")
        print(f"                            R^I = {rI_with:.8f}")
        print(f"                            R^V = {rV_with:.8e}")
        print(f"                            SA = {SA:.6e}, SB = {SB:.6e}")
        print(f"                            Time: {time.time()-t0:.1f}s")

        # WITHOUT spatial phase
        t0 = time.time()
        gammaI_without, gammaV_without, SA2, SB2 = compute_cross_e_variable_orf(
            f, posA, L1, posB, L2,
            include_spatial_phase=False, delta_x=None,
            ntheta=ntheta, nphi=nphi)
        norm2 = np.sqrt(SA2 * SB2) if SA2 * SB2 > 0 else 1.0
        rV_without = gammaV_without / norm2
        rI_without = gammaI_without / norm2
        print(f"    [WITHOUT spatial phase] Gamma^I = {gammaI_without:.8e}")
        print(f"                            Gamma^V = {gammaV_without:.8e}")
        print(f"                            R^I = {rI_without:.8f}")
        print(f"                            R^V = {rV_without:.8e}")
        print(f"                            Time: {time.time()-t0:.1f}s")

        # Relative difference
        abs_gammaV_with = abs(gammaV_with)
        abs_gammaV_without = abs(gammaV_without)
        rel_diff = abs(abs_gammaV_with - abs_gammaV_without) / max(abs_gammaV_without, 1e-50)
        print(f"    Relative difference in |Gamma^V|: {rel_diff:.2e} ({rel_diff*100:.4e}%)")

        results.append({
            'f': f,
            'gammaV_with': gammaV_with,
            'gammaV_without': gammaV_without,
            'rV_with': rV_with,
            'rV_without': rV_without,
            'rel_diff': rel_diff,
            'norm': norm,
        })

    # ━━━ Summary Table ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print(f"\n{'=' * 70}")
    print("  SUMMARY TABLE (for direct paper insertion)")
    print(f"{'=' * 70}")

    print(f"\n  {'f (Hz)':<10s}  {'Gamma^V (含空间相位)':>22s}  {'Gamma^V (不含空间相位)':>22s}")
    print("  " + "-" * 60)

    for r in results:
        gV_with_str = format_latex_sci(r['gammaV_with'])
        gV_without_str = format_latex_sci(r['gammaV_without'])
        print(f"  {r['f']:<10}  {gV_with_str:>22s}  {gV_without_str:>22s}")

    # ━── LaTeX Table ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print(f"\n  === LaTeX Table Code ===")
    print("  \\begin{table}[h]")
    print("  \\centering")
    print("  \\begin{tabular}{ccc}")
    print("    \\hline")
    print("    频率 (Hz) & $\\Gamma^V$ (含空间相位) & $\\Gamma^V$ (不含空间相位) \\\\")
    print("    \\hline")
    for r in results:
        gV_with = format_latex_sci(r['gammaV_with'])
        gV_without = format_latex_sci(r['gammaV_without'])
        print(f"    {r['f']} & {gV_with} & {gV_without} \\\\")
    print("    \\hline")
    print("  \\end{tabular}")
    print("  \\caption{LISA ($i=\\pi/6$) $\\times$ Taiji 手征 ORF $\\Gamma^V$}")
    print("  \\end{table}")

    # ━━━ R^V Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print(f"\n{'=' * 70}")
    print("  NORMALIZED R^V SUMMARY")
    print(f"{'=' * 70}")

    print(f"\n  {'f (Hz)':<10s}  {'R^V (含空间相位)':>22s}  {'R^V (不含空间相位)':>22s}")
    print("  " + "-" * 60)

    for r in results:
        rv_with_str = format_latex_sci(r['rV_with'])
        rv_without_str = format_latex_sci(r['rV_without'])
        print(f"  {r['f']:<10}  {rv_with_str:>22s}  {rv_without_str:>22s}")

    # ━━━ Inclination scan ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print(f"\n{'=' * 70}")
    print("  INCLINATION SCAN: Gamma^V vs LISA inclination (for f = 0.01 Hz)")
    print(f"{'=' * 70}")

    inclinations = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90]
    print(f"\n  {'LISA inc (deg)':<14s}  {'Gamma^I':>14s}  {'Gamma^V':>14s}  "
          f"{'R^V':>16s}")
    print("  " + "-" * 64)

    for inc in inclinations:
        posA_inc = build_constellation(L1, float(inc), rotation_deg=0.0)
        gammaI, gammaV, SA, SB = compute_cross_e_variable_orf(
            0.01, posA_inc, L1, posB, L2,
            include_spatial_phase=False, delta_x=None,
            ntheta=64, nphi=128)
        norm = np.sqrt(SA * SB) if SA * SB > 0 else 1.0
        rV = gammaV / norm
        print(f"  {inc:<14d}  {gammaI:14.6e}  {gammaV:14.6e}  {rV:16.8e}")

    print(f"\n{'=' * 70}")
    print(f"  v17 target: Gamma^V ~ -7.75e-3 (for inclination = pi/6 = 30 deg)")
    print(f"{'=' * 70}")

    print(f"\n{'=' * 70}")
    print("  COMPUTATION COMPLETE")
    print(f"{'=' * 70}")

    return results


if __name__ == '__main__':
    results = main()
