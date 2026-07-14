#!/usr/bin/env python3
"""Debug: gamma_I for two identical coplanar detectors should give ORF=1 at f=0."""
import numpy as np
import sys
sys.path.insert(0, '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts')

c = 299792458.0
from scipy.special import spherical_jn
def spherical_bessel(n, x):
    return spherical_jn(int(n), x)

def make_triangle_constellation(name, L, inclination, reference_position=None):
    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([L, 0.0, 0.0])
    r3 = np.array([L / 2, L * np.sqrt(3) / 2, 0.0])
    positions = np.array([r1, r2, r3])
    cos_i, sin_i = np.cos(inclination), np.sin(inclination)
    rotated = np.zeros_like(positions)
    rotated[:, 0] = positions[:, 0]
    rotated[:, 1] = positions[:, 1] * cos_i - positions[:, 2] * sin_i
    rotated[:, 2] = positions[:, 1] * sin_i + positions[:, 2] * cos_i
    centroid = np.mean(rotated, axis=0)
    return {
        'name': name, 'positions': rotated, 'centroid': centroid,
        'inclination': inclination, 'reference_position': reference_position, 'L': L
    }

def compute_detector_tensor_dimensionless(constellation):
    pos = constellation['positions']
    D = np.zeros((3, 3))
    cw_links = [(0, 1), (1, 2), (2, 0)]
    for i, j in cw_links:
        arm = pos[j] - pos[i]
        arm_len = np.linalg.norm(arm)
        if arm_len < 1e-30: continue
        u = arm / arm_len
        D += np.outer(u, u)
    return D

def response(a, b, D):
    result = np.zeros_like(a[0])
    for i in range(3):
        for j in range(3):
            result += D[i, j] * a[i] * b[j]
    return result

# Test case: Two identical coplanar detectors (same orientation) with zero separation
L = 3e9
const_A = make_triangle_constellation('A', L, 0.0)
const_B = make_triangle_constellation('B', L, 0.0)
const_B['centroid'] = const_A['centroid']  # zero separation

D1 = compute_detector_tensor_dimensionless(const_A)
D2 = compute_detector_tensor_dimensionless(const_B)

s_hat = np.array([0.0, 0.0, 1.0])  # arbitrary, delta_r = 0

M = np.array([[14, -21, 0], [1, 0, 0], [60, -10, 35/2]])
M_inv = np.linalg.inv(M)

# At f=0: psi=0, j0=1, j2=0, j4=0
psi = 0.0
j0 = spherical_bessel(0, psi)
j2 = spherical_bessel(2, psi)
j4 = spherical_bessel(4, psi)

bI = (1.0/7.0) * M_inv @ np.array([j0, j2, j4])
b0_I, b1_I, b2_I = bI

print("=== Two identical coplanar detectors (zero separation) ===")
print(f"bI = {bI}")
print(f"j0={j0}, j2={j2}, j4={j4}")
print(f"D1 = D2 = {D1}")

tr = np.einsum('ab,ab->', D1, D2)
D1s = D1 @ s_hat
D2s = D2 @ s_hat
term_s = np.dot(D1s, D2s)
sD1s = np.dot(s_hat, D1 @ s_hat)
sD2s = np.dot(s_hat, D2 @ s_hat)
term_ss = sD1s * sD2s

print(f"\ntr(D1D2) = {tr}")
print(f"(D@s).(D@s) = {term_s}")
print(f"s^T D s = {sD1s}")
print(f"(s^T D s)^2 = {term_ss}")

gamma_I = 4.0 * (b0_I * tr + b1_I * term_s + b2_I * term_ss)
print(f"\ngamma_I (JCAP) = {gamma_I}")

# For identical detectors, the ORF should be EXACTLY 1 at zero separation
# (perfect correlation)
# The self-correlation auto = integral(R^2 + R_x^2)
# So the ORF = integral(R*R + Rx*Rx) / sqrt(integral(R^2+Rx^2)^2) = 1

# Let's compute the numerical ORF
ntheta, nphi = 180, 360
thetas = np.linspace(0, np.pi, ntheta)
phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
tG, pG = np.meshgrid(thetas, phis, indexing='ij')
dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)

