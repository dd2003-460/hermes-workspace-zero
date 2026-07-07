#!/usr/bin/env python3
"""
Test: Why Orlando R^V != 0 for LISA-Taiji cross-correlation.

Key insight: R^V = 0 for coplanar detectors with SAME arm orientation.
R^V != 0 when detectors have DIFFERENT orientations (due to different orbital positions).

Orlando's "non-planar network" means: different detectors at different orbital positions
=> different relative arm orientations in 3D space.
"""

import numpy as np

# ===== Sky grid =====
NTH = 180
NPH = 360
th = np.linspace(0, np.pi, NTH)
ph = np.linspace(0, 2*np.pi, NPH, endpoint=False)
TH, PH = np.meshgrid(th, ph, indexing='ij')
dOmega = np.sin(TH) * (2*np.pi/NPH) * (np.pi/NTH)

# ===== Polarization basis =====
cos_t = np.cos(TH)
sin_t = np.sin(TH)
cos_p = np.cos(PH)
sin_p = np.sin(PH)

U_hat = np.stack([cos_t*cos_p, cos_t*sin_p, -sin_t], axis=0)
V_hat = np.stack([-sin_p, cos_p, np.zeros_like(TH)], axis=0)
K_hat = np.stack([np.sin(TH)*np.cos(PH), np.sin(TH)*np.sin(PH), np.cos(TH)], axis=0)

# ===== Detector arms (equilateral triangle) =====
base_arms = [
    np.array([1.0, 0.0, 0.0]),
    np.array([-0.5, np.sqrt(3)/2, 0.0]),
    np.array([-0.5, -np.sqrt(3)/2, 0.0]),
]

# ===== Rotation matrices =====
def rotate_around_x(arms, alpha):
    ca, sa = np.cos(alpha), np.sin(alpha)
    return [np.array([a[0], ca*a[1]-sa*a[2], sa*a[1]+ca*a[2]]) for a in arms]

def rotate_around_y(arms, beta):
    cb, sb = np.cos(beta), np.sin(beta)
    return [np.array([cb*a[0]+sb*a[2], a[1], -sb*a[0]+cb*a[2]]) for a in arms]

def rotate_around_z(arms, gamma):
    cg, sg = np.cos(gamma), np.sin(gamma)
    return [np.array([cg*a[0]-sg*a[1], sg*a[0]+cg*a[1], a[2]]) for a in arms]

# ===== Chiral antenna pattern =====
def chiral_antenna(arm1, arm2):
    a1 = arm1[0]*U_hat[0] + arm1[1]*U_hat[1] + arm1[2]*U_hat[2]
    b1 = arm1[0]*V_hat[0] + arm1[1]*V_hat[1] + arm1[2]*V_hat[2]
    a2 = arm2[0]*U_hat[0] + arm2[1]*U_hat[1] + arm2[2]*U_hat[2]
    b2 = arm2[0]*V_hat[0] + arm2[1]*V_hat[1] + arm2[2]*V_hat[2]
    GR1 = (a1 + 1j*b1)**2 / 4.0
    GL1 = (a1 - 1j*b1)**2 / 4.0
    GR2 = (a2 + 1j*b2)**2 / 4.0
    GL2 = (a2 - 1j*b2)**2 / 4.0
    return (GR1 - GR2), (GL1 - GL2)

# ===== Sky-averaged response =====
def sky_avg_response(detector1_arms, detector2_arms):
    """Compute R^I and R^V for cross-correlation between two detectors."""
    GR1 = [chiral_antenna(detector1_arms[i], detector1_arms[(i+1)%3])[0] for i in range(3)]
    GL1 = [chiral_antenna(detector1_arms[i], detector1_arms[(i+1)%3])[1] for i in range(3)]
    GR2 = [chiral_antenna(detector2_arms[i], detector2_arms[(i+1)%3])[0] for i in range(3)]
    GL2 = [chiral_antenna(detector2_arms[i], detector2_arms[(i+1)%3])[1] for i in range(3)]

    total_RI = 0.0
    total_RV = 0.0
    pairwise = []

    for i in range(3):
        for j in range(3):
            RR = GR1[i] * np.conj(GR2[j])
            RL = GL1[i] * np.conj(GL2[j])
            RI = np.real((RR + RL) / 2.0)
            RV = np.real((RR - RL) / 2.0)
            int_RI = np.sum(RI * dOmega) / (4*np.pi)
            int_RV = np.sum(RV * dOmega) / (4*np.pi)
            total_RI += int_RI
            total_RV += int_RV
            pairwise.append((int_RI, int_RV))

    return total_RI / 9.0, total_RV / 9.0, pairwise

# ===== Tests =====
f_test = 0.01  # 10 mHz
k_omega = 2 * np.pi * f_test / 3e8
L_LISA = 2.5e9
D = L_LISA  # Taiji displaced along x by 1*L_LISA

print("=" * 70)
print("1. IDENTICAL orientations (both in xy-plane, arms aligned)")
print("   => R^V should be 0 (same mirror plane)")
print("=" * 70)
RI, RV, pairs = sky_avg_response(base_arms, base_arms)
print(f"   R^I = {RI:.8f}, R^V = {RV:.12f}")
for i, (ri, rv) in enumerate(pairs):
    if abs(rv) > 1e-15:
        print(f"     Pair {i}: R^I={ri:.8f}, R^V={rv:.12f}")

