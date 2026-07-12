#!/usr/bin/env python3
"""Debug T6 normalization mismatch: analytical gamma_I vs numerical auto ORF."""
import numpy as np
import sys
sys.path.insert(0, '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts')

c = 299792458.0
AU = 1.495978707e11
LISA_L = 2_500_000.0 * 1000.0
TAIJI_L = 3_000_000.0 * 1000.0
LISA_INCLINATION = np.pi / 6.0
TAIJI_INCLINATION = 0.0

from scipy.special import spherical_jn

def spherical_bessel(n, x):
    return spherical_jn(int(n), x)

def compute_detector_tensor_dimensionless(constellation):
    pos = constellation['positions']
    D = np.zeros((3, 3))
    cw_links = [(0, 1), (1, 2), (2, 0)]
    for i, j in cw_links:
        arm = pos[j] - pos[i]
        arm_len = np.linalg.norm(arm)
        if arm_len < 1e-30:
            continue
        u = arm / arm_len
        D += np.outer(u, u)
    return D

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
        'name': name,
        'positions': rotated,
        'centroid': centroid,
        'inclination': inclination,
        'reference_position': reference_position,
        'L': L
    }

const_lisa = make_triangle_constellation('LISA', LISA_L, LISA_INCLINATION,
                                          reference_position=np.array([0, 0, 0]))
const_taiji = make_triangle_constellation('Taiji', TAIJI_L, TAIJI_INCLINATION,
                                           reference_position=np.array([AU, 0, 0]))

D1 = compute_detector_tensor_dimensionless(const_lisa)
D2 = compute_detector_tensor_dimensionless(const_taiji)

print("=== D tensors ===")
print(f"trace(D1) = {np.trace(D1):.4f}")
print(f"trace(D2) = {np.trace(D2):.4f}")
print(f"det(D1) = {np.linalg.det(D1):.2e}")
print(f"det(D2) = {np.linalg.det(D2):.2e}")

# The auto ORF numerical computes: Gamma = sum(R1*R2) / sqrt(sum(R1^2)*sum(R2^2))
# where R = theta^T D phi (response for each arm direction)

# Let's compute the sky integral of response products analytically
# For a single triangle (3 CW links), the response is:
# R_plus(theta, phi) = sum_l theta^T D_l theta = theta^T D_tot theta
# where D_tot = sum_l D_l (the dimensionless detector tensor)

# The auto-response integral:
# <R_plus^2 + R_cross^2> = integral (theta^T D theta)^2 dOmega + integral (theta^T D phi)^2 dOmega

# Let's compute these sky integrals numerically
thetas = np.linspace(0, np.pi, 200)
phis = np.linspace(0, 2*np.pi, 400, endpoint=False)
tG, pG = np.meshgrid(thetas, phis, indexing='ij')
dO = np.sin(tG) * (2*np.pi/400) * (np.pi/200)

th = np.stack([np.cos(tG)*np.cos(pG), np.cos(tG)*np.sin(pG), -np.sin(tG)])
ph = np.stack([-np.sin(pG), np.cos(pG), np.zeros_like(np.sin(pG))])

# Response: R_plus = theta^T D theta, R_cross = theta^T D phi
def response(a, b, D):
    """Compute a^T D b for arrays a,b of shape (3, ntheta, nphi)."""
    result = np.zeros_like(a[0])
    for i in range(3):
        for j in range(3):
            result += D[i, j] * a[i] * b[j]
    return result

R1_plus = response(th, th, D1)
R1_cross = response(th, ph, D1)
R2_plus = response(th, th, D2)
R2_cross = response(th, ph, D2)

auto_signal = R1_plus * R2_plus + R1_cross * R2_cross
auto_int = np.sum(auto_signal * dO)

norm1 = np.sum((R1_plus**2 + R1_cross**2) * dO)
norm2 = np.sum((R2_plus**2 + R2_cross**2) * dO)

