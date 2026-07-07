"""
Diagnostic: re-derive chiral ORF using proper frequency-dependent link transfer functions.

The key insight: Orlando's E-variable chiral response relies on frequency-dependent
TDI delay operators. In the long-wavelength limit (fL/c -> 0), the E-variable
response vanishes because clockwise and counter-clockwise link responses are
identical for equilateral triangles.

The chiral signal scales as (fL/c)^2 for fL/c << 1.

This diagnostic computes:
1. Sky-maximized Gamma^V (finding the worst-case sky position)
2. Proper frequency-dependent link transfer functions
3. The scaling of Gamma^V with fL/c
"""
import numpy as np

c = 299792458.0

def link_response_plus_cross(u_dir, th, ph):
    """Antenna response for a single interferometer arm along u_dir.

    F_+ = (th.u)^2 - (ph.u)^2
    F_x = 2*(th.u)*(ph.u)
    """
    th_dot_u = th[0]*u_dir[0] + th[1]*u_dir[1] + th[2]*u_dir[2]
    ph_dot_u = ph[0]*u_dir[0] + ph[1]*u_dir[1] + ph[2]*u_dir[2]
    return th_dot_u**2 - ph_dot_u**2, 2.0*th_dot_u*ph_dot_u


def complex_transfer(f, L, cos_nu):
    """Interferometer transfer function with full frequency dependence.

    This is the one-way link transfer function in the frequency domain.
    For LISA/Taiji: T = sinc(beta) * exp(-i*beta) where beta = pi*f*L/c
    """
    beta = np.pi * np.abs(f) * L / c
    sinc_val = np.where(np.abs(beta) < 1e-15, 1.0, np.sin(beta) / beta)
    phase = np.exp(-1j * beta)
    return sinc_val * phase


def e_variable_complex_response(f, const_positions, arm_length, ntheta, nphi):
    """
    Compute E-variable response using frequency-dependent link transfer functions.

    The E variable for a triangle combines the six one-way measurements as:
    E ~ (d_cw - d_ccw) where d_cw is clockwise and d_ccw is counter-clockwise.

    With frequency-dependent transfer functions, each link has a different T
    based on its cos_nu, breaking the symmetry.

    For each GW direction (theta_gw, phi_gw):
    - Compute polarization basis (th, ph)
    - For each link i->j: compute F_+, F_x and T(f, L, cos_nu_ij)
    - E response = sum_cw (F * T) - sum_ccw (F * T)
    """
    tG = np.linspace(0, np.pi, ntheta)
    pG = np.linspace(0, 2*np.pi, nphi)
    TG, PG = np.meshgrid(tG, pG, indexing='ij')

    # GW direction and polarization basis
    nx = np.sin(TG)*np.cos(PG)
    ny = np.sin(TG)*np.sin(PG)
    nz = np.cos(TG)

    th = np.array([np.cos(TG)*np.cos(PG),
                   np.cos(TG)*np.sin(PG),
                   -np.sin(TG)])
    ph = np.array([-np.sin(PG), np.cos(PG), np.zeros_like(PG)])

    # Compute 6 link directions and transfer functions
    positions = const_positions
    arms_cw = [(0,1), (1,2), (2,0)]  # clockwise
    arms_ccw = [(1,0), (2,1), (0,2)]  # counter-clockwise

    # Clockwise sum
    R_cw_plus = np.zeros_like(TG, dtype=np.complex128)
    R_cw_cross = np.zeros_like(TG, dtype=np.complex128)
    for i, j in arms_cw:
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)
        # Antenna pattern
        Fp, Fx = link_response_plus_cross(u, th, ph)
        # Transfer function for this link
        cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
        T = complex_transfer(f, arm_length, cos_nu)
        R_cw_plus += Fp * T
        R_cw_cross += Fx * T

    # Counter-clockwise sum
    R_ccw_plus = np.zeros_like(TG, dtype=np.complex128)
    R_ccw_cross = np.zeros_like(TG, dtype=np.complex128)
    for i, j in arms_ccw:
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)
        Fp, Fx = link_response_plus_cross(u, th, ph)
        cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
        T = complex_transfer(f, arm_length, cos_nu)
        R_ccw_plus += Fp * T
        R_ccw_cross += Fx * T

    # E variable response (difference)
    R_E_plus = R_cw_plus - R_ccw_plus
    R_E_cross = R_cw_cross - R_ccw_cross

    return R_E_plus, R_E_cross


