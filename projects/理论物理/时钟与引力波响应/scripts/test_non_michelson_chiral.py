#!/usr/bin/env python3
"""
Quick test: non-Michelson linear combinations of triangular OLC links.
Test whether E-like, T-like, and other weighted combinations give nonzero Gamma^V.

Theory: F_A(u) ∝ e_A^{ab} u_a u_b, and F_+/F_× = F_+(u)/F_×(u) depends only on u.
If all links in the combinations have the same u (or proportional F_+/F_×),
then any linear combination gives chiral factor = 0.

But different links have different u directions, so F_+/F_× varies.
Does this break the zero? Let's compute.
"""
import numpy as np

c = 299792458.0

def olc_transfer_function(f, L, cos_nu):
    f = np.atleast_1d(f)
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - np.abs(cos_nu)
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f) * L / c
    return prefac * sinc_v * phase

def olc_link_response_grid(theta_u, phi_u, L, tG, pG):
    nx = np.sin(tG)*np.cos(pG)
    ny = np.sin(tG)*np.sin(pG)
    nz = np.cos(tG)
    cos_nu = (nx*np.sin(theta_u)*np.cos(phi_u) +
              ny*np.sin(theta_u)*np.sin(phi_u) +
              nz*np.cos(theta_u))
    T = olc_transfer_function(np.ones_like(tG), L, cos_nu)

    ct, st = np.cos(tG), np.sin(tG)
    cp, sp = np.cos(pG), np.sin(pG)
    ux, uy, uz = np.sin(theta_u)*np.cos(phi_u), np.sin(theta_u)*np.sin(phi_u), np.cos(theta_u)
    th_x, th_y, th_z = ct*cp, ct*sp, -st
    ph_x, ph_y, ph_z = -sp, cp, 0.0

    R_plus = (th_x*ux)**2 + (th_y*uy)**2 + (th_z*uz)**2 - (ph_x*ux)**2 - (ph_y*uy)**2 - (ph_z*uz)**2
    R_cross = 2*(th_x*ux)*(ph_x*ux) + 2*(th_y*uy)*(ph_y*uy) + 2*(th_z*uz)*(ph_z*uz)
    return R_plus * T, R_cross * T

def link_dir(r_from, r_to):
    d = r_to - r_from
    d_norm = np.linalg.norm(d)
    ux, uy, uz = d[0]/d_norm, d[1]/d_norm, d[2]/d_norm
    theta = np.arccos(np.clip(uz, -1, 1))
    phi = np.arctan2(uy, ux)
    return theta, phi

def orf_for_combo(f, all_link_thphi, L, w1, w2, ntheta=32, nphi=64):
    """
    Compute (Gamma^I, Gamma^V) for two weighted combos.

    all_link_thphi: list of (theta, phi) for each link (6 links total)
    w1, w2: weight vectors of length 6
    """
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')
    dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)

    # Compute all link responses
    all_resp = []
    for th, ph in all_link_thphi:
        rp, rc = olc_link_response_grid(th, ph, L, tG, pG)
        all_resp.append((rp, rc))

    # Weighted combinations
    N = len(w1)
    M1p = sum(w1[i] * all_resp[i][0] for i in range(N))
    M1x = sum(w1[i] * all_resp[i][1] for i in range(N))
    M2p = sum(w2[i] * all_resp[i][0] for i in range(N))
    M2x = sum(w2[i] * all_resp[i][1] for i in range(N))

    # Chiral ORF
    chiral_factor = M1p * M2x - M1x * M2p
    corr_c = np.sum(chiral_factor * dO)

    # Standard ORF
    corr_s = np.sum((M1p*M2p + M1x*M2x) * dO)

    auto1 = np.sum((M1p**2 + M1x**2) * dO)
    auto2 = np.sum((M2p**2 + M2x**2) * dO)
    denom = np.sqrt(np.abs(auto1) * np.abs(auto2))
    if denom < 1e-30:
        return 0.0, 0.0

    return np.real(corr_s / denom), np.real(corr_c / denom)

# ━━━ Equilateral triangle ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
f = 0.01  # 10 mHz
L = 2.5e9  # 2.5 Gm
side = 2.5e9
tri = np.array([[0,0,0], [side,0,0], [side/2, side*np.sqrt(3)/2, 0]])

# 6 link directions
link_thphi = []
pairs = [(0,1), (1,0), (1,2), (2,1), (2,0), (0,2)]
names = ['12', '21', '23', '32', '31', '13']
for i, j in pairs:
    th, ph = link_dir(tri[i], tri[j])
    link_thphi.append((th, ph))

print("=" * 65)
print("Non-Michelson Linear Combinations Chiral ORF Test")
print("=" * 65)
print(f"f = {f} kHz, L = {L/1e9:.1f} Gm")
print()

# Weight vectors (6 links: 12, 21, 23, 32, 31, 13)
tests = {}

# Michelson-like combos
tests['(M_X, M_Y)'] = ([1,1,0,0,0,0], [0,0,1,1,0,0])
tests['(M_X, M_X)'] = ([1,1,0,0,0,0], [1,1,0,0,0,0])
tests['(M_X, M_Z)'] = ([1,1,0,0,0,0], [0,0,0,0,1,1])

# E-like: M_E = M_X - M_Y
tests['(M_E, M_X)'] = ([1,1,-1,-1,0,0], [1,1,0,0,0,0])
tests['(M_E, M_Y)'] = ([1,1,-1,-1,0,0], [0,0,1,1,0,0])
tests['(M_E, M_Z)'] = ([1,1,-1,-1,0,0], [0,0,0,0,1,1])
tests['(M_E, M_E)'] = ([1,1,-1,-1,0,0], [1,1,-1,-1,0,0])

# T-like: M_T = M_X + M_Y + M_Z
tests['(M_T, M_X)'] = ([1,1,1,1,1,1], [1,1,0,0,0,0])
tests['(M_T, M_Y)'] = ([1,1,1,1,1,1], [0,0,1,1,0,0])
tests['(M_T, M_Z)'] = ([1,1,1,1,1,1], [0,0,0,0,1,1])
tests['(M_T, M_E)'] = ([1,1,1,1,1,1], [1,1,-1,-1,0,0])
tests['(M_T, M_T)'] = ([1,1,1,1,1,1], [1,1,1,1,1,1])

# Unequal weights within a "Michelson"
tests['(M_X_2:1, M_Y)'] = ([2,1,0,0,0,0], [0,0,1,1,0,0])
tests['(M_X_1:2, M_Y)'] = ([1,2,0,0,0,0], [0,0,1,1,0,0])
tests['(M_X_1:-1, M_Y)'] = ([1,-1,0,0,0,0], [0,0,1,1,0,0])

# Non-symmetric combos
tests['(2M_X - M_Y, M_X + M_Y)'] = ([2,2,-1,-1,0,0], [1,1,1,1,0,0])

print(f"{'Pair':<28s}  {'<Gamma^I>':>12s}  {'<Gamma^V>':>14s}  {'|Gamma^V|':>12s}")
print("  " + "-" * 68)
for pair, (w1, w2) in tests.items():
    gi, gv = orf_for_combo(f, link_thphi, L, w1, w2, ntheta=32, nphi=64)
    print(f"  {pair:<26s}  {np.real(gi):12.6f}  {np.real(gv):14.2e}  {np.abs(gv):12.2e}")

print()
print("Key: nonzero |Gamma^V| for any non-Michelson combo?")