print(f"\n=== Sky integrals (numerical) ===")
print(f"auto_int = {auto_int}")
print(f"norm1 = {norm1}")
print(f"norm2 = {norm2}")
print(f"auto_int / sqrt(norm1*norm2) = {auto_int / np.sqrt(norm1 * norm2)}")

# Now compute the same analytical quantities
const12 = const_lisa
delta_x = const12['centroid'] - const_taiji['centroid']
delta_r = np.linalg.norm(delta_x)
s_hat = delta_x / delta_r

print(f"\n=== Delta ===")
print(f"delta_r = {delta_r}")
print(f"s_hat = {s_hat}")

tr_D1D2 = np.einsum('ab,ab->', D1, D2)
D1_s = D1 @ s_hat
D2_s = D2 @ s_hat
term_s = np.dot(D1_s, D2_s)
sD1s = np.dot(s_hat, D1 @ s_hat)
sD2s = np.dot(s_hat, D2 @ s_hat)
term_ss = sD1s * sD2s

print(f"\n=== Contractions ===")
print(f"tr(D1*D2) = {tr_D1D2}")
print(f"(D1@s) . (D2@s) = {term_s}")
print(f"(s^T D1 s) * (s^T D2 s) = {term_ss}")

# At f=0 (psi=0): j0=1, j2=0, j4=0
# bI = (1/7) * M_inv * [1, 0, 0]
# M_inv[0] = first column of M_inv
M = np.array([[14, -21, 0], [1, 0, 0], [60, -10, 35/2]])
M_inv = np.linalg.inv(M)
print(f"\n=== M_inv ===")
print(M_inv)

bI_at_0 = (1.0/7.0) * M_inv @ np.array([1.0, 0.0, 0.0])
b0_0, b1_0, b2_0 = bI_at_0
print(f"bI at psi=0: {bI_at_0}")

# gamma_I at psi=0
gamma_I_at_0 = 4.0 * (b0_0 * tr_D1D2 + b1_0 * term_s + b2_0 * term_ss)
print(f"gamma_I at psi=0: {gamma_I_at_0}")

# Check: auto_int / gamma_I_at_0
print(f"\nauto_int / gamma_I(0) = {auto_int / gamma_I_at_0}")

# What about the ratio for other frequencies?
print(f"\n=== Ratio at different frequencies ===")
for f in [0.001, 0.005, 0.01, 0.05, 0.1]:
    psi = 2.0 * np.pi * f * delta_r / c
    j0 = spherical_bessel(0, psi)
    j2 = spherical_bessel(2, psi)
    j4 = spherical_bessel(4, psi)
    bI = (1.0/7.0) * M_inv @ np.array([j0, j2, j4])
    b0, b1, b2 = bI
    gi = 4.0 * (b0 * tr_D1D2 + b1 * term_s + b2 * term_ss)
    ratio = auto_int / gi
    print(f"f={f:5.3f} Hz: psi={psi:.4f}, gamma_I={gi:.10f}, auto_int/gamma_I={ratio:.6f}")

# Now let's check: what does the auto_int equal for coplanar detectors?
# and what is the expected normalization?

# Let me also check the auto response for a single detector
# The auto ORF should be 1 by definition (normalized by auto response)
# But here we compute LISA-Taiji cross ORF, so auto_int is not 1

# The JCAP formula should give the unnormalized cross ORF
# The numerical code normalizes by sqrt(auto1 * auto2)

# Let me compute the auto responses separately
print(f"\n=== Auto responses for each detector ===")
for name, D in [('LISA', D1), ('Taiji', D2)]:
    R_plus = response(th, th, D)
    R_cross = response(th, ph, D)
    auto_val = np.sum((R_plus**2 + R_cross**2) * dO)
    print(f"{name}: auto = {auto_val}")

