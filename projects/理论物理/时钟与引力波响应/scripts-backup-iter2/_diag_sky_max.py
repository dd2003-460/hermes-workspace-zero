"""
Sky-maximized chiral ORF and transfer function convention check.
"""
import numpy as np

c = 299792458.0

def link_response_plus_cross(u_dir, th, ph):
    th_dot_u = th[0]*u_dir[0] + th[1]*u_dir[1] + th[2]*u_dir[2]
    ph_dot_u = ph[0]*u_dir[0] + ph[1]*u_dir[1] + ph[2]*u_dir[2]
    return th_dot_u**2 - ph_dot_u**2, 2.0*th_dot_u*ph_dot_u


def build_triangle_positions(L, inclination, rotation_phi=0):
    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([L, 0.0, 0.0])
    r3 = np.array([L/2, L*np.sqrt(3)/2, 0.0])
    positions = np.array([r1, r2, r3])
    cos_i = np.cos(inclination)
    sin_i = np.sin(inclination)
    rotated = np.zeros_like(positions)
    rotated[:, 0] = positions[:, 0]
    rotated[:, 1] = positions[:, 1] * cos_i - positions[:, 2] * sin_i
    rotated[:, 2] = positions[:, 1] * sin_i + positions[:, 2] * cos_i
    positions = rotated
    if rotation_phi != 0:
        cos_p = np.cos(rotation_phi)
        sin_p = np.sin(rotation_phi)
        new_pos = np.zeros_like(positions)
        new_pos[:, 0] = positions[:, 0] * cos_p - positions[:, 1] * sin_p
        new_pos[:, 1] = positions[:, 0] * sin_p + positions[:, 1] * cos_p
        new_pos[:, 2] = positions[:, 2]
        positions = new_pos
    return positions


def get_e_responses(TG, PG, positions):
    """Get E-variable responses for a constellation at given sky grid."""
    nx = np.sin(TG)*np.cos(PG)
    ny = np.sin(TG)*np.sin(PG)
    nz = np.cos(TG)
    th = np.array([np.cos(TG)*np.cos(PG), np.cos(TG)*np.sin(PG), -np.sin(TG)])
    ph = np.array([-np.sin(PG), np.cos(PG), np.zeros_like(PG)])
    cw_links = [(0,1), (1,2), (2,0)]
    D_plus = np.zeros_like(TG, dtype=np.complex128)
    D_cross = np.zeros_like(TG, dtype=np.complex128)
    for i, j in cw_links:
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)
        Fp, Fx = link_response_plus_cross(u, th, ph)
        D_plus += Fp
        D_cross += Fx
    return np.real(D_plus), np.real(D_cross)


def get_e_responses_with_tf(TG, PG, positions, f, L):
    """Get E-variable responses with link-specific TF."""
    nx = np.sin(TG)*np.cos(PG)
    ny = np.sin(TG)*np.sin(PG)
    nz = np.cos(TG)
    th = np.array([np.cos(TG)*np.cos(PG), np.cos(TG)*np.sin(PG), -np.sin(TG)])
    ph = np.array([-np.sin(PG), np.cos(PG), np.zeros_like(PG)])
    cw_links = [(0,1), (1,2), (2,0)]
    D_plus = np.zeros_like(TG, dtype=np.complex128)
    D_cross = np.zeros_like(TG, dtype=np.complex128)
    for i, j in cw_links:
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)
        Fp, Fx = link_response_plus_cross(u, th, ph)
        cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
        beta_link = np.pi * np.abs(f) * L / c
        sinc_val = np.where(np.abs(beta_link) < 1e-15, 1.0, np.sin(beta_link) / beta_link)
        phase = np.exp(-1j * beta_link)
        T = sinc_val * phase
        D_plus += Fp * T
        D_cross += Fx * T
    return D_plus, D_cross


L = 2.5e9
ntheta, nphi = 128, 256
tG = np.linspace(0, np.pi, ntheta)
pG = np.linspace(0, 2*np.pi, nphi)
TG, PG = np.meshgrid(tG, pG, indexing='ij')
dOmega = np.pi / (ntheta - 1) * 2 * np.pi / nphi

taiji0_pos = build_triangle_positions(L, 0.0)
lisa60_pos = build_triangle_positions(L, np.radians(60.0))

# ============ PURE GEOMETRIC (no TF) ============
print("=" * 70)
print("PURE GEOMETRIC ORF (no link transfer function)")
print("=" * 70)

R1p, R1x = get_e_responses(TG, PG, lisa60_pos)
R2p, R2x = get_e_responses(TG, PG, taiji0_pos)

