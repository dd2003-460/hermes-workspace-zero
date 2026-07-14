#!/usr/bin/env python3
"""
Test: Does |cos_nu| vs cos_nu in the OLC transfer function matter for the final ORF?

Theory (Lou Eq. 2-30):
    T = (i*2*pi*f*L/c) * sinc[pi*f*L/c * (1 - u.n)] * exp(-i*pi*f*L/c * (1 - u.n))

The argument uses (1 - u.n) = (1 - cos_nu), NOT (1 - |cos_nu|).
The chiral ORF scripts use |cos_nu|, the standard ORF script uses cos_nu.

This script quantifies the difference and its impact on the final ORF.
"""
import numpy as np

c = 299792458.0

# --- LISA-like parameters ---
f_test = 0.01       # Hz
L_test = 2.5e9      # meters (2.5 Gm arm length)

beta = np.pi * f_test * L_test / c
print(f"LISA-like parameters: f={f_test} Hz, L={L_test/1e9:.1f} Gm")
print(f"  beta = pi*f*L/c = {beta:.6f}")
print()


# === 1. Transfer function comparison ===
def olc_abs(f, L, cos_nu):
    """Current chiral-ORF implementation: uses 1 - |cos_nu|"""
    beta_val = np.pi * abs(f) * L / c
    one_minus = 1.0 - abs(cos_nu)
    sinc_arg = beta_val * one_minus
    if abs(sinc_arg) < 1e-10:
        sinc_v = 1.0
    else:
        sinc_v = np.sin(sinc_arg) / sinc_arg
    phase = np.exp(-1j * beta_val * one_minus)
    prefac = 1j * 2.0 * np.pi * abs(f) * L / c
    return prefac * sinc_v * phase


def olc_linear(f, L, cos_nu):
    """Theoretical form: uses 1 - cos_nu (Lou Eq. 2-30)"""
    beta_val = np.pi * abs(f) * L / c
    one_minus = 1.0 - cos_nu
    sinc_arg = beta_val * one_minus
    if abs(sinc_arg) < 1e-10:
        sinc_v = 1.0
    else:
        sinc_v = np.sin(sinc_arg) / sinc_arg
    phase = np.exp(-1j * beta_val * one_minus)
    prefac = 1j * 2.0 * np.pi * abs(f) * L / c
    return prefac * sinc_v * phase


# Full array version for vectorized computation
def olc_abs_vec(f, L, cos_nu_arr):
    """Vectorized version using |cos_nu|"""
    beta_val = np.pi * abs(f) * L / c
    one_minus = 1.0 - np.abs(cos_nu_arr)
    sinc_arg = beta_val * one_minus
    eps = 1e-10
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta_val * one_minus)
    prefac = 1j * 2.0 * np.pi * abs(f) * L / c
    return prefac * sinc_v * phase


def olc_linear_vec(f, L, cos_nu_arr):
    """Vectorized version using cos_nu (Lou Eq. 2-30)"""
    beta_val = np.pi * abs(f) * L / c
    one_minus = 1.0 - cos_nu_arr
    sinc_arg = beta_val * one_minus
    eps = 1e-10
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta_val * one_minus)
    prefac = 1j * 2.0 * np.pi * abs(f) * L / c
    return prefac * sinc_v * phase


# === Point 1: Full sky range ===
cos_nu_range = np.linspace(-1.0, 1.0, 401)
T_abs = olc_abs_vec(f_test, L_test, cos_nu_range)
T_lin = olc_linear_vec(f_test, L_test, cos_nu_range)

mag_diff = np.abs(np.abs(T_abs) - np.abs(T_lin))
phase_abs = np.angle(T_abs)
phase_lin = np.angle(T_lin)
phase_diff = np.abs(phase_abs - phase_lin)

print("=" * 70)
print("1. TRANSFER FUNCTION COMPARISON (full cos_nu range)")
print("=" * 70)
print(f"  |T| max difference:     {np.max(mag_diff):.6e}")
print(f"  |T| mean difference:    {np.mean(mag_diff):.6e}")
print(f"  |T| mean relative:      {np.mean(mag_diff)/np.mean(np.abs(T_lin)):.6e}")
print(f"  |phase| max difference: {np.max(phase_diff):.6e} rad = {np.max(phase_diff)*180/np.pi:.4f} deg")
print(f"  |phase| mean difference: {np.mean(phase_diff):.6e} rad = {np.mean(phase_diff)*180/np.pi:.6f} deg")

negative_region = cos_nu_range < 0
print(f"\n  In region cos_nu < 0 ({np.sum(negative_region)} points):")
print(f"    |T| max diff:    {np.max(mag_diff[negative_region]):.6e}")
print(f"    |phase| max diff: {np.max(phase_diff[negative_region]):.6e} rad")