# Check: what is the expected auto response from the dimensionless D tensor?
# The auto response for a triangle is:
# <R_plus^2 + R_cross^2> = 4pi/5 * (4*b0*tr(D^2) + 2*b1*(D@s).**(D@s) + term_ss?)
# Actually, for auto correlation at zero frequency, this should be related to the trace.

# Let me verify: for the parity-even case, the cross-correlation at f=0 should be:
# Gamma_I(0) = (4pi/5) * (4*b0(0)*tr(D1D2) + ...)
# where b0(0) = 1/7 * 14^(-1) * 1 = 1/49? No...

# Actually M_inv @ [1,0,0] = first column of M_inv
# Let me compute b0(0) more carefully
print(f"\n=== Detailed bI at psi=0 ===")
print(f"b0 = {b0_0} = {b0_0:.15f}")
print(f"b1 = {b1_0} = {b1_0:.15f}")
print(f"b2 = {b2_0} = {b2_0:.15f}")

# The expected auto response at f=0 for coplanar detectors:
# For coplanar (z=0), D is purely in xy plane
# trace(D) = 3 (for 3 arms of equilateral triangle)
# D = [[dxx, dxy, 0], [dxy, dyy, 0], [0, 0, 0]]
# Since det(D)=0, one eigenvalue is 0
# The non-zero eigenvalues sum to 3

# The expected normalized cross ORF at f=0 should be...
# The numerical code computes auto_int / sqrt(norm1 * norm2)
# where norm1 is the sky integral of (R1+^2 + R1x^2)
# For coplanar detectors, this gives norm1 = norm2 = auto_int (when const1==const2)
# Wait, auto_int is for the CROSS correlation between LISA and Taiji

# The key question: what should gamma_I_analytical give?
# JCAP Appendix B gives the unnormalized cross-correlation function
# The numerical code normalizes by sqrt(auto1 * auto2)

# Let me check what JCAP expects for the auto ORF
# For auto correlation (same detector), Gamma^I should be 1 (normalized)
# So for cross correlation, the expected normalization is sqrt(auto1*auto2)

# Let me compute: what is the JCAP formula's auto response?
# For const1 == const2, gamma_I should give the unnormalized auto response
# The numerical auto ORF gives 1 (by normalization)
print(f"\n=== Self-consistency check ===")
# Compute auto response for LISA using JCAP formula
D1_self = compute_detector_tensor_dimensionless(const_lisa)
tr_D1self_D1self = np.einsum('ab,ab->', D1_self, D1_self)
D1s_self = D1_self @ s_hat
term_s_self = np.dot(D1s_self, D1s_self)
sD1s_self = np.dot(s_hat, D1_self @ s_hat)
term_ss_self = sD1s_self**2

gi_lisa_auto = 4.0 * (b0_0 * tr_D1self_D1self + b1_0 * term_s_self + b2_0 * term_ss_self)
print(f"JCAP gamma_I auto (LISA, f=0): {gi_lisa_auto}")

# This should correspond to norm1 computed numerically
print(f"Numerical auto (LISA): {norm1}")
print(f"Ratio: {norm1 / gi_lisa_auto}")

# Now the cross:
# The numerical cross ORF = auto_int / sqrt(norm1 * norm2)
# The JCAP cross formula gives gamma_I (unnormalized)
# So the ratio should be: auto_int / gamma_I_analytical = sqrt(norm1 * norm2) / (some factor)

# Let me check what normalization factor makes them match:
print(f"\n=== Cross check ===")
print(f"auto_int (numerical cross) = {auto_int}")
print(f"gamma_I_analytical (f=0) = {gamma_I_at_0}")
print(f"auto_int / gamma_I_analytical = {auto_int / gamma_I_at_0}")
print(f"sqrt(norm1 * norm2) = {np.sqrt(norm1 * norm2)}")