th = np.stack([np.cos(tG)*np.cos(pG), np.cos(tG)*np.sin(pG), -np.sin(tG)])
ph = np.stack([-np.sin(pG), np.cos(pG), np.zeros_like(np.sin(pG))])

R1_plus = response(th, th, D1)
R1_cross = response(th, ph, D1)
R2_plus = response(th, th, D2)
R2_cross = response(th, ph, D2)

cross_int = np.sum((R1_plus * R2_plus + R1_cross * R2_cross) * dO)
auto_int = np.sum((R1_plus**2 + R1_cross**2) * dO)
num_orf = cross_int / np.sqrt(auto_int * auto_int)

print(f"\n=== Numerical result ===")
print(f"Cross integral = {cross_int}")
print(f"Auto integral = {auto_int}")
print(f"Numerical ORF = {num_orf}")

print(f"\n=== Comparison ===")
print(f"JCAP gamma_I = {gamma_I}")
print(f"Numerical ORF = {num_orf}")
print(f"JCAP should give... what?")

# For self-correlation, JCAP gives:
# gamma_I_self = 4 * (b0 * tr(D^2) + b1 * (D@s).(D@s) + b2 * (s^T D s)^2)
# This is the JCAP "auto" formula.

# For the numerical ORF:
# ORF = <R1R2> / sqrt(<R1^2><R2^2>)
# For identical detectors: ORF = <R1^2> / <R1^2> = 1

# For JCAP to give the ORF (not the integral), it must normalize by auto-correlations.
# But JCAP doesn't do this normalization explicitly.

# The key question: does JCAP gamma_I = <R1R2> (integral over sky) or
# does gamma_I = <R1R2>/<R^2> (normalized)?

# Let me check: what is 4pi * gamma_I?
print(f"\n4pi * gamma_I = {4*np.pi * gamma_I}")
print(f"gamma_I / (4pi) = {gamma_I / (4*np.pi)}")
print(f"gamma_I / auto_int = {gamma_I / auto_int}")
print(f"gamma_I * auto_int = {gamma_I * auto_int}")

# Now try: what is the analytical sky integral of R_plus^2 for a single coplanar detector?
# R_plus = theta^T D theta
# <theta_a theta_b theta_c theta_d> = 4pi/15 (delta_ab delta_cd + delta_ac delta_bd + delta_ad delta_bc)
# So <R_plus^2> = D_ab D_cd <theta_a theta_b theta_c theta_d>
#               = D_ab D_cd * 4pi/15 (delta_ab delta_cd + delta_ac delta_bd + delta_ad delta_bc)
#               = 4pi/15 * (tr(D)^2 + tr(D^2) + tr(D^2))
#               = 4pi/15 * (tr(D)^2 + 2*tr(D^2))

# For coplanar detector: tr(D) = 3, tr(D^2) = 3^2/2 = 4.5... wait let me compute.
trD = np.trace(D1)
trD2 = np.einsum('ab,ab->', D1, D1)
print(f"\ntr(D1) = {trD}")
print(f"tr(D1^2) = {trD2}")
expected_R_plus_squared_avg = 4*np.pi/15 * (trD**2 + 2*trD2)
print(f"<R_plus^2> (analytical) = {expected_R_plus_squared_avg}")
actual_R_plus_squared_avg = np.sum(R1_plus**2 * dO)
print(f"<R_plus^2> (numerical) = {actual_R_plus_squared_avg}")

# Now with cross term:
# <R_cross^2> = <theta_a D_ab phi_b theta_c D_cd phi_d>
#             = D_ab D_cd <theta_a phi_b theta_c phi_d>
# For isotropic sky: <theta_a phi_b theta_c phi_d> = ?
# This requires knowing the correlation between theta and phi.

# For the combined quantity:
# <R_plus^2 + R_cross^2> = ?
# Let me compute this numerically and see if there's a pattern.
total_avg = np.sum((R1_plus**2 + R1_cross**2) * dO)
print(f"\n<R_plus^2 + R_cross^2> (numerical) = {total_avg}")

