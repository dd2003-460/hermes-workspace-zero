#!/usr/bin/env python3
"""
P2-3: Fine search near theta=34°, phi=91.5° for no-SP (chi=1.0) case.
This is the approach that matches v17's methodology (no spatial phase).

Frequency-independent R^V verification at best match.
"""
import numpy as np

c = 299792458.0
TARGET_RV = -7.750753e-3

def olc_transfer_function(f, L, cos_nu):
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - cos_nu
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f) * L / c
    return prefac * sinc_v * phase


def antenna_cw_sum(tG, pG, positions, L, tf_fn):
    nx = np.sin(tG) * np.cos(pG)
    ny = np.sin(tG) * np.sin(pG)
    nz = np.cos(tG)

    th = np.array([np.cos(tG)*np.cos(pG),
                   np.cos(tG)*np.sin(pG),
                   -np.sin(tG)])
    ph = np.array([-np.sin(pG), np.cos(pG), np.zeros_like(pG)])

    cw_links = [(0, 1), (1, 2), (2, 0)]
    R_plus = np.zeros_like(tG, dtype=np.complex128)
    R_cross = np.zeros_like(tG, dtype=np.complex128)

    for i, j in cw_links:
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)
        th_dot_u = th[0]*u[0] + th[1]*u[1] + th[2]*u[2]
        ph_dot_u = ph[0]*u[0] + ph[1]*u[1] + ph[2]*u[2]

        F_plus = th_dot_u**2 - ph_dot_u**2
        F_cross = 2.0 * th_dot_u * ph_dot_u

        cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
        T = tf_fn(np.ones_like(tG), L, cos_nu)

        R_plus += F_plus * T
        R_cross += F_cross * T

    return R_plus, R_cross


def build_constellation(L, inclination_rad):
    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([L, 0.0, 0.0])
    r3 = np.array([L/2, L*np.sqrt(3)/2, 0.0])
    positions = np.array([r1, r2, r3])

    cos_i = np.cos(inclination_rad)
    sin_i = np.sin(inclination_rad)
    rotated = np.zeros_like(positions)
    rotated[:, 0] = positions[:, 0]
    rotated[:, 1] = positions[:, 1] * cos_i - positions[:, 2] * sin_i
    rotated[:, 2] = positions[:, 1] * sin_i + positions[:, 2] * cos_i
    return rotated


def compute_orf_no_sp(R1p, R1x, R2p, R2x):
    """No SP: chi=1.0"""
    raw_chiral = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)
    raw_cross = np.real(np.conj(R1p)*R2p + np.conj(R1x)*R2x)

    S_A = np.real(np.conj(R1p)*R1p + np.conj(R1x)*R1x)
    S_B = np.real(np.conj(R2p)*R2p + np.conj(R2x)*R2x)

    rv = raw_chiral / np.sqrt(S_A * S_B) if (S_A > 1e-30 and S_B > 1e-30) else 0.0
    return raw_cross, raw_chiral, S_A, S_B, rv


L_lisa = 2.5e9
L_taiji = 3.0e9
pos1 = build_constellation(L_lisa, np.radians(30.0))
pos2 = build_constellation(L_taiji, np.radians(0.0))
# No delta_x — chi=1.0

# ===== Part 1: Fine search =====
print("=" * 90)
print("FINE SEARCH: no-SP (chi=1.0) around theta=34°, phi=91.5°")
print(f"Target R^V = {TARGET_RV:.10e}")
print("=" * 90)

thetas = np.arange(32.0, 38.0, 0.05)
phis = np.arange(88.0, 96.0, 0.05)

best_dist = 1e30
best = None
ntotal = 0

for td in thetas:
    theta = np.radians(td)
    for pd in phis:
        phi = np.radians(pd)
        ntotal += 1

        T = np.array([[theta]])
        P = np.array([[phi]])

        R1p, R1x = antenna_cw_sum(T, P, pos1, L_lisa, olc_transfer_function)
        R2p, R2x = antenna_cw_sum(T, P, pos2, L_taiji, olc_transfer_function)

        cross, chiral, SA, SB, rv = compute_orf_no_sp(R1p[0,0], R1x[0,0], R2p[0,0], R2x[0,0])

        dist = abs(rv - TARGET_RV)
        if dist < best_dist:
            best_dist = dist
            best = (td, pd, rv, dist, chiral, SA, SB, cross)
        if dist < 1e-10:
            print(f"  *** EXACT MATCH: theta={td:.2f}°, phi={pd:.2f}°, R^V={rv:.12e} ***")

