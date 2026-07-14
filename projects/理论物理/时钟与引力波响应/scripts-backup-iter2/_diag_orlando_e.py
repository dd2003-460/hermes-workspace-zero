"""
Test: what does Orlando actually compute for Gamma^V?

Orlando 2021 (arXiv:2011.07059) uses TDI A/E/M variables.
The E variable is NOT a simple circulant sum. It's defined as:

E(t) = (1-P21) * d12 + (1-P32) * d23 + (1-P13) * d31

where Pij are delay operators (Pij * x(t) = x(t - L_ij/c)) and dij are one-way time delays.

In the frequency domain:
E(f) = (1 - e^{-2pi f L_21/c}) * d12 + (1 - e^{-2pi f L_32/c}) * d23 + (1 - e^{-2pi f L_13/c}) * d31

For an equilateral triangle: L_12 = L_23 = L_31 = L (all one-way links same length)
So: E(f) = (1 - e^{-i beta}) * [d12 + d23 + d31] where beta = 2pi f L/c

Wait, but P21 delays by L_21 = L (one-way light travel time), and the delay is e^{-i 2pi f L/c}.

Actually, TDI notation: P_i delays by the light travel time from satellite i.
For equilateral triangle, all one-way light travel times are equal = L/c.

So: E(f) = (1 - e^{-i * 2pi f L/c}) * (d12 + d23 + d31)

The factor (1 - e^{-i beta}) multiplies the sum. For small beta: (1 - e^{-i beta}) ~ i*beta

The chiral response comes from the one-way time delays d_ij which have different
antenna patterns for different links.

The KEY difference from my circulant: E sums CW links only (not CW - CCW).
The E variable is NOT circulant.

Let me compute the E variable as Orlando defines it:
E ~ (1 - e^{-i beta_ij}) * d_ij summed over the three links.

The chiral ORF comes from the INTERFERENCE between different links with
different transfer functions.
"""
import numpy as np

c = 299792458.0

def link_response_plus_cross(u_dir, th, ph):
    """Antenna response for a single interferometer arm along u_dir."""
    th_dot_u = th[0]*u_dir[0] + th[1]*u_dir[1] + th[2]*u_dir[2]
    ph_dot_u = ph[0]*u_dir[0] + ph[1]*u_dir[1] + ph[2]*u_dir[2]
    return th_dot_u**2 - ph_dot_u**2, 2.0*th_dot_u*ph_dot_u


def build_triangle_positions(L, inclination, rotation_phi=0):
    """Build equilateral triangle positions with inclination and rotation."""
    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([L, 0.0, 0.0])
    r3 = np.array([L/2, L*np.sqrt(3)/2, 0.0])
    positions = np.array([r1, r2, r3])

    # Apply inclination (x-axis rotation)
    cos_i = np.cos(inclination)
    sin_i = np.sin(inclination)
    rotated = np.zeros_like(positions)
    rotated[:, 0] = positions[:, 0]
    rotated[:, 1] = positions[:, 1] * cos_i - positions[:, 2] * sin_i
    rotated[:, 2] = positions[:, 1] * sin_i + positions[:, 2] * cos_i
    positions = rotated

    # Apply z-rotation
    if rotation_phi != 0:
        cos_p = np.cos(rotation_phi)
        sin_p = np.sin(rotation_phi)
        new_pos = np.zeros_like(positions)
        new_pos[:, 0] = positions[:, 0] * cos_p - positions[:, 1] * sin_p
        new_pos[:, 1] = positions[:, 0] * sin_p + positions[:, 1] * cos_p
        new_pos[:, 2] = positions[:, 2]
        positions = new_pos

    return positions


