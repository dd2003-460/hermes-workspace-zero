#!/usr/bin/env python3
"""T6: Figure out the correct normalization for gamma_I."""
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

const_lisa = make_triangle_constellation('LISA', LISA_L, LISA_INCLINATION, reference_position=np.array([0, 0, 0]))
const_taiji = make_triangle_constellation('Taiji', TAIJI_L, TAIJI_INCLINATION, reference_position=np.array([AU, 0, 0]))

# Sky grid (high resolution for accuracy)
ntheta, nphi = 200, 400
thetas = np.linspace(0, np.pi, ntheta)
phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
tG, pG = np.meshgrid(thetas, phis, indexing='ij')
dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)

th = np.stack([np.cos(tG)*np.cos(pG), np.cos(tG)*np.sin(pG), -np.sin(tG)])
ph = np.stack([-np.sin(pG), np.cos(pG), np.zeros_like(np.sin(pG))])
k_hat = np.stack([np.sin(tG)*np.cos(pG), np.sin(tG)*np.sin(pG), np.cos(tG)])

# Response function: R(a,b,D) = a^T D b
def response(a, b, D):
    result = np.zeros_like(a[0])
    for i in range(3):
        for j in range(3):
            result += D[i, j] * a[i] * b[j]
    return result

# Dimensionless detector tensor
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

D1 = compute_detector_tensor_dimensionless(const_lisa)
D2 = compute_detector_tensor_dimensionless(const_taiji)

# JCAP s_hat (from const1 to const2)
delta_x = const_lisa['centroid'] - const_taiji['centroid']
delta_r = np.linalg.norm(delta_x)
s_hat = delta_x / delta_r

# M and M_inv
M = np.array([[14, -21, 0], [1, 0, 0], [60, -10, 35/2]])
M_inv = np.linalg.inv(M)

# gamma_I analytical (JCAP formula)
def gamma_I_jcap(f):
    psi = 2.0 * np.pi * abs(f) * delta_r / c
    j0 = spherical_bessel(0, psi)
    j2 = spherical_bessel(2, psi)
    j4 = spherical_bessel(4, psi)
    bI = (1.0/7.0) * M_inv @ np.array([j0, j2, j4])
    b0, b1, b2 = bI
    tr = np.einsum('ab,ab->', D1, D2)
    D1s = D1 @ s_hat
    D2s = D2 @ s_hat
    term_s = np.dot(D1s, D2s)
    sD1s = np.dot(s_hat, D1 @ s_hat)
    sD2s = np.dot(s_hat, D2 @ s_hat)
    term_ss = sD1s * sD2s
    return 4.0 * (b0 * tr + b1 * term_s + b2 * term_ss)

# Numerical: sky integral of response products
R1_plus = response(th, th, D1)
R1_cross = response(th, ph, D1)
R2_plus = response(th, th, D2)
R2_cross = response(th, ph, D2)

parity_even_signal = R1_plus * R2_plus + R1_cross * R2_cross
auto_int = np.sum(parity_even_signal * dO)  # sky integral of R1*R2

norm1 = np.sum((R1_plus**2 + R1_cross**2) * dO)
norm2 = np.sum((R2_plus**2 + R2_cross**2) * dO)
num_orf = auto_int / np.sqrt(norm1 * norm2)

print(f"Numerical sky integral (R1+*R2+ + R1x*R2x) = {auto_int:.10f}")
print(f"Numerical cross ORF (normalized) = {num_orf:.10f}")

# JCAP gamma_I at various frequencies
print(f"\nf (Hz)    JCAP gamma_I    JCAP*norm/4pi   num_orf    JCAP*norm/4pi / num_orf")
for f in [0.001, 0.005, 0.01, 0.05, 0.1]:
    gi = gamma_I_jcap(f)
    # Test various normalization conventions:
    # gamma_I should represent <R1+R2+ + R1xR2x> averaged over sky = (1/4pi) * integral
    norm_factor = np.sqrt(norm1 * norm2) / (4 * np.pi)
    scaled = gi * norm_factor
    ratio = scaled / num_orf
    psi = 2.0 * np.pi * abs(f) * delta_r / c
    print(f"{f:10.3f}  {gi:14.10f}  {scaled:14.10f}  {num_orf:10.6f}  {ratio:10.6f}")

# Now let's compute the sky integral of R1+*R2+ + R1x*R2x analytically
# R_plus = theta^T D theta, R_cross = theta^T D phi
# R1_plus * R2_plus = (theta^T D1 theta)(theta^T D2 theta) = theta_a D1_ab theta_b theta_c D2_cd theta_d
# R1_cross * R2_cross = (theta^T D1 phi)(theta^T D2 phi) = theta_a D1_ab phi_b theta_c D2_cd phi_d

# Sky integral of theta_a theta_b theta_c theta_d = (4pi/15) * (delta_ab delta_cd + delta_ac delta_bd + delta_ad delta_bc - 2/7 * corrections for anisotropy)
# But with s_hat breaking isotropy...

# Actually, the key insight: for coplanar detectors, the response in the z direction
# has specific symmetry. Let me check what the sky integral of the response product
# should be in terms of the contractions.

# Let me compute: what would make gamma_I match at f=0?
gi0 = gamma_I_jcap(0.0)
print(f"\n=== At f=0 ===")
print(f"gamma_I(0) = {gi0}")
print(f"auto_int = {auto_int}")
print(f"Required multiplier: {auto_int / gi0}")