print(f"\n  Evaluated {ntotal} points")
if best:
    td, pd, rv, dist, chiral, SA, SB, cross = best
    print(f"  Best match: theta = {td:.4f}°, phi = {pd:.4f}°")
    print(f"  R^V = {rv:.10e}")
    print(f"  Target = {TARGET_RV:.10e}")
    print(f"  |delta| = {dist:.10e}")
    print(f"  Relative error = {dist/abs(TARGET_RV)*100:.4f}%")

# ===== Part 2: Frequency sweep at best match =====
print(f"\n{'=' * 90}")
print("FREQUENCY SWEEP at best match (no-SP)")
print(f"{'=' * 90}")

if best:
    td, pd = best[0], best[1]
    theta = np.radians(td)
    phi = np.radians(pd)

    print(f"  {'f (Hz)':<12s} {'R^V':<22s} {'|delta|':<20s} {'R^V(f)/R^V(0.001Hz)':<25s}")
    print(f"  " + "-" * 80)

    rv0 = None
    for f in [0.0001, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1]:
        T = np.array([[theta]])
        P = np.array([[phi]])

        R1p, R1x = antenna_cw_sum(T, P, pos1, L_lisa, olc_transfer_function)
        R2p, R2x = antenna_cw_sum(T, P, pos2, L_taiji, olc_transfer_function)

        cross, chiral, SA, SB, rv = compute_orf_no_sp(R1p[0,0], R1x[0,0], R2p[0,0], R2x[0,0])

        dist = abs(rv - TARGET_RV)
        ratio = rv / rv0 if rv0 else 1.0
        if rv0 is None:
            rv0 = rv
        print(f"  {f:<12.4f} {rv:<22.6e} {dist:<20.6e} {ratio:<25.6f}")

# ===== Part 3: Sky-averaged (no SP) =====
print(f"\n{'=' * 90}")
print("SKY-AVERAGED (no SP, chi=1.0)")
print(f"{'=' * 90}")

f = 0.001
TG = np.linspace(0, np.pi, 256, endpoint=False)
PG = np.linspace(0, 2*np.pi, 512, endpoint=False)
_TG, _PG = np.meshgrid(TG, PG, indexing='ij')

R1p, R1x = antenna_cw_sum(_TG, _PG, pos1, L_lisa, olc_transfer_function)
R2p, R2x = antenna_cw_sum(_TG, _PG, pos2, L_taiji, olc_transfer_function)

dtheta = np.pi / 256
dphi = 2.0 * np.pi / 512
sin_theta = np.sin(_TG)
dOmega = sin_theta * dtheta * dphi
inv4pi = 1.0 / (4.0 * np.pi)

cross_sky = np.real(np.conj(R1p)*R2p + np.conj(R1x)*R2x)
chiral_sky = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)

S_A_sky = np.sum(np.real(np.conj(R1p)*R1p + np.conj(R1x)*R1x) * dOmega) * inv4pi
S_B_sky = np.sum(np.real(np.conj(R2p)*R2p + np.conj(R2x)*R2x) * dOmega) * inv4pi

gamma_I_sky = np.sum(cross_sky * dOmega) * inv4pi
gamma_V_sky = np.sum(chiral_sky * dOmega) * inv4pi
rv_sky = gamma_V_sky / np.sqrt(S_A_sky * S_B_sky)

print(f"  Gamma^I (sky-avg) = {gamma_I_sky:.10e}")
print(f"  Gamma^V (sky-avg) = {gamma_V_sky:.10e}")
print(f"  R^V (sky-avg) = {rv_sky:.10e}")
print(f"  vs target = {TARGET_RV:.10e}")
print(f"  |ratio| = {abs(rv_sky/TARGET_RV):.6f}")

# ===== Part 4: Write results =====
if best:
    td, pd, rv, dist, chiral, SA, SB, cross = best
    results = f"""P2-3 Fine Search (No SP, chi=1.0)
=====================================

Target R^V = {TARGET_RV:.10e}
Constellations: LISA30 x Taiji0 (no spatial offset)
Frequency: 0.001 Hz

Best match:
  theta = {td:.4f}°
  phi = {pd:.4f}°
  R^V = {rv:.10e}
  |delta| = {dist:.10e}
  Relative error = {dist/abs(TARGET_RV)*100:.6f}%

Sky-averaged:
  Gamma^V = {gamma_V_sky:.10e}
  R^V (sky-avg) = {rv_sky:.10e}
  vs target = {TARGET_RV:.10e}
  |ratio| = {abs(rv_sky/TARGET_RV):.6f}
  → Sky-avg is {'much smaller' if abs(rv_sky) < abs(TARGET_RV) else 'different'} than v17 target
  → Confirms v17 value is a single-direction result, not sky-averaged
"""
    with open("loop/2-loop/p23-fine-no-sp.txt", "w") as f:
        f.write(results)
    print(f"\nResults written to loop/2-loop/p23-fine-no-sp.txt")