# === Point 2: Specific evaluation points ===
test_points = [-1.0, -0.8, -0.5, -0.2, 0.0, 0.2, 0.5, 0.8, 1.0]
print(f"\n{'=' * 70}")
print("2. DETAILED COMPARISON AT SPECIFIC cos_nu VALUES")
print("=" * 70)
header = f"  {'cos_nu':>8} | {'|T_abs|':>12} | {'|T_lin|':>12} | {'d|T|':>12} | " \
         f"{'arg_abs':>10} | {'arg_lin':>10} | {'darg':>10}"
print(header)
print("  " + "-" * 88)

for cn in test_points:
    ta = olc_abs(f_test, L_test, cn)
    tl = olc_linear(f_test, L_test, cn)
    print(f"  {cn:>8.1f} | {abs(ta):>12.8f} | {abs(tl):>12.8f} | {abs(abs(ta)-abs(tl)):>12.8e} | "
          f"{np.angle(ta):>10.6f} | {np.angle(tl):>10.6f} | {abs(np.angle(ta)-np.angle(tl)):>10.6e}")

# === Point 3: Sky-averaged transfer function ===
print(f"\n{'=' * 70}")
print("3. SKY-AVERAGED TRANSFER FUNCTION (LISA-like triangular config)")
print("=" * 70)

# Two arms in a triangular detector
u1 = np.array([1.0, 0.0, 0.0])
u2 = np.array([-0.5, np.sqrt(3)/2, 0.0])

ntheta, nphi = 180, 360
thetas = np.linspace(0, np.pi, ntheta)
phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
tG, pG = np.meshgrid(thetas, phis, indexing='ij')
dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)

nx = np.sin(tG)*np.cos(pG)
ny = np.sin(tG)*np.sin(pG)
nz = np.cos(tG)

cos_nu_1 = nx*u1[0] + ny*u1[1] + nz*u1[2]  # = nx
cos_nu_2 = nx*u2[0] + ny*u2[1] + nz*u2[2]  # = -0.5*nx + sqrt(3)/2*ny

T1u_abs = olc_abs_vec(f_test, L_test, cos_nu_1)
T1u_lin = olc_linear_vec(f_test, L_test, cos_nu_1)
T2u_abs = olc_abs_vec(f_test, L_test, cos_nu_2)
T2u_lin = olc_linear_vec(f_test, L_test, cos_nu_2)

# Sky-averaged product
avg_T_prod_abs = np.sum(T1u_abs * T2u_abs * dO) / (4*np.pi)
avg_T_prod_lin = np.sum(T1u_lin * T2u_lin * dO) / (4*np.pi)
avg_T2_abs = np.sum(np.abs(T1u_abs)**2 * np.abs(T2u_abs)**2 * dO) / (4*np.pi)
avg_T2_lin = np.sum(np.abs(T1u_lin)**2 * np.abs(T2u_lin)**2 * dO) / (4*np.pi)

print(f"  Sky-averaged <T1*T2> (|cos_nu|):   {avg_T_prod_abs:.8e}")
print(f"  Sky-averaged <T1*T2> (cos_nu):     {avg_T_prod_lin:.8e}")
print(f"  |diff| in <T1*T2>:                 {abs(avg_T_prod_abs - avg_T_prod_lin):.8e}")
print(f"  Sky-averaged <|T1|^2*|T2|^2> (|cos_nu|): {avg_T2_abs:.8e}")
print(f"  Sky-averaged <|T1|^2*|T2|^2> (cos_nu):  {avg_T2_lin:.8e}")
print(f"  Rel diff in <|T|^4>:               {(avg_T2_abs - avg_T2_lin)/avg_T2_lin:.6e}")

# === Point 4: Full two-detector chiral ORF ===
def antenna_FpFx(n_theta, n_phi, arm_theta, arm_phi):
    """F_+ and F_x for a single interferometer arm."""
    ct, st = np.cos(n_theta), np.sin(n_theta)
    cp, sp = np.cos(n_phi), np.sin(n_phi)
    ux = np.sin(arm_theta)*np.cos(arm_phi)
    uy = np.sin(arm_theta)*np.sin(arm_phi)
    uz = np.cos(arm_theta)
    th_x, th_y, th_z = ct*cp, ct*sp, -st
    ph_x, ph_y, ph_z = -sp, cp, 0.0
    Fp = (th_x*ux)**2 + (th_y*uy)**2 + (th_z*uz)**2 - (ph_x*ux)**2 - (ph_y*uy)**2 - (ph_z*uz)**2
    Fx = 2.0*(th_x*ux)*(ph_x*ux) + 2.0*(th_y*uy)*(ph_y*uy) + 2.0*(th_z*uz)*(ph_z*uz)
    return Fp, Fx