# For coplanar detector, R_cross = 0 always (no z components in D).
# So <R_plus^2 + R_cross^2> = <R_plus^2> = 4pi/15 * (9 + 9) = 4pi * 6/5 = 24pi/5
# Wait, tr(D)=3, tr(D^2)=4.5 for coplanar:
# = 4pi/15 * (9 + 9) = 4pi * 18/15 = 4pi * 6/5 = 24pi/5 = 15.08

# But numerically we got ~9.66. Something's off.
# Let me recompute tr(D^2) for coplanar detector:
print(f"\nDetailed D tensor:")
print(D1)
print(f"D1^2 = {D1 @ D1}")
print(f"tr(D1^2) = {np.einsum('ab,ab->', D1, D1)}")

# For coplanar detector in xy plane:
# D = [[3/2, 0, 0], [0, 3/2, 0], [0, 0, 0]]
# tr(D) = 3
# D^2 = [[9/4, 0, 0], [0, 9/4, 0], [0, 0, 0]]
# tr(D^2) = 9/2 = 4.5

# So <R_plus^2> = 4pi/15 * (9 + 9) = 24pi/5 = 15.08
# But numerical gives ~9.66. The issue: the numerical sky grid doesn't give exact results.
# Or my formula is wrong.

# Actually wait, R_plus = theta^T D theta, not R_plus = theta^T D^2 theta.
# Let me redo:
# R_plus^2 = (theta^T D theta)^2 = theta_a D_ab theta_b theta_c D_cd theta_d
#           = D_ab D_cd theta_a theta_b theta_c theta_d

# <theta_a theta_b theta_c theta_d> = 4pi/15 (delta_ab delta_cd + delta_ac delta_bd + delta_ad delta_bc)
# So:
# <R_plus^2> = 4pi/15 * [D_ab D_cd (delta_ab delta_cd + delta_ac delta_bd + delta_ad delta_bc)]
#            = 4pi/15 * [D_ab D_ab + D_ab D_ba + D_ad D_da]
#            = 4pi/15 * [tr(D^2) + tr(D^2) + tr(D^2)]  (since D is symmetric)
#            = 4pi/15 * 3 * tr(D^2)
#            = 4pi/5 * tr(D^2)
#            = 4pi/5 * 9/2 = 18pi/5 = 11.31

# Hmm, but that's different from what I computed above. Let me be more careful.

# <R_plus^2> = D_ab D_cd <theta_a theta_b theta_c theta_d>
# <theta_a theta_b theta_c theta_d> is an isotropic 4th-rank tensor:
# = 4pi/15 * (delta_ab delta_cd + delta_ac delta_bd + delta_ad delta_bc)

# Contracting with D_ab D_cd:
# D_ab D_cd delta_ab delta_cd = (D_ab delta_ab) (D_cd delta_cd) = tr(D)^2 = 9
# D_ab D_cd delta_ac delta_bd = D_ab D_bd D_ac... no wait.
# = D_ab D_cd delta_ac delta_bd = D_ac D_ca = tr(D^2)
# D_ab D_cd delta_ad delta_bc = D_ad D_da = tr(D^2)

# So: <R_plus^2> = 4pi/15 * (tr(D)^2 + tr(D^2) + tr(D^2)) = 4pi/15 * (9 + 9) = 4pi * 6/5 = 24pi/5

# But tr(D^2) for D = diag(1.5, 1.5, 0) is 1.5^2 + 1.5^2 + 0 = 4.5
# tr(D) = 3, tr(D)^2 = 9
# So <R_plus^2> = 4pi/15 * (9 + 4.5 + 4.5) = 4pi/15 * 18 = 72pi/15 = 24pi/5 ≈ 15.08

# But numerical gives ~9.66. That's 72pi/15 vs 9.66.
# 24pi/5 ≈ 15.08 vs 9.66. Factor of ~1.56.

# I think the issue is that the sky integral <R_plus^2> should NOT just use
# isotropic <theta^4>. The theta basis vectors depend on k (direction of propagation).
# For each k direction, theta(k) is defined in a specific way.
# The isotropic formula <theta_a theta_b theta_c theta_d> = 4pi/15 * (...)
# applies when theta is the unit vector n (isotropic).
# But in GW physics, theta(k) is a UNIT VECTOR perpendicular to k.

