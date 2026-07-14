#!/usr/bin/env python3
"""
Deep follow-up: Chiral ORF as function of internal weights within a Michelson.

Key distinction:
- Weight ratio within Michelson: (w_a, w_b)
- If w_a = w_b → Gamma^V = 0 (proportionality preserved)
- If w_a = -w_b → Gamma^V != 0 (sensitive to sign of cos_nu, breaks mirror)
- If w_a != w_b (general) → continuous exploration

Meanwhile, weight ratios BETWEEN Michelsons (E-like, T-like) do NOT break zero.
"""
import numpy as np

c = 299792458.0

def olc_transfer_function(f, L, cos_nu):
    f = np.atleast_1d(f)
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - cos_nu
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

def orf_pair(all_link_thphi, L, w1, w2, ntheta=32, nphi=64):
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')
    dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)

    all_resp = []
    for th, ph in all_link_thphi:
        rp, rc = olc_link_response_grid(th, ph, L, tG, pG)
        all_resp.append((rp, rc))

    N = len(w1)
    M1p = sum(w1[i] * all_resp[i][0] for i in range(N))
    M1x = sum(w1[i] * all_resp[i][1] for i in range(N))
    M2p = sum(w2[i] * all_resp[i][0] for i in range(N))
    M2x = sum(w2[i] * all_resp[i][1] for i in range(N))

    corr_c = np.sum((M1p * M2x - M1x * M2p) * dO)
    corr_s = np.sum((M1p*M2p + M1x*M2x) * dO)

    auto1 = np.sum((M1p**2 + M1x**2) * dO)
    auto2 = np.sum((M2p**2 + M2x**2) * dO)
    denom = np.sqrt(np.abs(auto1) * np.abs(auto2))
    if denom < 1e-30:
        return 0.0, 0.0

    return np.real(corr_s / denom), np.real(corr_c / denom)

# ━━━ Equilateral triangle ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
f = 0.01
L = 2.5e9
side = 2.5e9
tri = np.array([[0,0,0], [side,0,0], [side/2, side*np.sqrt(3)/2, 0]])

link_thphi = []
for i, j in [(0,1), (1,0), (1,2), (2,1), (2,0), (0,2)]:
    th, ph = link_dir(tri[i], tri[j])
    link_thphi.append((th, ph))

# Fixed: M2 = M_Y with weights (0,0,1,1,0,0)
w2_y = [0, 0, 1, 1, 0, 0]

print("=" * 65)
print("Chiral ORF vs internal weight ratio in M_X")
print("=" * 65)
print(f"M_Y fixed weights: [0,0,1,1,0,0]")
print(f"{'w_X_internal (a,b)':<22s}  {'Ratio':>8s}  {'Gamma^I':>12s}  {'Gamma^V':>14s}  {'|Gamma^V|':>12s}")
print("  " + "-" * 72)

# Sweep weight ratio r = b/a from -1 to 1
ratios = np.linspace(-1.0, 1.0, 21)
for r in ratios:
    # w_X = (1, r, 0, 0, 0, 0)
    a = 1.0
    b = r
    w1_x = [a, b, 0, 0, 0, 0]
    gi, gv = orf_pair(link_thphi, L, w1_x, w2_y, ntheta=32, nphi=64)
    ratio_str = f"{r:.2f}" if abs(r - round(r)) > 0.01 else f"{round(r):.2f}"
    print(f"  ({a:.0f}, {b:.2f})         {ratio_str:>8s}  {np.real(gi):12.6f}  {np.real(gv):14.2e}  {np.abs(gv):12.2e}")

print()
print("Frequency dependence of (1,-1) asymmetric Michelson:")
print(f"{'f (mHz)':>10s}  {'Gamma^I':>12s}  {'Gamma^V':>14s}  {'|Gamma^V|':>12s}")
print("  " + "-" * 52)
for f_mHz in [0.1, 1.0, 3.0, 10.0, 30.0, 100.0]:
    f_hz = f_mHz / 1000.0
    L = 2.5e9
    w1_a = [1, -1, 0, 0, 0, 0]
    w2_y = [0, 0, 1, 1, 0, 0]
    gi, gv = orf_pair(link_thphi, L, w1_a, w2_y, ntheta=32, nphi=64)
    print(f"  {f_mHz:>10.1f}  {np.real(gi):12.6f}  {np.real(gv):14.2e}  {np.abs(gv):12.2e}")