def compute_chiral_orf(f, L, det1_u, det1_v, det2_u, det2_v,
                       theta_s, phi_s, d, use_abs=True, ntheta=180, nphi=360):
    """Compute chiral ORF Gamma^V for two detectors."""
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')
    dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)

    nx = np.sin(tG)*np.cos(pG)
    ny = np.sin(tG)*np.sin(pG)
    nz = np.cos(tG)

    # Arm directions
    u1t, u1p = det1_u
    v1t, v1p = det1_v
    u2t, u2p = det2_u
    v2t, v2p = det2_v

    # cos_nu for all four arms
    def get_cos_nu(at, ap):
        ux = np.sin(at)*np.cos(ap)
        uy = np.sin(at)*np.sin(ap)
        uz = np.cos(at)
        return nx*ux + ny*uy + nz*uz

    cn1u = get_cos_nu(u1t, u1p)
    cn1v = get_cos_nu(v1t, v1p)
    cn2u = get_cos_nu(u2t, u2p)
    cn2v = get_cos_nu(v2t, v2p)

    if use_abs:
        T1u = olc_abs_vec(f, L, cn1u)
        T1v = olc_abs_vec(f, L, cn1v)
        T2u = olc_abs_vec(f, L, cn2u)
        T2v = olc_abs_vec(f, L, cn2v)
    else:
        T1u = olc_linear_vec(f, L, cn1u)
        T1v = olc_linear_vec(f, L, cn1v)
        T2u = olc_linear_vec(f, L, cn2u)
        T2v = olc_linear_vec(f, L, cn2v)

    Fp1, Fx1 = antenna_FpFx(tG, pG, u1t, u1p)
    Fp2, Fx2 = antenna_FpFx(tG, pG, u2t, u2p)

    # Chiral geometric factor
    chiral_geom = Fp1*Fx2 - Fx1*Fp2

    # TF coupling: product of T_u * T_v for each detector
    # For cross-correlation, detector 2 is complex conjugated
    tf_coupling = (T1u * T1v) * np.conj(T2u * T2v)

    # Baseline propagation phase
    s = np.array([np.sin(theta_s)*np.cos(phi_s),
                  np.sin(theta_s)*np.sin(phi_s),
                  np.cos(theta_s)])
    bl_phase = np.exp(-1j * 2.0*np.pi*abs(f)*d/c *
                      (nx*s[0] + ny*s[1] + nz*s[2]))

    integrand = chiral_geom * tf_coupling * bl_phase
    gamma_V = np.sum(integrand * dO) / (4*np.pi)

    auto1 = np.sum(np.abs(T1u)**2 * np.abs(T1v)**2 * dO) / (4*np.pi)
    auto2 = np.sum(np.abs(T2u)**2 * np.abs(T2v)**2 * dO) / (4*np.pi)

    return gamma_V, np.sqrt(auto1 * auto2)


print(f"\n{'=' * 70}")
print("4. TWO-DETECTOR CHIRAL ORF COMPARISON")
print("=" * 70)

# Test case A: Parallel coplanar configuration (should give ~0 chiral ORF by symmetry)
print("  Test A: Parallel coplanar detectors (symmetric)")
d_test = 1.0e9
theta_s = np.pi/4; phi_s = np.pi/4

det1_u = (np.pi/2, 0.0)
det1_v = (np.pi/2, 2*np.pi/3)
det2_u = (np.pi/2, 0.0)
det2_v = (np.pi/2, 2*np.pi/3)

ga_a, na_a = compute_chiral_orf(f_test, L_test, det1_u, det1_v, det2_u, det2_v,
                                 theta_s, phi_s, d_test, use_abs=True)
gl_a, nl_a = compute_chiral_orf(f_test, L_test, det1_u, det1_v, det2_u, det2_v,
                                 theta_s, phi_s, d_test, use_abs=False)
print(f"    Normalized Gamma^V (|cos_nu|):  {ga_a/na_a:.8e}")
print(f"    Normalized Gamma^V (cos_nu):    {gl_a/nl_a:.8e}")
print(f"    Normalized diff:                {abs(ga_a/na_a - gl_a/nl_a):.8e}")

# Test case B: Two LISA detectors at 60 deg separation on Earth orbit
print("  Test B: Two LISA-like detectors, 60 deg orbital separation")
# Det 1: same as above
# Det 2: rotated by 60 deg in the ecliptic plane
det2_u_b = (np.pi/2, np.pi/3)
det2_v_b = (np.pi/2, np.pi)

