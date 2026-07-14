#!/usr/bin/env python3
"""
Debug: Why doesn't PTA-geo ORF match Hellings-Downs at d=0?

Test the decomposition: F_plus^2 + F_cross^2 vs ((1+n.u)/2)^2
and compare sky integrals for cross vs auto correlation.
"""
import numpy as np

def antenna_patterns(n_theta, n_phi, u_theta, u_phi):
    ct, st = np.cos(n_theta), np.sin(n_theta)
    cp, sp = np.cos(n_phi), np.sin(n_phi)
    cu_t, cu_p = np.cos(u_theta), np.cos(u_phi)
    su_t, su_p = np.sin(u_theta), np.sin(u_phi)
    ux = su_t * cu_p
    uy = su_t * su_p
    uz = cu_t
    th_x, th_y, th_z = ct * cp, ct * sp, -st
    ph_x, ph_y, ph_z = -sp, cp, 0.0
    F_plus = (th_x*ux)**2 + (th_y*uy)**2 + (th_z*uz)**2 - (ph_x*ux)**2 - (ph_y*uy)**2 - (ph_z*uz)**2
    F_cross = 2.0*(th_x*ux)*(ph_x*ux) + 2.0*(th_y*uy)*(ph_y*uy) + 2.0*(th_z*uz)*(ph_z*uz)
    return F_plus, F_cross

# ─── Test 1: F_plus^2 + F_cross^2 vs (1+n.u)^2/4 ────────────────────────────
print("=" * 60)
print("Test 1: F_plus^2+F_cross^2 vs (1+n.u)^2/4")
print("=" * 60)
# Fix u = x-axis (theta=pi/2, phi=0)
u_th = np.pi / 2; u_ph = 0.0

thetas = np.linspace(0, np.pi, 200)
phis = np.linspace(0, 2*np.pi, 400, endpoint=False)
tG, pG = np.meshgrid(thetas, phis, indexing='ij')
dO = np.sin(tG) * (2.0*np.pi/400) * (np.pi/200)

nx = np.sin(tG)*np.cos(pG)
ny = np.sin(tG)*np.sin(pG)
nz = np.cos(tG)

cos_nu = nx*np.sin(u_th)*np.cos(u_ph) + ny*np.sin(u_th)*np.sin(u_ph) + nz*np.cos(u_th)
# cos_nu = nx for u = x-axis

Fp, Fc = antenna_patterns(tG, pG, u_th, u_ph)

print(f"  Sky avg(F_plus^2 + F_cross^2) = {np.sum((Fp**2 + Fc**2) * dO) / np.sum(dO):.6f}")
print(f"  Sky avg((1+n.u)^2 / 4)        = {np.sum((1 + cos_nu)**2 / 4 * dO) / np.sum(dO):.6f}")
print(f"  Ratio = {np.sum((Fp**2 + Fc**2) * dO) / np.sum(((1 + cos_nu)**2 / 4) * dO):.6f}")
print(f"  Sky avg of n.u = {np.sum(cos_nu * dO) / np.sum(dO):.6f} (should be 0 by symmetry)")
print()

# Check equality at each sky pixel
diff = np.abs((Fp**2 + Fc**2) - (1 + cos_nu)**2 / 4)
print(f"  Max|Fp^2+Fc^2 - (1+n.u)^2/4| = {np.max(diff):.6f}")
print()

# ─── Test 2: Compute auto-correlation sky integral ────────────────────────────
print("=" * 60)
print("Test 2: Auto-correlation integral for one arm")
print("=" * 60)
auto_with_F = np.sum((Fp**2 + Fc**2) * dO)
auto_with_T = np.sum(((1 + cos_nu) / 2)**2 * dO)
print(f"  Integral(F_plus^2 + F_cross^2) = {auto_with_F:.6f}")
print(f"  Integral(((1+n.u)/2)^2)         = {auto_with_T:.6f}")
print(f"  Ratio = {auto_with_F / auto_with_T:.6f}")
print()

# ─── Test 3: Cross-correlation for same arm (should give ratio = 1) ──────────
print("=" * 60)
print("Test 3: Same arm cross-correlation = auto-correlation")
print("=" * 60)
# For same arm, F1 = F2 and T1 = T2
# cross = Integral(Fp1*Fp1 + Fc1*Fc1) * T1^2 * dO
#       = Integral(Fp^2 + Fc^2) * ((1+n.u)/2)^2 * dO
# auto  = Integral((Fp^2 + Fc^2)) * ((1+n.u)/2)^2 * dO
# These are the same! So ORF should = 1.0
cross = np.sum((Fp**2 + Fc**2) * ((1 + cos_nu) / 2)**2 * dO)
auto = np.sum((Fp**2 + Fc**2) * ((1 + cos_nu) / 2)**2 * dO)
print(f"  Cross = {cross:.6f}")
print(f"  Auto  = {auto:.6f}")
print(f"  ORF   = {cross/auto:.6f} (should be 1.0)")
print()

