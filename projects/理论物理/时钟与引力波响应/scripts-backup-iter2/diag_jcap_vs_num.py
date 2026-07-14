#!/usr/bin/env python3
"""Diagnostic: compare JCAP gamma_I with numerical sky integral (un-normalized)."""
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
print("D1 (LISA at 30 deg):", D1)
print("D2 (Taiji at 0 deg):", D2)
print("tr(D1) =", np.trace(D1))
print("tr(D2) =", np.trace(D2))
print("tr(D1^2) =", np.einsum('ab,ab->', D1, D1))
print("tr(D2^2) =", np.einsum('ab,ab->', D2, D2))

delta_x = const_lisa['centroid'] - const_taiji['centroid']
delta_r = np.linalg.norm(delta_x)
s_hat = delta_x / delta_r
print(f"\ndelta_r = {delta_r:.6e} m = {delta_r/1e9:.3f} km")

# JCAP gamma_I
def gamma_I_jcap(f):
    f_abs = np.abs(f)
    psi = 2.0 * np.pi * f_abs * delta_r / c
    j0 = spherical_bessel(0, psi)
    j2 = spherical_bessel(2, psi)
    j4 = spherical_bessel(4, psi)
    M = np.array([[14, -21, 0], [1, 0, 0], [60, -10, 35/2]])
    M_inv = np.linalg.inv(M)
    bI = (1.0 / 7.0) * M_inv @ np.array([j0, j2, j4])
    b0_I, b1_I, b2_I = bI
    tr = np.einsum('ab,ab->', D1, D2)
    D1_s = D1 @ s_hat
    D2_s = D2 @ s_hat
    term_s = np.dot(D1_s, D2_s)
    sD1s = np.dot(s_hat, D1 @ s_hat)
    sD2s = np.dot(s_hat, D2 @ s_hat)
    term_ss = sD1s * sD2s
    return -4.0 * (b0_I * tr + b1_I * term_s + b2_I * term_ss)

# Numerical sky integral (un-normalized)
ntheta, nphi = 200, 400
thetas = np.linspace(0, np.pi, ntheta)
phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
tG, pG = np.meshgrid(thetas, phis, indexing='ij')
dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)

th = np.stack([np.cos(tG)*np.cos(pG), np.cos(tG)*np.sin(pG), -np.sin(tG)])
ph = np.stack([-np.sin(pG), np.cos(pG), np.zeros_like(np.sin(pG))])

def response_func(a, b, D):
    result = np.zeros_like(a[0])
    for i in range(3):
        for j in range(3):
            result += D[i, j] * a[i] * b[j]
    return result

# Corrected response (theta^T D theta - phi^T D phi)
R1_plus = response_func(th, th, D1) - response_func(ph, ph, D1)
R1_cross = response_func(th, ph, D1)
R2_plus = response_func(th, th, D2) - response_func(ph, ph, D2)
R2_cross = response_func(th, ph, D2)

# Numerical sky integral of response product (un-normalized)
num_integral = np.sum((R1_plus * R2_plus + R1_cross * R2_cross) * dO)
print(f"\n=== Numerical sky integral (un-normalized) ===")
print(f"<R1+*R2+ + R1x*R2x> * 4pi = {num_integral:.10f}")

# Self-normalized numerical ORF
norm1 = np.sum((R1_plus**2 + R1_cross**2) * dO)
norm2 = np.sum((R2_plus**2 + R2_cross**2) * dO)
num_orf = num_integral / np.sqrt(norm1 * norm2)
print(f"Numerical self-norm ORF = {num_orf:.10f}")

# JCAP gamma_I at f=0
print(f"\n=== JCAP values ===")
gi_cross = gamma_I_jcap(0.001)
print(f"JCAP gamma_I (f=0.001) = {gi_cross:.12f}")
gi_cross0 = gamma_I_jcap(0.0)
print(f"JCAP gamma_I (f=0) = {gi_cross0:.12f}")

# JCAP auto values
M = np.array([[14, -21, 0], [1, 0, 0], [60, -10, 35/2]])
M_inv = np.linalg.inv(M)
b0_0, b1_0, b2_0 = (1.0/7.0) * M_inv @ np.array([1.0, 0.0, 0.0])
print(f"\nb-coefficients at f=0: b0={b0_0:.15e}, b1={b1_0:.15f}, b2={b2_0:.15f}")

tr11 = np.einsum('ab,ab->', D1, D1)
D1s = D1 @ s_hat
term_s11 = np.dot(D1s, D1s)
sD1s = np.dot(s_hat, D1 @ s_hat)
auto1_jcap = -4.0 * (b0_0 * tr11 + b1_0 * term_s11 + b2_0 * sD1s**2)

tr22 = np.einsum('ab,ab->', D2, D2)
D2s = D2 @ s_hat
term_s22 = np.dot(D2s, D2s)
sD2s = np.dot(s_hat, D2 @ s_hat)
auto2_jcap = -4.0 * (b0_0 * tr22 + b1_0 * term_s22 + b2_0 * sD2s**2)

print(f"JCAP auto1 (LISA) = {auto1_jcap:.12f}")
print(f"JCAP auto2 (Taiji) = {auto2_jcap:.12f}")
print(f"JCAP self-norm = {gi_cross0 / np.sqrt(auto1_jcap * auto2_jcap):.12f}")

# Numerical auto values
num_auto1 = np.sum((R1_plus**2 + R1_cross**2) * dO)
num_auto2 = np.sum((R2_plus**2 + R2_cross**2) * dO)
print(f"\nNumerical auto1 = {num_auto1:.10f}")
print(f"Numerical auto2 = {num_auto2:.10f}")

# Check ratio
print(f"\n=== Ratios ===")
ratio_cross = num_integral / gi_cross0
ratio_auto1 = num_auto1 / auto1_jcap
ratio_auto2 = num_auto2 / auto2_jcap
print(f"num_integral / JCAP_cross = {ratio_cross:.6f}")
print(f"num_auto1 / JCAP_auto1 = {ratio_auto1:.6f}")
print(f"num_auto2 / JCAP_auto2 = {ratio_auto2:.6f}")

# At f=0.001
gi_cross_1 = gamma_I_jcap(0.001)
num_int_1 = num_integral  # Transfer function T_iso ≈ 1 at low f
print(f"\n=== At f=0.001 Hz ===")
print(f"num_integral / JCAP_cross = {num_int_1 / gi_cross_1:.6f}")

# Check if the issue is coplanar enhancement
print(f"\n=== Coplanar enhancement analysis ===")
# For coplanar detector D2 = diag(1.5, 1.5, 0): what are the contractions?
# Isotropic: <R_plus^2> = 0.3 (from JCAP)
# Coplanar: actual sky average should be different
# The enhancement ratio is: num_auto2 / (auto2_jcap * (4pi))
# If all ratios are the same, then the scaling is consistent
