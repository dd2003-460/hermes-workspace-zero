#!/usr/bin/env python3
"""Debug script to trace through the gamma_V and gamma_I computation."""
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

def cross_first_index(s_hat, D):
    eps = np.array([[[0, 0, 0], [0, 0, -1], [0, 1, 0]],
                    [[0, 0, 1], [0, 0, 0], [-1, 0, 0]],
                    [[0, -1, 0], [1, 0, 0], [0, 0, 0]]])
    w = np.einsum('ace,e,ab->cb', eps, s_hat, D)
    return w

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

# Check coplanarity and det(D)
for incl_name, incl in [('LISA 30°', LISA_INCLINATION), ('Taiji 0°', TAIJI_INCLINATION)]:
    const = make_triangle_constellation(incl_name, TAIJI_L, incl)
    D = compute_detector_tensor_dimensionless(const)
    print(f"\n=== {incl_name} ===")
    print(f"D =\n{D}")
    print(f"trace(D) = {np.trace(D):.4f}")
    print(f"det(D) = {np.linalg.det(D):.2e}")

# Full computation
const_lisa = make_triangle_constellation('LISA', LISA_L, LISA_INCLINATION,
                                          reference_position=np.array([0, 0, 0]))
const_taiji = make_triangle_constellation('Taiji', TAIJI_L, TAIJI_INCLINATION,
                                           reference_position=np.array([AU, 0, 0]))

f = 0.001
f_abs = np.abs(f)
delta_x = const_lisa['centroid'] - const_taiji['centroid']
delta_r = np.linalg.norm(delta_x)
psi = 2.0 * np.pi * f_abs * delta_r / c
s_hat = delta_x / delta_r

print(f"\n=== Parameters ===")
print(f"delta_x = {delta_x}")
print(f"delta_r = {delta_r}")
print(f"s_hat = {s_hat}")
print(f"psi = {psi}")

bv0 = (4.0 / 5.0) * spherical_bessel(1, psi)
bv1 = (-4.0 / 35.0) * spherical_bessel(3, psi)
print(f"\nb_V0 = {bv0}")
print(f"b_V1 = {bv1}")

D1 = compute_detector_tensor_dimensionless(const_lisa)
D2 = compute_detector_tensor_dimensionless(const_taiji)
w1 = cross_first_index(s_hat, D1)
w2 = cross_first_index(s_hat, D2)

D1_s = D1 @ s_hat
D2_s = D2 @ s_hat

term_1 = np.einsum('ac,ab,cb->', w1, D1, D2)
term_2 = np.einsum('ac,ab,cb->', w2, D2, D1)
term_3 = np.einsum('ac,a,c->', w1, D1_s, D2_s)
term_4 = np.einsum('ac,a,c->', w2, D2_s, D1_s)

print(f"\n=== Terms ===")
print(f"w1 =\n{w1}")
print(f"w2 =\n{w2}")
print(f"D1 @ s_hat = {D1_s}")
print(f"D2 @ s_hat = {D2_s}")
print(f"term_1 = {term_1}")
print(f"term_2 = {term_2}")
print(f"term_3 = {term_3}")
print(f"term_4 = {term_4}")

gamma_V = 4.0 * (bv0 * (term_1 + term_2) + bv1 * (term_3 + term_4))
print(f"\n=== Result ===")
print(f"gamma_V = {gamma_V}")

# Now check the chiral response numerically
print(f"\n=== Numerical chiral response (no spatial phase) ===")
thetas = np.linspace(0, np.pi, 30)
phis = np.linspace(0, 2*np.pi, 60, endpoint=False)
tG, pG = np.meshgrid(thetas, phis, indexing='ij')
dO = np.sin(tG) * (2*np.pi/60) * (np.pi/30)

th = np.stack([np.cos(tG)*np.cos(pG), np.cos(tG)*np.sin(pG), -np.sin(tG)])
ph = np.stack([-np.sin(pG), np.cos(pG), np.zeros_like(np.sin(pG))])
k_hat = np.stack([np.sin(tG)*np.cos(pG), np.sin(tG)*np.sin(pG), np.cos(tG)])

def response(theta, phi, D):
    result = np.zeros((th.shape[1], th.shape[2]))
    for i in range(3):
        for j in range(3):
            result += D[i, j] * theta[i, :, :] * phi[j, :, :]
    return result

R1_plus = response(th, th, D1)
R1_cross = response(th, ph, D1)
R2_plus = response(th, th, D2)
R2_cross = response(th, ph, D2)

# WITHOUT transfer functions
chiral_signal = R1_plus * R2_cross - R1_cross * R2_plus
auto_signal = R1_plus * R2_plus + R1_cross * R2_cross

print(f"Mean |R1_plus| = {np.mean(np.abs(R1_plus)):.4f}")
print(f"Mean |R1_cross| = {np.mean(np.abs(R1_cross)):.4f}")
print(f"Mean |R2_plus| = {np.mean(np.abs(R2_plus)):.4f}")
print(f"Mean |R2_cross| = {np.mean(np.abs(R2_cross)):.4f}")
print(f"Mean |chiral| = {np.mean(np.abs(chiral_signal)):.2e}")
print(f"Mean |auto| = {np.mean(np.abs(auto_signal)):.4f}")