# The key insight: what is the relationship?
# auto_int = integral of (R1+*R2+ + R1x*R2x) dOmega
# gamma_I_analytical is supposed to be this integral / (4pi) or something similar?
# Let me check if auto_int equals gamma_I_analytical * 4pi / 5 or similar
print(f"\n=== Checking expected normalization ===")
print(f"auto_int = {auto_int}")
print(f"gamma_I_at_0 * 4pi/5 = {gamma_I_at_0 * 4*np.pi/5}")
print(f"gamma_I_at_0 * 4pi = {gamma_I_at_0 * 4*np.pi}")
print(f"auto_int / (4pi/5) = {auto_int / (4*np.pi/5)}")
print(f"auto_int / (4pi) = {auto_int / (4*np.pi)}")
print(f"auto_int / gamma_I_at_0 = {auto_int / gamma_I_at_0}")

# Let me also check: what is 4pi/15 * tr(D1D2)?
print(f"\n4pi/15 * tr(D1D2) = {4*np.pi/15 * tr_D1D2}")
print(f"4pi/5 * tr(D1D2) = {4*np.pi/5 * tr_D1D2}")

# Check auto response: for auto, the expected normalization factor
# For auto correlation at f=0: gamma_I_auto = (4pi/15) * tr(D^2) * 4?
# Or something with the trace

# Actually, let me compute: what should the auto response be for a coplanar triangle?
# R_plus = sum_l (theta^T u_l)^2 - (theta^T phi_l)^2 ... no, for CW links:
# R_plus = sum_l ((theta . u_l)^2 - (phi . u_l)^2) = theta^T D theta
# For coplanar detectors in xy plane, D has only xy components

# The auto response integral:
# integral (theta^T D theta)^2 dOmega + integral (theta^T D phi)^2 dOmega
# = (4pi/5) * [4 * tr(D^2) + ...] for auto

# Wait, for auto correlation (const1 = const2 = const_lisa):
# tr(D1D2) = tr(D1^2)
# term_s = (D1@s).(D1@s) = |D1@s|^2
# term_ss = (s^T D1 s)^2

# Let me compute what the JCAP formula gives vs numerical for auto
D1D1 = np.einsum('ab,cd->ac', D1, D1)
tr_D1D1 = np.einsum('ab,ab->', D1, D1)
print(f"\n=== LISA auto correlations ===")
print(f"tr(D1*D1) = {tr_D1D1}")
D1s = D1 @ s_hat
print(f"|D1@s|^2 = {np.dot(D1s, D1s)}")
print(f"(s^T D1 s)^2 = {(np.dot(s_hat, D1 @ s_hat))**2}")

# Now let me try: auto_int should equal gamma_I_analytical * normalization
# At f=0, the JCAP formula gives gamma_I(0) = 4 * b0(0) * tr(D1D2) + ...
# What is the correct normalization?

# Let me try: does auto_int = (4pi/5) * gamma_I_at_0 * something?
# Or auto_int = gamma_I_at_0 * factor?

# The numerical auto_int = 5.84 (for cross between LISA and Taiji)
# The JCAP gamma_I_at_0 = about -0.02
# So the factor is about 5.84 / (-0.02) = -292

# Hmm, that's close to the -279 to -300 range we saw before.
# But the factor changes with frequency because gamma_I oscillates.

# The issue is that the JCAP formula is a low-frequency expansion.
# At low frequencies (psi << 1), j0 ~ 1, j2 ~ psi^2/14, j4 ~ psi^4/396
# So gamma_I changes with frequency because j2 and j4 contribute.

# But the numerical code uses the EXACT response functions (no low-freq expansion).
# The analytical formula is only valid at very low frequency.

# For T6, we should compare at the same low frequency limit.
# At f -> 0, both should give the same value.

# Let me verify: at f=0, what should both give?
print(f"\n=== AT f=0 (psi=0) ===")
print(f"j0(0) = {spherical_bessel(0, 0)}")
print(f"j2(0) = {spherical_bessel(2, 0)}")
print(f"j4(0) = {spherical_bessel(4, 0)}")