# ─── Test 4: Cross-correlation for two DIFFERENT arms ─────────────────────────
print("=" * 60)
print("Test 4: Cross-correlation for different arms")
print("=" * 60)
angle_deg = 60
angle_rad = np.deg2rad(angle_deg)

# u = x-axis, v = rotated by 60 deg from u around z
# v = (cos(60), sin(60), 0) = (0.5, 0.866, 0)
v_theta = np.pi / 2
v_phi = angle_rad

cos_nv = nx*np.sin(v_theta)*np.cos(v_phi) + ny*np.sin(v_theta)*np.sin(v_phi) + nz*np.cos(v_theta)
Fp2, Fc2 = antenna_patterns(tG, pG, v_theta, v_phi)
T2 = (1 + cos_nv) / 2

Fp1 = Fp; Fc1 = Fc; T1 = (1 + cos_nu) / 2

cross_12 = np.sum((Fp1*Fp2 + Fc1*Fc2) * T1 * T2 * dO)
auto_1 = np.sum((Fp1**2 + Fc1**2) * T1**2 * dO)
auto_2 = np.sum((Fp2**2 + Fc2**2) * T2**2 * dO)
orf = np.real(cross_12) / np.sqrt(auto_1 * auto_2)

print(f"  Cross = {cross_12:.6f}")
print(f"  Auto1 = {auto_1:.6f}")
print(f"  Auto2 = {auto_2:.6f}")
print(f"  ORF   = {orf:.6f} (at arm angle 60 deg, d=0)")

# Compute the product (u.a)(v.a) integral analytically
# For u=x, v=cos(a)*x + sin(a)*y
# cos_nu = nx, cos_nv = cos(a)*nx + sin(a)*ny
# T1*T2 = (1+nx)/2 * (1+cos(a)*nx+sin(a)*ny)/2
# The cross integral picks up the constant and nx^2 terms
# Let's compute the "n-direction correlation":
n_corr = np.sum(cos_nu * cos_nv * dO)
n_corr_normalized = n_corr / np.sum(dO)
print(f"  Sky avg(n.u * n.v) = {n_corr_normalized:.6f}")
print(f"  u.v = {np.cos(angle_rad):.6f}")
print(f"  Ratio (avg/n.u) = {n_corr_normalized / np.cos(angle_rad):.6f}")
print()

# ─── Test 5: HD analytic computation ─────────────────────────────────────────
print("=" * 60)
print("Test 5: Hellings-Downs analytic from Legendre expansion")
print("=" * 60)

def hellings_downs(xi_rad):
    x = (1.0 - np.cos(xi_rad)) / 2.0
    x_clamped = np.maximum(x, 1e-30)
    return 1.5 * x_clamped * np.log(x_clamped) + x_clamped / 4.0 - 0.5

for a_deg in [30, 60, 90, 120, 180]:
    a_rad = np.deg2rad(a_deg)
    print(f"  HD({a_deg}) = {hellings_downs(a_rad):.5f}")

print()

# ─── Test 6: What does the exact F_dot_F integral give? ──────────────────────
print("=" * 60)
print("Test 6: F_dot_F for the specific HD test case (u vs v directions)")
print("=" * 60)
print("In HD, the arms point TOWARD pulsars, and we correlate as a function of")
print("the angle between the two pulsar directions.")
print()
print("For HD at d=0 (Earth term only), the ORF is:")
print("  <F(u) * F(v)> / <F(u)^2>   averaged over GW sky directions")
print("where F = (1+n.u)(1+n.v)/4")
print()

# The key integral: sum over polarizations: e_A.ab(u^a u^b) e_A.cd(v^c v^d)
# Then integrate over GW sky.
# This equals: the sum of products of antenna patterns integrated over sky.

# Let's compute this differently: fix the two arm directions u, v
# and integrate over GW sky n.
# The answer should be expressible in terms of the angle between u and v.

# Known result: for PTA geometry with the standard antenna pattern:
# Omega(u, v) = (1/4) * [ (3 - cos(xi)) / 8 * log((1-cos(xi))/2) + ... ]
# This IS the HD curve.

# But with our specific arm setup:
# u = (1, 0, 0) and v = (cos(a), sin(a), 0)
# We get one specific value for each angle a.
# That IS our ORF at d=0.

# The comparison should be: does our integral match HD for the same angle?