# Integrate
norm1 = np.sum((np.abs(R1_plus)**2 + np.abs(R1_cross)**2) * dO)
norm2 = np.sum((np.abs(R2_plus)**2 + np.abs(R2_cross)**2) * dO)
print(f"\nnorm1 (auto1 without TF) = {norm1}")
print(f"norm2 (auto2 without TF) = {norm2}")

chiral_int = np.sum(chiral_signal * dO)
auto_int = np.sum(auto_signal * dO)
print(f"chiral integral = {chiral_int}")
print(f"auto integral = {auto_int}")
gamma_V_num_no_phase = chiral_int / np.sqrt(norm1 * norm2)
print(f"gamma_V numerical (no phase, no TF) = {gamma_V_num_no_phase}")

# Now with spatial phase
k_dot_delta = k_hat[0]*delta_x[0] + k_hat[1]*delta_x[1] + k_hat[2]*delta_x[2]
alpha = 2.0 * np.pi * f / c
bp = np.exp(-1j * alpha * k_dot_delta)
chiral_int_phase = np.sum(chiral_signal * bp * dO)
gamma_V_num_phase = chiral_int_phase / np.sqrt(norm1 * norm2)
print(f"gamma_V numerical (WITH phase, no TF) = {gamma_V_num_phase}")

# Now with transfer functions
beta1 = np.pi * np.abs(f) * const_lisa['L'] / c
beta2 = np.pi * np.abs(f) * const_taiji['L'] / c
T1 = np.sin(beta1) / beta1 * np.exp(-1j * beta1)
T2 = np.sin(beta2) / beta2 * np.exp(-1j * beta2)

R1_plus_tf = T1 * R1_plus
R1_cross_tf = T1 * R1_cross
R2_plus_tf = T2 * R2_plus
R2_cross_tf = T2 * R2_cross

chiral_tf = R1_plus_tf * R2_cross_tf - R1_cross_tf * R2_plus_tf
chiral_tf_int = np.sum(chiral_tf * dO)
norm1_tf = np.sum((np.abs(R1_plus_tf)**2 + np.abs(R1_cross_tf)**2) * dO)
norm2_tf = np.sum((np.abs(R2_plus_tf)**2 + np.abs(R2_cross_tf)**2) * dO)
print(f"\n=== WITH transfer functions ===")
print(f"norm1_tf = {norm1_tf}")
print(f"norm2_tf = {norm2_tf}")
print(f"chiral integral (with TF, no phase) = {chiral_tf_int}")
gamma_V_num_tf = chiral_tf_int / np.sqrt(norm1_tf * norm2_tf)
print(f"gamma_V numerical (WITH TF, no phase) = {gamma_V_num_tf}")

chiral_tf_phase = np.sum(chiral_tf * bp * dO)
gamma_V_num_tf_phase = chiral_tf_phase / np.sqrt(norm1_tf * norm2_tf)
print(f"gamma_V numerical (WITH TF, WITH phase) = {gamma_V_num_tf_phase}")

# Check M_inv bug for gamma_I
print(f"\n=== M_inv check ===")
M = np.array([[14, -21, 0], [1, 0, 0], [60, -10, 35/2]])
M_inv_wrong = np.array([[0, 1, 0], [2/3, 0, 7/15], [1/3, 0, -2/15]])
M_inv_correct = np.linalg.inv(M)
print(f"M_inv_wrong @ M =\n{M_inv_wrong @ M}")
print(f"M_inv_correct @ M =\n{M_inv_correct @ M}")

# Compute gamma_I with both
j0 = spherical_bessel(0, psi)
j2 = spherical_bessel(2, psi)
j4 = spherical_bessel(4, psi)
bI_wrong = (1.0 / 7.0) * M_inv_wrong @ np.array([j0, j2, j4])
bI_correct = (1.0 / 7.0) * M_inv_correct @ np.array([j0, j2, j4])
print(f"\nbI_wrong = {bI_wrong}")
print(f"bI_correct = {bI_correct}")

tr_D1D2 = np.einsum('ab,ab->', D1, D2)
D1_s2 = D1 @ s_hat
D2_s2 = D2 @ s_hat
term_s = np.dot(D1_s2, D2_s2)
sD1s = np.dot(s_hat, D1 @ s_hat)
sD2s = np.dot(s_hat, D2 @ s_hat)
term_ss = sD1s * sD2s

gamma_I_wrong = 4.0 * (bI_wrong[0] * tr_D1D2 + bI_wrong[1] * term_s + bI_wrong[2] * term_ss)
gamma_I_correct = 4.0 * (bI_correct[0] * tr_D1D2 + bI_correct[1] * term_s + bI_correct[2] * term_ss)
print(f"\ngamma_I_wrong = {gamma_I_wrong}")
print(f"gamma_I_correct = {gamma_I_correct}")

# Parity-even numerical
parity_even_int = np.sum(auto_signal * dO)
gamma_I_num = parity_even_int / np.sqrt(norm1 * norm2)
print(f"\ngamma_I numerical (no TF, no phase) = {gamma_I_num}")