# So the isotropic formula doesn't directly apply. I need to integrate over the sky.

# The correct approach: average over k-direction, with the specific definition of
# theta(k) and phi(k) used in the numerical code.
# The numerical integration gives the correct answer.

# So: for coplanar detectors, the numerical ORF at zero separation should be 1.
# And JCAP gamma_I should also be 1 (or should give -1 if the sign is wrong).

# For self-correlation of coplanar detector with itself:
D1s2 = D1 @ s_hat
term_s11 = np.dot(D1s2, D1s2)
sD1s1 = np.dot(s_hat, D1 @ s_hat)

# For self: D1 = D2
gi_self = 4.0 * (b0_I * np.einsum('ab,ab->', D1, D1) + b1_I * np.dot(D1s2, D1s2) + b2_I * sD1s1**2)
print(f"\n=== Self-correlation ===")
print(f"JCAP self gamma_I = {gi_self}")
print(f"For self-corr, ORF should be 1 or -1 (not 0)")
print(f"Numerical ORF = {num_orf}")
print(f"Numerical self-norm ORF = {num_orf} (by definition = 1)")

# The self-norm: self-norm JCAP = gamma_I_cross / sqrt(gamma_I_self1 * gamma_I_self2)
# For identical detectors: = 1 (or -1 if sign wrong)

# Now for the LISA-Taiji case:
LISA_L = 2_500_000.0 * 1000.0
TAIJI_L = 3_000_000.0 * 1000.0
const_lisa = make_triangle_constellation('LISA', LISA_L, np.pi/6)
const_taiji = make_triangle_constellation('Taiji', TAIJI_L, 0.0)

D_lisa = compute_detector_tensor_dimensionless(const_lisa)
D_taiji = compute_detector_tensor_dimensionless(const_taiji)
delta_x = const_lisa['centroid'] - const_taiji['centroid']
delta_r = np.linalg.norm(delta_x)
s_hat_lt = delta_x / delta_r

# At f=0
b0_I = (1/7) * M_inv[0,0]  # effectively 0
b1_I = (1/7) * M_inv[1,0]  # = -1/147
b2_I = (1/7) * M_inv[2,0]  # = -4/147

gi_lisa_cross = 4.0 * (b0_I * np.einsum('ab,ab->', D_lisa, D_taiji) + b1_I * np.dot(D_lisa @ s_hat, D_taiji @ s_hat) + b2_I * np.dot(s_hat, D_lisa @ s_hat) * np.dot(s_hat, D_taiji @ s_hat))

# Self correlations:
gi_lisa_self = 4.0 * (b0_I * np.einsum('ab,ab->', D_lisa, D_lisa) + b1_I * np.dot(D_lisa @ s_hat, D_lisa @ s_hat) + b2_I * np.dot(s_hat, D_lisa @ s_hat)**2)
gi_taiji_self = 4.0 * (b0_I * np.einsum('ab,ab->', D_taiji, D_taiji) + b1_I * np.dot(D_taiji @ s_hat, D_taiji @ s_hat) + b2_I * np.dot(s_hat, D_taiji @ s_hat)**2)

sn_jcap = gi_lisa_cross / np.sqrt(gi_lisa_self * gi_taiji_self)

# Numerical ORF
R_lisa_plus = response(th, th, D_lisa)
R_lisa_cross = response(th, ph, D_lisa)
R_taiji_plus = response(th, th, D_taiji)
R_taiji_cross = response(th, ph, D_taiji)

cross_int_lt = np.sum((R_lisa_plus * R_taiji_plus + R_lisa_cross * R_taiji_cross) * dO)
auto1_lt = np.sum((R_lisa_plus**2 + R_lisa_cross**2) * dO)
auto2_lt = np.sum((R_taiji_plus**2 + R_taiji_cross**2) * dO)
num_orf_lt = cross_int_lt / np.sqrt(auto1_lt * auto2_lt)