def orlando_e_variable_response(f, const_positions, arm_length, ntheta, nphi):
    """
    Orlando-style E-variable response.

    E(f) = sum_k (1 - e^{-i * 2pi f L_k/c}) * d_k

    where d_k is the one-way time delay along link k.

    For equilateral triangle: all L_k = L (one-way).
    E(f) = (1 - e^{-i beta}) * sum_k d_k where beta = 2pi f L/c

    But each d_k has different antenna pattern:
    d_k = h_+ * F_+(link_k) + h_x * F_x(link_k)

    The (1 - e^{-i beta}) factor is common to all links for equilateral triangles.
    So: E ~ (1 - e^{-i beta}) * (d12 + d23 + d31)

    The chiral response from summing CW links (not CW - CCW):
    The sum d12 + d23 + d31 has BOTH + and x sensitivity because each link
    sees different GW polarization depending on its orientation.
    """
    tG = np.linspace(0, np.pi, ntheta)
    pG = np.linspace(0, 2*np.pi, nphi)
    TG, PG = np.meshgrid(tG, pG, indexing='ij')

    positions = const_positions
    L = arm_length

    # GW direction and polarization basis
    nx = np.sin(TG)*np.cos(PG)
    ny = np.sin(TG)*np.sin(PG)
    nz = np.cos(TG)

    th = np.array([np.cos(TG)*np.cos(PG),
                   np.cos(TG)*np.sin(PG),
                   -np.sin(TG)])
    ph = np.array([-np.sin(PG), np.cos(PG), np.zeros_like(PG)])

    beta = 2.0 * np.pi * np.abs(f) * L / c

    # Sum of one-way time delays along CW links
    # d_k = h_+ * F_+(link_k) + h_x * F_x(link_k)
    # We factor out h_+ and h_x to get antenna patterns:
    # D_+ = sum_k F_+(link_k) * T_k
    # D_x = sum_k F_x(link_k) * T_k
    # where T_k is the link transfer function

    # Links: 1->2, 2->3, 3->1 (clockwise)
    cw_links = [(0,1), (1,2), (2,0)]

    D_plus = np.zeros_like(TG, dtype=np.complex128)
    D_cross = np.zeros_like(TG, dtype=np.complex128)

    for i, j in cw_links:
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)

        Fp, Fx = link_response_plus_cross(u, th, ph)

        # Link-specific transfer function
        cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
        beta_link = np.pi * np.abs(f) * L / c  # beta for one-way
        sinc_val = np.where(np.abs(beta_link) < 1e-15, 1.0, np.sin(beta_link) / beta_link)
        phase = np.exp(-1j * beta_link)
        T = sinc_val * phase  # one-way link TF

        D_plus += Fp * T
        D_cross += Fx * T

    # The E variable response includes the (1 - e^{-i*2beta}) factor
    # But this is a common factor that cancels in the normalized ORF
    # So we can just use D_plus and D_cross

    # Actually, we need to be more careful. The E variable has a frequency-dependent
    # prefactor, but for cross-correlation between SAME type detectors,
    # the prefactor cancels in normalization.

    return D_plus, D_cross


def compute_cross_orf_new(f, pos1, L1, pos2, L2, ntheta=64, nphi=128):
    """Compute cross-correlation using the new E-variable response."""
    D1p, D1x = orlando_e_variable_response(f, pos1, L1, ntheta, nphi)
    D2p, D2x = orlando_e_variable_response(f, pos2, L2, ntheta, nphi)

    dOmega = np.pi / (ntheta - 1) * 2 * np.pi / nphi

    gamma_I = np.real(np.sum(np.conj(D1p) * D2p + np.conj(D1x) * D2x)) * dOmega / (4 * np.pi)
    gamma_V = np.real(np.sum(np.conj(D1p) * D2x - np.conj(D1x) * D2p)) * dOmega / (4 * np.pi)

    auto1 = np.real(np.sum(np.conj(D1p)*D1p + np.conj(D1x)*D1x)) * dOmega / (4*np.pi)
    auto2 = np.real(np.sum(np.conj(D2p)*D2p + np.conj(D2x)*D2x)) * dOmega / (4*np.pi)

    return gamma_I, gamma_V, auto1, auto2


print("=" * 70)
print("ORLANDO E-VARIABLE: CW link sum (NOT CW - CCW)")
print("=" * 70)

L = 2.5e9
taiji0_pos = build_triangle_positions(L, 0.0)
lisa60_pos = build_triangle_positions(L, np.radians(60.0))
taiji60_pos = build_triangle_positions(L, np.radians(60.0))

# Same constellation - should have Gamma^V ~ 0
print("\nTaiji(0) x Taiji(0) - self-correlation:")
gI, gV, a1, a2 = compute_cross_orf_new(0.1, taiji0_pos, L, taiji0_pos, L, ntheta=48, nphi=96)
print(f"  Gamma^I = {gI:+.8f}, Gamma^V = {gV:+.8e}")
print(f"  (should be ~0 for self-correlation of same constellation)")

print("\nLISA(60) x LISA(60) - self-correlation:")
gI, gV, a1, a2 = compute_cross_orf_new(0.1, lisa60_pos, L, lisa60_pos, L, ntheta=48, nphi=96)
print(f"  Gamma^I = {gI:+.8f}, Gamma^V = {gV:+.8e}")

# Cross correlation
print("\nLISA(60) x Taiji(0):")
gI, gV, a1, a2 = compute_cross_orf_new(0.1, lisa60_pos, L, taiji0_pos, L, ntheta=48, nphi=96)
norm = np.sqrt(a1 * a2)
print(f"  Gamma^I = {gI:+.8f}, Gamma^V = {gV:+.8e}, norm_V = {gV/norm:+.8e}")