ga_b, na_b = compute_chiral_orf(f_test, L_test, det1_u, det1_v, det2_u_b, det2_v_b,
                                 theta_s, phi_s, d_test, use_abs=True)
gl_b, nl_b = compute_chiral_orf(f_test, L_test, det1_u, det1_v, det2_u_b, det2_v_b,
                                 theta_s, phi_s, d_test, use_abs=False)
print(f"    Normalized Gamma^V (|cos_nu|):  {ga_b/na_b:.8e}")
print(f"    Normalized Gamma^V (cos_nu):    {gl_b/nl_b:.8e}")
print(f"    Normalized diff:                {abs(ga_b/na_b - gl_b/nl_b):.8e}")

# Test case C: Non-coplanar (tilted detector)
print("  Test C: Non-coplanar (Det 2 tilted 30 deg out of plane)")
det2_u_c = (np.pi/2 - np.pi/12, np.pi/6)
det2_v_c = (np.pi/2 - np.pi/12, 2*np.pi/3 + np.pi/6)

ga_c, na_c = compute_chiral_orf(f_test, L_test, det1_u, det1_v, det2_u_c, det2_v_c,
                                 theta_s, phi_s, d_test, use_abs=True)
gl_c, nl_c = compute_chiral_orf(f_test, L_test, det1_u, det1_v, det2_u_c, det2_v_c,
                                 theta_s, phi_s, d_test, use_abs=False)
print(f"    Normalized Gamma^V (|cos_nu|):  {ga_c/na_c:.8e}")
print(f"    Normalized Gamma^V (cos_nu):    {gl_c/nl_c:.8e}")
print(f"    Normalized diff:                {abs(ga_c/na_c - gl_c/nl_c):.8e}")

# === Point 5: Frequency scan ===
print(f"\n{'=' * 70}")
print("5. FREQUENCY SCAN: Normalized ORF difference (Test B geometry)")
print("=" * 70)
freqs = np.logspace(-3, 1, 21)
max_rel_diff = 0.0
for freq in freqs:
    ga, na = compute_chiral_orf(freq, L_test, det1_u, det1_v, det2_u_b, det2_v_b,
                                 theta_s, phi_s, d_test, use_abs=True)
    gl, nl = compute_chiral_orf(freq, L_test, det1_u, det1_v, det2_u_b, det2_v_b,
                                 theta_s, phi_s, d_test, use_abs=False)
    abs_norm_a = abs(ga/na) if na > 0 else 0
    abs_norm_l = abs(gl/nl) if nl > 0 else 0
    rel_diff = abs(abs_norm_a - abs_norm_l) / (abs_norm_a + 1e-30)
    marker = " <<<" if rel_diff > 0.01 else ""
    print(f"    f={freq:8.4f} Hz:  norm(|cos_nu|)={abs_norm_a:.8e}, "
          f"norm(cos_nu)={abs_norm_l:.8e}, rel_diff={rel_diff:.6e}{marker}")
    max_rel_diff = max(max_rel_diff, rel_diff)

print(f"\n  Max relative ORF difference across frequency range: {max_rel_diff:.6e}")

# === Summary ===
print(f"\n{'=' * 70}")
print("SUMMARY")
print("=" * 70)
print("  Question: Does |cos_nu| vs cos_nu in the OLC transfer function")
print("  matter for the final ORF?")
print()
print("  Key observation: for cos_nu < 0, (1-|cos_nu|) != (1-cos_nu).")
print("  At cos_nu = -1: (1-|cos_nu|) = 0, (1-cos_nu) = 2.")
print("  This corresponds to GWs propagating opposite to the arm.")
print()
print(f"  Transfer function (single link, f=0.01 Hz):")
print(f"    |T| max absolute diff:    {np.max(mag_diff):.6e}")
print(f"    |T| mean relative diff:   {np.mean(mag_diff)/np.mean(np.abs(T_lin)):.6e}")
print(f"    Phase max diff:           {np.max(phase_diff)*180/np.pi:.4f} deg")
print()
print(f"  Sky-averaged <|T|^4> diff: {(avg_T2_abs - avg_T2_lin)/avg_T2_lin:.6e}")
print(f"  Chiral ORF max rel diff:  {max_rel_diff:.6e}")
print()
if max_rel_diff > 1e-3:
    print(f"  >>> DIFFERENCE IS SIGNIFICANT ({max_rel_diff*100:.3f}% relative error in ORF)")
    print(f"  >>> The |cos_nu| implementation should be corrected to cos_nu")
else:
    print(f"  >>> Difference is negligible ({max_rel_diff*100:.5f}% relative error)")