print("\n" + "=" * 70)
print("2. ROTATED Taiji: 120° around z (different arm orientations)")
print("   => R^V may be nonzero (different mirror planes)")
print("=" * 70)
taiji_z = rotate_around_z(base_arms, np.pi/3)  # 60° rotation
RI, RV, pairs = sky_avg_response(base_arms, taiji_z)
print(f"   R^I = {RI:.8f}, R^V = {RV:.12f}")
for i, (ri, rv) in enumerate(pairs):
    if abs(rv) > 1e-8:
        print(f"     Pair {i}: R^I={ri:.8f}, R^V={rv:.12f}")

print("\n" + "=" * 70)
print("3. TILTED Taiji: 60° around x-axis")
print("   => Non-planar network (different orbital planes)")
print("=" * 70)
taiji_x = rotate_around_x(base_arms, np.pi/3)
RI, RV, pairs = sky_avg_response(base_arms, taiji_x)
print(f"   R^I = {RI:.8f}, R^V = {RV:.12f}")
for i, (ri, rv) in enumerate(pairs):
    if abs(rv) > 1e-8:
        print(f"     Pair {i}: R^I={ri:.8f}, R^V={rv:.12f}")

print("\n" + "=" * 70)
print("4. TILTED 30° around x-axis")
print("=" * 70)
taiji_30 = rotate_around_x(base_arms, np.pi/6)
RI, RV, pairs = sky_avg_response(base_arms, taiji_30)
print(f"   R^I = {RI:.8f}, R^V = {RV:.12f}")
for i, (ri, rv) in enumerate(pairs):
    if abs(rv) > 1e-8:
        print(f"     Pair {i}: R^I={ri:.8f}, R^V={rv:.12f}")

print("\n" + "=" * 70)
print("5. SELF-correlations (should all be R^V = 0)")
print("=" * 70)
RI, RV, _ = sky_avg_response(base_arms, base_arms)
print(f"   Self: R^I = {RI:.8f}, R^V = {RV:.12f}")

print("\n" + "=" * 70)
print("6. Phase factor effect: coplanar with exp(i*k.D) term")
print("=" * 70)

# With phase factor
def sky_avg_response_with_phase(detector1_arms, detector2_arms, D_vec):
    """Cross-correlation with spatial phase factor."""
    GR1 = [chiral_antenna(detector1_arms[i], detector1_arms[(i+1)%3])[0] for i in range(3)]
    GL1 = [chiral_antenna(detector1_arms[i], detector1_arms[(i+1)%3])[1] for i in range(3)]
    GR2 = [chiral_antenna(detector2_arms[i], detector2_arms[(i+1)%3])[0] for i in range(3)]
    GL2 = [chiral_antenna(detector2_arms[i], detector2_arms[(i+1)%3])[1] for i in range(3)]

    # Phase factor: exp(2pi i k . D_vec)
    phase = k_omega * (D_vec[0]*K_hat[0] + D_vec[1]*K_hat[1] + D_vec[2]*K_hat[2])

    total_RI = 0.0
    total_RV = 0.0
    pairwise = []

    for i in range(3):
        for j in range(3):
            RR = GR1[i] * np.conj(GR2[j]) * np.exp(1j * phase)
            RL = GL1[i] * np.conj(GL2[j]) * np.exp(1j * phase)
            RI = np.real((RR + RL) / 2.0)
            RV = np.real((RR - RL) / 2.0)
            int_RI = np.sum(RI * dOmega) / (4*np.pi)
            int_RV = np.sum(RV * dOmega) / (4*np.pi)
            total_RI += int_RI
            total_RV += int_RV
            pairwise.append((int_RI, int_RV))

    return total_RI / 9.0, total_RV / 9.0, pairwise

# Coplanar, same orientation, with phase
D_vec = np.array([L_LISA, 0, 0])
RI, RV, pairs = sky_avg_response_with_phase(base_arms, base_arms, D_vec)
print(f"   Coplanar, same arms, D = {D_vec[0]/1e9:.1f} Gm:")
print(f"   R^I = {RI:.8f}, R^V = {RV:.12f}")

# Coplanar, rotated, with phase
taiji_rot = rotate_around_z(base_arms, np.pi/3)
RI, RV, pairs = sky_avg_response_with_phase(base_arms, taiji_rot, D_vec)
print(f"   Coplanar, 60° z-rot, D = {D_vec[0]/1e9:.1f} Gm:")
print(f"   R^I = {RI:.8f}, R^V = {RV:.12f}")

# 3D non-planar, with phase
taiji_tilt = rotate_around_x(base_arms, np.pi/3)
RI, RV, pairs = sky_avg_response_with_phase(base_arms, taiji_tilt, D_vec)
print(f"   60° x-tilt (non-planar), D = {D_vec[0]/1e9:.1f} Gm:")
print(f"   R^I = {RI:.8f}, R^V = {RV:.12f}")