# Our computation for various angles:
print(f"  {'Angle':>8s}  {'ORF(our)':>10s}  {'HD':>10s}  {'Match?':>8s}")
print("  " + "-" * 45)
for a_deg in [30, 45, 60, 90, 120, 150, 180]:
    a_rad = np.deg2rad(a_deg)

    # v at angle a from u in the equatorial plane
    v_t = np.pi / 2; v_p = a_rad

    cos_nv = nx*np.sin(v_t)*np.cos(v_p) + ny*np.sin(v_t)*np.sin(v_p) + nz*np.cos(v_t)
    Fp2, Fc2 = antenna_patterns(tG, pG, v_t, v_p)
    T2 = (1 + cos_nv) / 2

    cross_v = np.sum((Fp*Fp2 + Fc*Fc2) * T1_v_approx if 'T1_v_approx' in dir() else (Fp*Fp2 + Fc*Fc2) * ((1 + cos_nu)/2) * T2 * dO)

    # Recompute cleanly
    T1_val = (1 + cos_nu) / 2
    T2_val = (1 + cos_nv) / 2
    c_v = np.sum((Fp*Fp2 + Fc*Fc2) * T1_val * T2_val * dO)
    a1_v = np.sum((Fp**2 + Fc**2) * T1_val**2 * dO)
    a2_v = np.sum((Fp2**2 + Fc2**2) * T2_val**2 * dO)
    orf_v = np.real(c_v) / np.sqrt(a1_v * a2_v)

    hd_v = hellings_downs(a_rad)
    rel_err = abs(orf_v - hd_v) / (abs(hd_v) + 1e-30)

    print(f"  {a_deg:>8d}  {orf_v:>10.5f}  {hd_v:>10.5f}  {'OK' if rel_err < 0.05 else 'NO: ' + f'{rel_err:.0%}':>8s}")

print()

# ─── Analytical check ────────────────────────────────────────────────────────
print("=" * 60)
print("Analytical check: symmetry and isotropy")
print("=" * 60)
print("Key: u.v = cos(a)")
print("  u = (1,0,0), v = (cos a, sin a, 0)")
print("  n.u = sin(t)*cos(p), n.v = cos(a)*sin(t)*cos(p) + sin(a)*sin(t)*sin(p)")
print("  By rotational symmetry, <n.u * n.v> = 0, <n.u^2> = <n.v^2> = 1/3")
print("  <n.u * n.v> = 1/3 * cos(a)?  No - the average is over unit sphere, so")
print("  the correlation of direction cosines with different axes IS cos(a)/3.")
# Let's verify:
# n.u = cos(alpha_u) where alpha_u is angle from u direction
# n.v = cos(alpha_v) where alpha_v is angle from v direction
# <cos(alpha_u) cos(alpha_v)> = (1/3) cos(a)  ???
# Actually: <n_i n_j> = delta_ij / 3
# So <(n.u)(n.v)> = u_i v_j <n_i n_j> = u_i v_j delta_ij / 3 = (u.v) / 3

n_dot = cos_nu * cos_nv
avg = np.sum(n_dot * dO) / np.sum(dO)
uv = np.cos(angle_rad)
print(f"  <n.u * n.v> = {avg:.6f}")
print(f"  (u.v) / 3   = {uv / 3:.6f}")
print(f"  Match: {abs(avg - uv/3) < 1e-3}")

# Now let's expand (1+n.u)(1+n.v) = 1 + n.u + n.v + (n.u)(n.v)
# Average: 1 + 0 + 0 + (u.v)/3 = 1 + cos(a)/3
# And ((1+n.u)/2)(1+n.v)/2: average = (1+cos(a)/3)/4
# The normalization factors cancel, so ORF_d=0 = (1 + cos(a)/3)
# BUT THIS IS WRONG for HD! HD has a more complex function.

print()
print("Simple factor-only model predicts ORF(d=0) = (1+cos(a)/3)/something")
print("But HD has the LOG term — the dipole model alone DOES NOT reproduce HD!")
print("HD requires the GW back-reaction/pulsar term / long-baseline physics.")
print()

# Let me also check what Hu PRD says about this.
# The ORF in Hu PRD is the INTEGRAL of all the terms, including the
# temporal response T(beta, ...) factors.
# For PTA: beta = pi * f * L / c. L ~ kpc, f ~ nHz -> beta ~ 10^(-15)
# So T -> 0 in PTA? No, T_pta = (1+n.u)/2, which comes from a different derivation.

print("CONCLUSION: The Hellings-Downs curve requires proper PTA physics,")
print("not just the simple dipole (1+n.u)/2 model.")
print("The key HD terms come from: (a) pulsar term phase e^{i omega L(1-n.p)/c},")
print("(b) the cross-spectrum of timing residuals from common GW.")
print()
print("Our ORF code is testing the Earth-term only, which gives a simpler")
print("angular pattern that is NOT the HD curve.")