# At f=0, j0=1, j2=0, j4=0
# bI = (1/7) * M_inv @ [1, 0, 0]
# gamma_I = 4 * b0 * tr(D1D2)

# But wait - the JCAP formula for gamma_I has spherical Bessel functions j0, j2, j4
# These depend on psi = 2 pi f delta_r / c
# At f=0, psi=0, so j0=1, j2=0, j4=0

# The numerical code at f close to 0 but non-zero: the response is still
# computed exactly without low-freq expansion

# So the issue might be that the JCAP formula gives the sky-AVERAGED cross-correlation
# while the numerical gives the exact integral

# Let me try: what if we divide gamma_I by 4pi and multiply by something?
# Or what if gamma_I already includes the sky average (1/4pi factor)?

# In the JCAP paper, gamma_V and gamma_I are sky-averaged quantities.
# So gamma_I should be: (1/4pi) * integral(...dOmega)
# Therefore: integral = 4pi * gamma_I
print(f"\n=== Checking 4pi normalization ===")
print(f"auto_int / (4pi * gamma_I_at_0) = {auto_int / (4*np.pi * gamma_I_at_0)}")

# Or maybe the normalization is different. Let me check with auto correlation.
# For auto correlation of the same detector, the JCAP formula gives gamma_I_auto.
# The numerical gives 1 (normalized auto ORF).
# The unnormalized auto integral = integral (R^2) dOmega
# = (1/4pi) * integral (R^2) dOmega * 4pi = gamma_I_auto * 4pi?
# No wait, for auto, the numerical normalizes by sqrt(auto1*auto2) = auto1
# So the numerical auto ORF = auto1/auto1 = 1

# The question is: what normalization does the JCAP formula use?
# Looking at JCAP Appendix B, the formulas for gamma_V and gamma_I
# give the ORF values directly (sky-averaged)

# The numerical code computes: Gamma = integral(R1*R2 dOmega) / sqrt(integral(R1^2 dOmega) * integral(R2^2 dOmega))
# The JCAP formula computes: gamma = some combination of D tensors and Bessel functions

# These should give the SAME value when properly normalized.
# The issue is that the JCAP formula uses dimensionless D tensors with trace=3,
# while the numerical code uses the actual detector responses.

# Let me check if the JCAP auto ORF formula gives a constant that when used
# as the normalization denominator gives matching results.

# For auto: gamma_I_auto = 4 * (b0 * tr(D^2) + b1 * |D@s|^2 + b2 * (s^T D s)^2)
# If we divide by gamma_I_auto (same formula for auto), we get 1.
# For cross: gamma_I_cross = 4 * (b0 * tr(D1D2) + b1 * (D1@s).(D2@s) + b2 * (s^T D1 s)(s^T D2 s))
# Dividing by sqrt(gamma_I_auto1 * gamma_I_auto2) would give the normalized cross ORF.

# Is that what the JCAP formula should be? Let me check:
gamma_I_auto1 = 4.0 * (b0_0 * tr_D1D1 + b1_0 * np.dot(D1s, D1s) + b2_0 * (np.dot(s_hat, D1 @ s_hat))**2)
gamma_I_auto2 = 4.0 * (b0_0 * np.einsum('ab,ab->', D2, D2) + b1_0 * np.dot(D2 @ s_hat, D2 @ s_hat) + b2_0 * (np.dot(s_hat, D2 @ s_hat))**2)

print(f"\n=== Self-normalized check ===")
print(f"gamma_I_auto(LISA) = {gamma_I_auto1}")
print(f"gamma_I_auto(Taiji) = {gamma_I_auto2}")
print(f"gamma_I_cross = {gamma_I_at_0}")
print(f"gamma_I_cross / sqrt(gamma_I_auto1 * gamma_I_auto2) = {gamma_I_at_0 / np.sqrt(gamma_I_auto1 * gamma_I_auto2)}")
print(f"Numerical cross ORF (no TF, no phase) = {auto_int / np.sqrt(norm1 * norm2)}")