def compute_chiral_orf_link_based(f, const1_pos, const1_L, const2_pos, const2_L,
                                   ntheta=64, nphi=128):
    """Compute cross-correlation chiral ORF using link-based E-variable responses."""
    R1p, R1x = e_variable_complex_response(f, const1_pos, const1_L, ntheta, nphi)
    R2p, R2x = e_variable_complex_response(f, const2_pos, const2_L, ntheta, nphi)

    dOmega = np.pi / (ntheta - 1) * 2 * np.pi / nphi

    gamma_I = np.real(np.sum(np.conj(R1p) * R2p + np.conj(R1x) * R2x)) * dOmega / (4 * np.pi)
    gamma_V = np.real(np.sum(np.conj(R1p) * R2x - np.conj(R1x) * R2p)) * dOmega / (4 * np.pi)

    # Auto ORFs for normalization
    auto1 = np.real(np.sum(np.conj(R1p)*R1p + np.conj(R1x)*R1x)) * dOmega / (4*np.pi)
    auto2 = np.real(np.sum(np.conj(R2p)*R2p + np.conj(R2x)*R2x)) * dOmega / (4*np.pi)

    return gamma_I, gamma_V, auto1, auto2


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


print("=" * 70)
print("LINK-BASED E-VARIABLE: Frequency scan (with fL/c dependence)")
print("=" * 70)

L = 2.5e9
c = 299792458.0

# Build constellations
taiji0_pos = build_triangle_positions(L, 0.0)
lisa60_pos = build_triangle_positions(L, np.radians(60.0))

frequencies = [0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
print("\nLISA(60) x Taiji(0):")
print(f"  {'f(Hz)':>8s}  {'fL/c':>8s}  {'Gamma^I':>12s}  {'Gamma^V':>12s}  {'norm_V':>12s}")
for f in frequencies:
    fLc = np.pi * f * L / c
    gI, gV, a1, a2 = compute_chiral_orf_link_based(f, lisa60_pos, L, taiji0_pos, L, ntheta=48, nphi=96)
    norm = np.sqrt(a1 * a2)
    print(f"  {f:8.3f}  {fLc:8.4f}  {gI:+12.8f}  {gV:+12.8e}  {gV/norm:+12.8e}")

# Same constellation
print("\nLISA(60) x LISA(60):")
for f in [0.001, 0.1, 1.0]:
    gI, gV, a1, a2 = compute_chiral_orf_link_based(f, lisa60_pos, L, lisa60_pos, L, ntheta=48, nphi=96)
    print(f"  f={f}: Gamma^I={gI:+.8f}, Gamma^V={gV:+.8e} (should be ~0)")

# Taiji(0) x Taiji(0)
print("\nTaiji(0) x Taiji(0):")
for f in [0.001, 0.1, 1.0]:
    gI, gV, a1, a2 = compute_chiral_orf_link_based(f, taiji0_pos, L, taiji0_pos, L, ntheta=48, nphi=96)
    print(f"  f={f}: Gamma^I={gI:+.8f}, Gamma^V={gV:+.8e} (should be ~0)")

print("\n" + "=" * 70)
print("DETECTOR TENSOR vs LINK-BASED: comparison at f=0.1 Hz")
print("=" * 70)

# Link-based at f=0.1
gI_link, gV_link, a1, a2 = compute_chiral_orf_link_based(0.1, lisa60_pos, L, taiji0_pos, L, ntheta=48, nphi=96)
print(f"  Link-based: Gamma^I={gI_link:+.8f}, Gamma^V={gV_link:+.8e}")
print(f"  Auto1={a1:.6e}, Auto2={a2:.6e}")

# Check: long-wavelength limit (should approach 0 for link-based)
print("\n" + "=" * 70)
print("LONG-WAVELENGTH LIMIT: f -> 0")
print("=" * 70)

for f in [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]:
    gI, gV, a1, a2 = compute_chiral_orf_link_based(f, lisa60_pos, L, taiji0_pos, L, ntheta=32, nphi=64)
    norm = np.sqrt(a1 * a2)
    print(f"  f={f:.0e}: norm_V = {gV/norm:+.8e}, |T|~={np.sin(np.pi*f*L/c)/(np.pi*f*L/c):.6f}")

print("\n" + "=" * 70)
print("INCLINATION SCAN: norm_Gamma^V vs inclination difference")
print("=" * 70)

print("\nLISA(60) x Taiji(i):")
for inc_deg in [0, 15, 30, 45, 60, 75, 90]:
    taiji_inc = build_triangle_positions(L, np.radians(inc_deg))
    gI, gV, a1, a2 = compute_chiral_orf_link_based(0.01, lisa60_pos, L, taiji_inc, L, ntheta=48, nphi=96)
    norm = np.sqrt(a1 * a2)
    print(f"  Taiji(i={inc_deg}): norm_V = {gV/norm:+.8e}")