print("\nLISA(60) x Taiji(60):")
gI, gV, a1, a2 = compute_cross_orf_new(0.1, lisa60_pos, L, taiji60_pos, L, ntheta=48, nphi=96)
norm = np.sqrt(a1 * a2)
print(f"  Gamma^I = {gI:+.8f}, Gamma^V = {gV:+.8e}, norm_V = {gV/norm:+.8e}")

# Frequency scan
print("\n" + "=" * 70)
print("FREQUENCY SCAN: LISA(60) x Taiji(0)")
print("=" * 70)

print(f"  {'f(Hz)':>8s}  {'fL/c':>8s}  {'Gamma^I':>12s}  {'Gamma^V':>12s}  {'norm_V':>12s}")
for f in [0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]:
    gI, gV, a1, a2 = compute_cross_orf_new(f, lisa60_pos, L, taiji0_pos, L, ntheta=48, nphi=96)
    norm = np.sqrt(a1 * a2)
    fLc = np.pi * f * L / c
    print(f"  {f:8.3f}  {fLc:8.4f}  {gI:+12.8f}  {gV:+12.8e}  {gV/norm:+12.8e}")

# Inclination scan
print("\n" + "=" * 70)
print("INCLINATION SCAN: LISA(60) x Taiji(i)")
print("=" * 70)

print(f"  {'inc_deg':>8s}  {'Gamma^I':>12s}  {'Gamma^V':>12s}  {'norm_V':>12s}")
for inc_deg in [0, 15, 30, 45, 60, 75, 90]:
    pos = build_triangle_positions(L, np.radians(inc_deg))
    gI, gV, a1, a2 = compute_cross_orf_new(0.01, lisa60_pos, L, pos, L, ntheta=48, nphi=96)
    norm = np.sqrt(a1 * a2)
    print(f"  {inc_deg:8d}  {gI:+12.8f}  {gV:+12.8e}  {gV/norm:+12.8e}")

print("\n" + "=" * 70)
print("COMPARISON: CW sum vs CW-CCW difference")
print("=" * 70)

# CW sum (current approach)
def orlando_e_variable_cw_ccw(f, const_positions, arm_length, ntheta, nphi):
    """E variable as CW sum minus CCW sum."""
    tG = np.linspace(0, np.pi, ntheta)
    pG = np.linspace(0, 2*np.pi, nphi)
    TG, PG = np.meshgrid(tG, pG, indexing='ij')

    positions = const_positions
    L = arm_length

    nx = np.sin(TG)*np.cos(PG)
    ny = np.sin(TG)*np.sin(PG)
    nz = np.cos(TG)

    th = np.array([np.cos(TG)*np.cos(PG), np.cos(TG)*np.sin(PG), -np.sin(TG)])
    ph = np.array([-np.sin(PG), np.cos(PG), np.zeros_like(PG)])

    cw_links = [(0,1), (1,2), (2,0)]
    ccw_links = [(1,0), (2,1), (0,2)]

    R_cw_plus = np.zeros_like(TG, dtype=np.complex128)
    R_cw_cross = np.zeros_like(TG, dtype=np.complex128)
    R_ccw_plus = np.zeros_like(TG, dtype=np.complex128)
    R_ccw_cross = np.zeros_like(TG, dtype=np.complex128)

    for i, j in cw_links + ccw_links:
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)
        Fp, Fx = link_response_plus_cross(u, th, ph)
        cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
        beta_link = np.pi * np.abs(f) * L / c
        sinc_val = np.where(np.abs(beta_link) < 1e-15, 1.0, np.sin(beta_link) / beta_link)
        phase = np.exp(-1j * beta_link)
        T = sinc_val * phase

        if (i,j) in cw_links:
            R_cw_plus += Fp * T
            R_cw_cross += Fx * T
        else:
            R_ccw_plus += Fp * T
            R_ccw_cross += Fx * T

    R_plus = (R_cw_plus - R_ccw_plus)  # CW - CCW
    R_cross = (R_cw_cross - R_ccw_cross)

    return R_plus, R_cross


# Check if CW sum gives nonzero while CW-CCW gives zero
for f in [0.1, 1.0]:
    Dp, Dx = orlando_e_variable_response(f, lisa60_pos, L, 32, 64)
    Rp, Rx = orlando_e_variable_cw_ccw(f, lisa60_pos, L, 32, 64)

    # Check magnitude difference
    print(f"\n  f={f} Hz:")
    print(f"    CW sum:  |D_+|_rms={np.sqrt(np.mean(np.abs(Dp)**2)):.6f}, |D_x|_rms={np.sqrt(np.mean(np.abs(Dx)**2)):.6f}")
    print(f"    CW-CCW: |R_+|_rms={np.sqrt(np.mean(np.abs(Rp)**2)):.10f}, |R_x|_rms={np.sqrt(np.mean(np.abs(Rx)**2)):.10f}")