print(f"\n=== LISA-Taiji case ===")
print(f"JCAP self-lisa = {gi_lisa_self}")
print(f"JCAP self-taiji = {gi_taiji_self}")
print(f"JCAP cross = {gi_lisa_cross}")
print(f"Self-norm JCAP = {sn_jcap}")
print(f"Numerical ORF = {num_orf_lt}")
print(f"\nSign analysis:")
print(f"JCAP sign = {np.sign(gi_lisa_cross)}")
print(f"Numerical sign = {np.sign(num_orf_lt)}")
print(f"If JCAP sign is wrong, expected ORF = {-sn_jcap}")
print(f"Difference (with sign flip): {abs(-sn_jcap - num_orf_lt):.6f}")

# The self-norm JCAP gives -0.813 vs numerical +0.774
# The 5% residual difference might be due to:
# 1. The JCAP formula is an approximation (low-frequency)
# 2. A different convention in the paper
# 3. Numerical integration error

# Let me check: at f=0, the JCAP formula should give EXACTLY the numerical result.
# So the 5% difference at f=0 is a real discrepancy.

# Let me check the b-coefficients more carefully.
# The JCAP paper's Eq. B.18 gives the b coefficients.
# Let me verify: does the JCAP formula correctly give the sky-averaged ORF?

# The sky average of R_plus*R_plus for two coplanar detectors:
# <R_plus*R_plus> = <theta^T D1 theta * theta^T D2 theta>
# = D1_ab D2_cd <theta_a theta_b theta_c theta_d>

# But theta depends on the sky direction k.
# For a fixed k, theta(k) is in the plane perpendicular to k.
# <theta_a theta_b> (sky average) = ?

# Actually, the JCAP approach doesn't use theta(k). Instead, it directly computes
# the sky-averaged integral of D^ab D^cd * (contractions with s_hat).

# The key insight from JCAP: the sky-averaged integral can be expressed purely
# in terms of the dimensionless D tensors and the separation vector s_hat.
# The coefficients b^I encode the sky-averaging angular integrals.

# The b-coefficients are determined by matching to known cases (e.g., collinear
# detectors or coplanar detectors).

# If the b-coefficients have a sign error (all should be positive, not negative),
# then gamma_I would have the opposite sign and match the numerical result.

# Let me check: what if the correct b-coefficients have a minus sign?
bI_minus = -bI
b0_m, b1_m, b2_m = bI_minus
tr_LT = np.einsum('ab,ab->', D_lisa, D_taiji)
D1s_LT = D_lisa @ s_hat
D2s_LT = D_taiji @ s_hat
term_s_LT = np.dot(D1s_LT, D2s_LT)
sD1s_LT = np.dot(s_hat, D_lisa @ s_hat)
sD2s_LT = np.dot(s_hat, D_taiji @ s_hat)
term_ss_LT = sD1s_LT * sD2s_LT

gi_cross_minus = 4.0 * (b0_m * tr_LT + b1_m * term_s_LT + b2_m * term_ss_LT)
gi_lisa_self_minus = 4.0 * (b0_m * np.einsum('ab,ab->', D_lisa, D_lisa) + b1_m * np.dot(D_lisa @ s_hat, D_lisa @ s_hat) + b2_m * np.dot(s_hat, D_lisa @ s_hat)**2)
gi_taiji_self_minus = 4.0 * (b0_m * np.einsum('ab,ab->', D_taiji, D_taiji) + b1_m * np.dot(D_taiji @ s_hat, D_taiji @ s_hat) + b2_m * np.dot(s_hat, D_taiji @ s_hat)**2)
sn_jcap_minus = gi_cross_minus / np.sqrt(gi_lisa_self_minus * gi_taiji_self_minus)

print(f"\n=== With b-coefficient sign flip ===")
print(f"JCAP cross (negated b) = {gi_cross_minus}")
print(f"JCAP self-lisa (negated b) = {gi_lisa_self_minus}")
print(f"JCAP self-taiji (negated b) = {gi_taiji_self_minus}")
print(f"Self-norm JCAP (negated b) = {sn_jcap_minus}")
print(f"Numerical ORF = {num_orf_lt}")
print(f"Difference = {abs(sn_jcap_minus - num_orf_lt):.6f}")
print(f"Relative error = {abs(sn_jcap_minus - num_orf_lt)/num_orf_lt * 100:.2f}%")