# Also check: does the self-normalized JCAP give the right answer?
# For auto1:
tr11 = np.einsum('ab,ab->', D1, D1)
D1s = D1 @ s_hat
term_s11 = np.dot(D1s, D1s)
sD1s1 = np.dot(s_hat, D1 @ s_hat)

gi_auto1 = 4.0 * (-6.80272109e-03 * tr11 + (-6.80272109e-03) * term_s11 + (-3.88726919e-03) * sD1s1**2)
# Wait, at f=0, b0~0, b1=-0.006803, b2=-0.003887
b0_0, b1_0, b2_0 = -1.239e-19, -0.006802721088435373, -0.0038872691933916417
gi_auto1 = 4.0 * (b0_0 * tr11 + b1_0 * term_s11 + b2_0 * sD1s1**2)

# For auto2:
D2s = D2 @ s_hat
tr22 = np.einsum('ab,ab->', D2, D2)
term_s22 = np.dot(D2s, D2s)
sD2s2 = np.dot(s_hat, D2 @ s_hat)
gi_auto2 = 4.0 * (b0_0 * tr22 + b1_0 * term_s22 + b2_0 * sD2s2**2)

tr_D1D2 = np.einsum('ab,ab->', D1, D2)
D1s = D1 @ s_hat
D2s = D2 @ s_hat
term_s = np.dot(D1s, D2s)
sD1s = np.dot(s_hat, D1 @ s_hat)
sD2s = np.dot(s_hat, D2 @ s_hat)

print(f"\n=== Self-normalized JCAP ===")
print(f"gamma_I_auto1(f=0) = {gi_auto1}")
print(f"gamma_I_auto2(f=0) = {gi_auto2}")
gi_cross = 4.0 * (b0_0 * tr_D1D2 + b1_0 * term_s + b2_0 * sD1s * sD2s)
print(f"gamma_I_cross(f=0) = {gi_cross}")
print(f"Self-norm JCAP = {gi_cross / np.sqrt(gi_auto1 * gi_auto2)}")

# Check: numerical auto ORFs
norm1_only = np.sum((R1_plus**2 + R1_cross**2) * dO)
norm2_only = np.sum((R2_plus**2 + R2_cross**2) * dO)
print(f"Numerical auto1 = {norm1_only}")
print(f"Numerical auto2 = {norm2_only}")
print(f"Numerical cross ORF = {auto_int / np.sqrt(norm1_only * norm2_only)}")

# Key question: what's the relationship between JCAP normalization and numerical normalization?
# JCAP: gamma_I = 4*(b0*tr + b1*term_s + b2*term_ss)
# Numerical: ORF = integral(R1*R2) / sqrt(integral(R1^2)*integral(R2^2))

# For self-correlation (auto), both should give 1 when properly normalized.
# The self-norm JCAP gives -0.813 for cross, numerical gives 0.775.
# Close but sign opposite!

# Could there be a sign convention difference?
# JCAP might define gamma_I with a different sign convention.
# Or the M matrix inverse in JCAP might have a different sign.

# Let me check: if I negate gi_cross, does it match?
print(f"\n=== With sign flip ===")
print(f"-Self-norm JCAP = {-gi_cross / np.sqrt(gi_auto1 * gi_auto2)}")
print(f"Difference from numerical: {abs(-gi_cross / np.sqrt(gi_auto1 * gi_auto2) - num_orf):.6f}")

# Also try different M_inv conventions
print(f"\n=== Checking M matrix signature ===")
# Maybe the JCAP M matrix should be inverted differently?
# What if M_inv should be [1, 0, 0]^T / 14 for b0?
bI_alt = np.array([1.0/14, 0, 0])  # Simple diagonal inverse
b0_alt, b1_alt, b2_alt = bI_alt
gi_cross_alt = 4.0 * (b0_alt * tr_D1D2 + b1_alt * np.dot(D1s, D2s) + b2_alt * sD1s1 * sD2s2)
print(f"Alt gamma_I_cross (diag inverse) = {gi_cross_alt}")
print(f"Alt self-norm = {gi_cross_alt / np.sqrt(4*(b0_alt*tr11) * 4*(b0_alt*tr22))}")
print(f"Num orf = {num_orf}")

# tr_D1D2 value
tr_D1D2 = np.einsum('ab,ab->', D1, D2)
D1s = D1 @ s_hat
D2s = D2 @ s_hat
term_s = np.dot(D1s, D2s)
sD1s = np.dot(s_hat, D1 @ s_hat)
sD2s = np.dot(s_hat, D2 @ s_hat)
term_ss = sD1s * sD2s

print(f"\n=== All contractions ===")
print(f"tr(D1D2) = {tr_D1D2}")
print(f"(D1@s).(D2@s) = {term_s}")
print(f"(s^T D1 s) * (s^T D2 s) = {term_ss}")
print(f"tr(D1^2) = {tr11}")
print(f"tr(D2^2) = {tr22}")

# What about: the 4pi normalization?
# If the sky average gives: <R1*R2> = 4pi * gamma_I * normalization_factor
# Then: auto_int = 4pi * gamma_I * factor
# And: factor = auto_int / (4pi * gamma_I)
print(f"\n=== 4pi normalization ===")
factor = auto_int / (4 * np.pi * gi0)
print(f"factor = auto_int / (4pi * gamma_I(0)) = {factor}")

# Try: gamma_I should be multiplied by (4pi/5) for sky averaging?
# Or by 4pi / (15 * something)?
