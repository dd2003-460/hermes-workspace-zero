"""Diagnostic: frequency dependence of Gamma^V to check if it's geometric or transfer function."""
import numpy as np
import importlib.util

spec = importlib.util.spec_from_file_location(
    "multi",
    "/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/11-multi-constellation-chiral-orf.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

Constellation = mod.Constellation
compute_cross_orf = mod.compute_cross_e_variable_orf
create_lisa = mod.create_lisa
create_taiji = mod.create_olc  # reuse for test

# Create constellations
lisa60 = Constellation('LISA_60', 2.5e9, inclination_rad=np.radians(60.0))
taiji0 = Constellation('Taiji_0', 2.5e9, inclination_rad=0.0)
taiji60 = Constellation('Taiji_60', 2.5e9, inclination_rad=np.radians(60.0))

print("=" * 70)
print("FREQUENCY SCAN: LISA(60) x Taiji(0) - Gamma^I and Gamma^V vs f")
print("=" * 70)
frequencies = [0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
for f in frequencies:
    # Inline computation to get frequency-dependent result
    ntheta, nphi = 32, 64
    tG = np.linspace(0, np.pi, ntheta)
    pG = np.linspace(0, 2 * np.pi, nphi)
    TG, PG = np.meshgrid(tG, pG, indexing='ij')
    dOmega = np.pi / (ntheta - 1) * 2 * np.pi / nphi

    a1_1, a2_1, a3_1, n1 = lisa60.get_detector_tensor_e()
    a1_2, a2_2, a3_2, n2 = taiji0.get_detector_tensor_e()
    arm_vecs_1 = [a1_1, a2_1, a3_1]
    arm_vecs_2 = [a1_2, a2_2, a3_2]

    R1p, R1x = mod.antenna_pattern_e_variable_universal(TG, PG, arm_vecs_1, n1, lisa60.L, 'interferometer')
    R2p, R2x = mod.antenna_pattern_e_variable_universal(TG, PG, arm_vecs_2, n2, taiji0.L, 'interferometer')

    # Recompute with frequency-specific T
    # The function above uses T implicitly via the transfer function - let me check
    # Actually the function signature doesn't take frequency; it uses L only
    # So T is evaluated at the default frequency encoded in the transfer function...
    # Wait, looking at antenna_pattern_e_variable_universal:
    # It calls taiji_transfer_function(np.ones_like(tG_a), L, transfer_cos_nu)
    # The transfer function takes (f, L, cos_nu) but here f is np.ones - meaning f=1 Hz? No.
    # taiji_transfer_function: beta = pi * |f| * L / c, where f = np.ones => f=1 Hz equivalent?
    # No, f = np.ones means every element = 1, so f is dimensionless "1" and beta = pi*1*L/c
    # This is weird. Let me check what the actual T values are.

    # Get T at frequency f
    nx = np.sin(TG)*np.cos(PG)
    ny = np.sin(TG)*np.sin(PG)
    nz = np.cos(TG)

    avg_arm1 = np.mean(arm_vecs_1, axis=0)
    cos_nu1 = nx*avg_arm1[0] + ny*avg_arm1[1] + nz*avg_arm1[2]
    avg_arm2 = np.mean(arm_vecs_2, axis=0)
    cos_nu2 = nx*avg_arm2[0] + ny*avg_arm2[1] + nz*avg_arm2[2]

    T1 = mod.taiji_transfer_function(np.ones_like(TG), f, cos_nu1)
    T2 = mod.taiji_transfer_function(np.ones_like(TG), f, cos_nu2)

    # Recompute R with proper frequency
    sqrt3 = np.sqrt(3.0)
    cross1 = np.cross(arm_vecs_1[0], n1)
    cross2 = np.cross(arm_vecs_1[1], n1)
    cross3 = np.cross(arm_vecs_1[2], n1)
    Dxy1 = (cross1[0]*arm_vecs_1[0][1] + cross2[0]*arm_vecs_1[1][1] + cross3[0]*arm_vecs_1[2][1]) / sqrt3
    Dxz1 = (cross1[0]*arm_vecs_1[0][2] + cross2[0]*arm_vecs_1[1][2] + cross3[0]*arm_vecs_1[2][2]) / sqrt3
    Dyz1 = (cross1[1]*arm_vecs_1[0][2] + cross2[1]*arm_vecs_1[1][2] + cross3[1]*arm_vecs_1[2][2]) / sqrt3

    th = np.array([np.cos(TG)*np.cos(PG), np.cos(TG)*np.sin(PG), -np.sin(TG)])
    ph = np.array([-np.sin(PG), np.cos(PG), np.zeros_like(PG, dtype=np.float64)])
    epp_xy = th[0]*th[1] - ph[0]*ph[1]
    epp_xz = th[0]*th[2] - ph[0]*ph[2]
    epp_yz = th[1]*th[2] - ph[1]*ph[2]
    ecx_xy = th[0]*ph[1] + ph[0]*th[1]
    ecx_xz = th[0]*ph[2] + ph[0]*th[2]
    ecx_yz = th[1]*ph[2] + ph[1]*th[2]

    geo_plus1 = 2.0*Dxy1*epp_xy + 2.0*Dxz1*epp_xz + 2.0*Dyz1*epp_yz
    geo_cross1 = 2.0*Dxy1*ecx_xy + 2.0*Dxz1*ecx_xz + 2.0*Dyz1*ecx_yz

    # Same for constellation 2
    cross1b = np.cross(arm_vecs_2[0], n2)
    cross2b = np.cross(arm_vecs_2[1], n2)
    cross3b = np.cross(arm_vecs_2[2], n2)
    Dxy2 = (cross1b[0]*arm_vecs_2[0][1] + cross2b[0]*arm_vecs_2[1][1] + cross3b[0]*arm_vecs_2[2][1]) / sqrt3
    Dxz2 = (cross1b[0]*arm_vecs_2[0][2] + cross2b[0]*arm_vecs_2[1][2] + cross3b[0]*arm_vecs_2[2][2]) / sqrt3
    Dyz2 = (cross1b[1]*arm_vecs_2[0][2] + cross2b[1]*arm_vecs_2[1][2] + cross3b[1]*arm_vecs_2[2][2]) / sqrt3

    geo_plus2 = 2.0*Dxy2*epp_xy + 2.0*Dxz2*epp_xz + 2.0*Dyz2*epp_yz
    geo_cross2 = 2.0*Dxy2*ecx_xy + 2.0*Dxz2*ecx_xz + 2.0*Dyz2*ecx_yz

    # With proper frequency-dependent T
    R1p_f = geo_plus1 * T1
    R1x_f = geo_cross1 * T1
    R2p_f = geo_plus2 * T2
    R2x_f = geo_cross2 * T2

    gamma_I_f = np.real(np.sum(np.conj(R1p_f) * R2p_f + np.conj(R1x_f) * R2x_f)) * dOmega / (4 * np.pi)
    gamma_V_f = np.real(np.sum(np.conj(R1p_f) * R2x_f - np.conj(R1x_f) * R2p_f)) * dOmega / (4 * np.pi)

    # Also compute auto ORFs for normalization
    auto1_f = np.real(np.sum(np.conj(R1p_f) * R1p_f + np.conj(R1x_f) * R1x_f)) * dOmega / (4 * np.pi)
    auto2_f = np.real(np.sum(np.conj(R2p_f) * R2p_f + np.conj(R2x_f) * R2x_f)) * dOmega / (4 * np.pi)
    norm = np.sqrt(auto1_f * auto2_f)

    print(f"  f={f:6.3f} Hz: Gamma^I={gamma_I_f:+12.8f}, Gamma^V={gamma_V_f:+12.8e}, "
          f"norm={norm:.6e}, normalized Gamma^V={gamma_V_f/norm:+12.8e}, |T1|={np.mean(np.abs(T1)):.6f}")

print("\n" + "=" * 70)
print("GEOMETRY CHECK: What are the detector tensor magnitudes?")
print("=" * 70)

# Compute detector tensor for each constellation
for name, const in [('LISA(60)', lisa60), ('Taiji(0)', taiji0), ('Taiji(60)', taiji60)]:
    a1, a2, a3, n = const.get_detector_tensor_e()
    print(f"\n  {name}:")
    print(f"    a1 = {a1}, |a1|={np.linalg.norm(a1):.6f}")
    print(f"    a2 = {a2}, |a2|={np.linalg.norm(a2):.6f}")
    print(f"    a3 = {a3}, |a3|={np.linalg.norm(a3):.6f}")
    print(f"    n = {n}, |n|={np.linalg.norm(n):.6f}")

    # Compute detector tensor components
    for i, a in enumerate([a1, a2, a3]):
        c = np.cross(a, n)
        print(f"    arm[{i}] x n = {c}, |cross|={np.linalg.norm(c):.6f}")

    # The Dxy, Dxz, Dyz magnitudes
    cross1 = np.cross(a1, n)
    cross2 = np.cross(a2, n)
    cross3 = np.cross(a3, n)
    Dxy = (cross1[0]*a1[1] + cross2[0]*a2[1] + cross3[0]*a3[1]) / sqrt3
    Dxz = (cross1[0]*a1[2] + cross2[0]*a2[2] + cross3[0]*a3[2]) / sqrt3
    Dyz = (cross1[1]*a1[2] + cross2[1]*a2[2] + cross3[1]*a3[2]) / sqrt3
    D_mag = np.sqrt(Dxy**2 + Dxz**2 + Dyz**2)
    print(f"    Dxy={Dxy:.6f}, Dxz={Dxz:.6f}, Dyz={Dyz:.6f}, |D|={D_mag:.6f}")

print("\n" + "=" * 70)
print("COMPARISON: LISA(60) x Taiji(0) vs LISA(60) x Taiji(60)")
print("=" * 70)
for const_name, const in [('Taiji(0)', taiji0), ('Taiji(60)', taiji60)]:
    gamma_I, gamma_V = compute_cross_orf(None, lisa60, const,
                                          const1_type='interferometer', const2_type='interferometer',
                                          ntheta=32, nphi=64)
    print(f"  LISA(60) x {const_name}: Gamma^I={gamma_I:+.8f}, Gamma^V={gamma_V:+.8e}")

print("\n" + "=" * 70)
print("KEY TEST: What if we use the same inclination but different rotation?")
print("=" * 70)
lisa60r = Constellation('LISA_60r', 2.5e9, inclination_rad=np.radians(60.0), rotation_phi=np.radians(45.0))
for const_name, const in [('Taiji(0)', taiji0), ('Taiji(0,zrot=45)', lisa60r)]:
    lisa_test = lisa60 if const_name == 'Taiji(0)' else lisa60r
    const2 = taiji0
    gamma_I, gamma_V = compute_cross_orf(None, lisa_test, const2,
                                          const1_type='interferometer', const2_type='interferometer',
                                          ntheta=32, nphi=64)
    auto1, _ = compute_cross_orf(None, lisa_test, lisa_test,
                                  const1_type='interferometer', const2_type='interferometer',
                                  ntheta=32, nphi=64)
    auto2, _ = compute_cross_orf(None, const2, const2,
                                  const1_type='interferometer', const2_type='interferometer',
                                  ntheta=32, nphi=64)
    norm = np.sqrt(auto1 * auto2)
    print(f"  {const_name}: Gamma^I={gamma_I:+.8f}, Gamma^V={gamma_V:+.8e}, "
          f"norm={norm:.6e}, norm_V={gamma_V/norm:+.8e}")