gI = np.sum(R1p * R2p + R1x * R2x) * dOmega / (4 * np.pi)
gV = np.sum(R1p * R2x - R1x * R2p) * dOmega / (4 * np.pi)
auto1 = np.sum(R1p**2 + R1x**2) * dOmega / (4 * np.pi)
auto2 = np.sum(R2p**2 + R2x**2) * dOmega / (4 * np.pi)

print(f"LISA(60) x Taiji(0): Gamma^I={gI:+.8f}, Gamma^V={gV:+.8e}")
print(f"  Auto1={auto1:.6e}, Auto2={auto2:.6e}")
print(f"  Normalized Gamma^V = {gV/np.sqrt(auto1*auto2):+.8e}")

# Sky distribution of chiral integrand
sky_chiral = R1p * R2x - R1x * R2p
sky_chiral_norm = sky_chiral / np.sqrt(auto1 * auto2)
print(f"  Sky-max chiral = {np.max(sky_chiral_norm):.8f}")
print(f"  Sky-min chiral = {np.min(sky_chiral_norm):.8f}")
print(f"  Sky-max |chiral| = {np.max(np.abs(sky_chiral_norm)):.8f}")

# Same constellation
R1p_s, R1x_s = get_e_responses(TG, PG, lisa60_pos)
gI_s = np.sum(R1p_s**2 + R1x_s**2) * dOmega / (4 * np.pi)
print(f"\nLISA(60) x LISA(60): Gamma^I={gI_s:+.8f}, (should equal auto1)")

# ============ WITH LINK TF (f=0.01 Hz) ============
print("\n" + "=" * 70)
print("WITH LINK TF (f=0.01 Hz)")
print("=" * 70)

R1p_tf, R1x_tf = get_e_responses_with_tf(TG, PG, lisa60_pos, 0.01, L)
R2p_tf, R2x_tf = get_e_responses_with_tf(TG, PG, taiji0_pos, 0.01, L)

gI_tf = np.real(np.sum(np.conj(R1p_tf) * R2p_tf + np.conj(R1x_tf) * R2x_tf)) * dOmega / (4 * np.pi)
gV_tf = np.real(np.sum(np.conj(R1p_tf) * R2x_tf - np.conj(R1x_tf) * R2p_tf)) * dOmega / (4 * np.pi)
auto1_tf = np.real(np.sum(np.conj(R1p_tf)*R1p_tf + np.conj(R1x_tf)*R1x_tf)) * dOmega / (4*np.pi)
auto2_tf = np.real(np.sum(np.conj(R2p_tf)*R2p_tf + np.conj(R2x_tf)*R2x_tf)) * dOmega / (4*np.pi)

print(f"LISA(60) x Taiji(0): Gamma^I={gI_tf:+.8f}, Gamma^V={gV_tf:+.8e}")
print(f"  Auto1={auto1_tf:.6e}, Auto2={auto2_tf:.6e}")
print(f"  Normalized Gamma^V = {gV_tf/np.sqrt(auto1_tf*auto2_tf):+.8e}")

# Compare geometric vs TF
print(f"\n  Geometric norm_V: {gV/np.sqrt(auto1*auto2):.8e}")
print(f"  TF norm_V (f=0.01): {gV_tf/np.sqrt(auto1_tf*auto2_tf):.8e}")
print(f"  Ratio: {gV_tf/np.sqrt(auto1_tf*auto2_tf) / (gV/np.sqrt(auto1*auto2)):.6f}")

# ============ FREQUENCY DEPENDENCE (WITH LINK TF) ============
print("\n" + "=" * 70)
print("FREQUENCY SCAN (WITH LINK TF - different TF per detector)")
print("=" * 70)

print(f"  {'f(Hz)':>8s}  {'gamma_I':>12s}  {'gamma_V':>12s}  {'norm_V':>12s}")
for f in [0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]:
    R1p_tf, R1x_tf = get_e_responses_with_tf(TG, PG, lisa60_pos, f, L)
    R2p_tf, R2x_tf = get_e_responses_with_tf(TG, PG, taiji0_pos, f, L)
    gI_f = np.real(np.sum(np.conj(R1p_tf) * R2p_tf + np.conj(R1x_tf) * R2x_tf)) * dOmega / (4 * np.pi)
    gV_f = np.real(np.sum(np.conj(R1p_tf) * R2x_tf - np.conj(R1x_tf) * R2p_tf)) * dOmega / (4 * np.pi)
    a1_f = np.real(np.sum(np.conj(R1p_tf)*R1p_tf + np.conj(R1x_tf)*R1x_tf)) * dOmega / (4*np.pi)
    a2_f = np.real(np.sum(np.conj(R2p_tf)*R2p_tf + np.conj(R2x_tf)*R2x_tf)) * dOmega / (4*np.pi)
    print(f"  {f:8.3f}  {gI_f:+12.8f}  {gV_f:+12.8e}  {gV_f/np.sqrt(a1_f*a2_f):+12.8e}")

# ============ COMPARISON: WITH vs WITHOUT link TF in Orlando's E ============
print("\n" + "=" * 70)
print("What Orlando likely uses:")
print("  E(f) = (1-e^{-i*2beta}) * sum_k d_k(link_k)  where d_k has NO link TF")
print("  The link TF is already absorbed in the (1-P) delay operator")
print("=" * 70)

# The (1-e^{-i*2beta}) factor is COMMON to both detectors and cancels.
# So Orlando's Gamma^V should equal the PURE GEOMETRIC result.
#
# Our geometric result: |norm_V| = 8.3e-3
# Orlando's |Gamma^V|_max ~ 0.3
#
# The discrepancy is factor ~36.
#
# POSSIBLE EXPLANATIONS:
# (a) Orlando's |Gamma^V|_max is sky-maximized (not sky-averaged)
# (b) Orlando uses a different normalization
# (c) Orlando's E variable is different from what we think

print("\n  Our sky-averaged |norm_V| (geometric) = 8.3e-3")
print(f"  Our sky-max |chiral| (geometric) = {np.max(np.abs(sky_chiral_norm)):.8f}")

ratio = np.max(np.abs(sky_chiral_norm)) / np.abs(gV/np.sqrt(auto1*auto2))
print(f"  Sky-max / Sky-avg ratio = {ratio:.1f}")
print(f"\n  If Orlando's |Gamma^V|_max ~ 0.3:")
print(f"    We need sky-max ~ 0.3 (explanation a, OR)")
print(f"    We need a different convention that gives 36x larger values")

# ============ KEY CHECK: Orlando's definition ============
print("\n" + "=" * 70)
print("CHECK: What is the STANDARD definition of Gamma^V?")
print("=" * 70)
print("""
Standard cross-correlation ORF (Allen & Romano 1987):

The expected correlation of detector outputs:
  <d1(f) * d2*(f)> = (3*H0^2 / 10pi) * gamma_V(f) / (2pi*f)^3 * S_p^2(f)

where gamma_V is the chiral ORF:
  gamma_V = integral dOmega sum_A R_A1 * R_B2 * F_A^*(sky, det1) * F_B(sky, det2)

For chiral: gamma_V = integral dOmega/(4pi) * [R_+1*R_x2 - R_x1*R_+2]

The normalization is: max(|gamma_I|) <= 1 for a single detector.
""")

print("  Our normalized Gamma^V should be in [-1, 1].")
print(f"  We get: {gV/np.sqrt(auto1*auto2):.8e}")
print("  This is well within [-1,1] but much smaller than 0.3.")

# ============ THE REAL QUESTION: does Orlando use Michelson instead of E? ============
print("\n" + "=" * 70)
print("HYPOTHESIS: Orlando's |Gamma^V|_max ~ 0.3 might be for A/E variables")
print("with a SPECIFIC sky position, not sky-averaged.")
print("=" * 70)

# Let's find the sky position that maximizes |chiral integrand|
max_idx_flat = np.argmax(np.abs(sky_chiral))
max_i, max_j = max_idx_flat // nphi, max_idx_flat % nphi
max_theta = tG[max_i]
max_phi = pG[max_j]
print(f"\n  Sky position of max |chiral integrand|:")
print(f"    theta = {np.degrees(max_theta):.1f} deg, phi = {np.degrees(max_phi):.1f} deg")
print(f"    |chiral integrand| = {np.max(np.abs(sky_chiral)):.8f}")

# The normalized integrand at this sky position
sky_chiral_norm_local = sky_chiral / np.sqrt(auto1 * auto2)
print(f"    normalized = {sky_chiral_norm_local[max_i, max_j]:.8f}")

# Is this close to 0.3?
print(f"\n  Our sky-max |norm_V| = {np.max(np.abs(sky_chiral_norm)):.8f}")
print(f"  Orlando's |Gamma^V|_max ~ 0.3")
print(f"  DISCREPANCY: {0.3 / np.max(np.abs(sky_chiral_norm)):.1f}x")
