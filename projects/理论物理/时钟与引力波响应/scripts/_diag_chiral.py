"""Diagnostic: test various configs for nonzero Gamma^V."""
import sys
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
create_taiji = mod.create_taiji
create_olc = mod.create_olc

print("Test 1: LISA(i=60) x Taiji(i=0) same arm")
lisa = create_lisa()
taiji = create_taiji()

gI, gV = compute_cross_orf(None, lisa, taiji,
                           const1_type='interferometer', const2_type='interferometer',
                           ntheta=32, nphi=64)
print(f"  LISA(60) x Taiji(0): <G^I>={gI:.6f}, G^V={gV:.6e}")

print("\nTest 2: LISA x Taiji with z-rotation")
taiji_rot = Constellation('Taiji_rot', 2.5e9, inclination_rad=0.0, rotation_phi=np.radians(30.0))
gI, gV = compute_cross_orf(None, lisa, taiji_rot,
                           const1_type='interferometer', const2_type='interferometer',
                           ntheta=32, nphi=64)
print(f"  LISA(60) x Taiji_rot(0,30): <G^I>={gI:.6f}, G^V={gV:.6e}")

print("\nTest 3: Different arm length")
taiji_800 = Constellation('Taiji_800', 2.0e9, inclination_rad=0.0)
gI, gV = compute_cross_orf(None, lisa, taiji_800,
                           const1_type='interferometer', const2_type='interferometer',
                           ntheta=32, nphi=64)
print(f"  LISA(2.5) x Taiji_800(2.0): <G^I>={gI:.6f}, G^V={gV:.6e}")

print("\nTest 4: OLC(i=0) x Taiji(i=0)")
olc = create_olc()
gI, gV = compute_cross_orf(None, olc, taiji,
                           const1_type='olc', const2_type='interferometer',
                           ntheta=32, nphi=64)
print(f"  OLC(0) x Taiji(0): <G^I>={gI:.6f}, G^V={gV:.6e}")

print("\nTest 5: OLC(i=60) x Taiji(i=0)")
olc60 = Constellation('OLC_60', 2.5e9, inclination_rad=np.radians(60.0))
gI, gV = compute_cross_orf(None, olc60, taiji,
                           const1_type='olc', const2_type='interferometer',
                           ntheta=32, nphi=64)
print(f"  OLC(60) x Taiji(0): <G^I>={gI:.6f}, G^V={gV:.6e}")

print("\nTest 6: OLC(i=60, zrot=30) x Taiji(i=0)")
olc60r = Constellation('OLC_60r', 2.5e9,
                        inclination_rad=np.radians(60.0),
                        rotation_phi=np.radians(30.0))
gI, gV = compute_cross_orf(None, olc60r, taiji,
                           const1_type='olc', const2_type='interferometer',
                           ntheta=32, nphi=64)
print(f"  OLC(60,30) x Taiji(0): <G^I>={gI:.6f}, G^V={gV:.6e}")

print("\nTest 7: OLC(0) x OLC(0) same")
gI, gV = compute_cross_orf(None, olc, olc,
                           const1_type='olc', const2_type='olc',
                           ntheta=32, nphi=64)
print(f"  OLC(0) x OLC(0): <G^I>={gI:.6f}, G^V={gV:.6e}")

print("\nTest 8: LISA(i=60) x LISA_rot(i=60, zrot=30)")
lisa_rot = Constellation('LISA_rot', 2.5e9, inclination_rad=np.radians(60.0),
                          rotation_phi=np.radians(30.0))
gI, gV = compute_cross_orf(None, lisa, lisa_rot,
                           const1_type='interferometer', const2_type='interferometer',
                           ntheta=32, nphi=64)
print(f"  LISA(60) x LISA_rot(60,30): <G^I>={gI:.6f}, G^V={gV:.6e}")

print("\nTest 9: Taiji(i=0) x Taiji_rot(i=0, zrot=30)")
taiji_rot2 = Constellation('Taiji_rot2', 2.5e9, inclination_rad=0.0, rotation_phi=np.radians(45.0))
gI, gV = compute_cross_orf(None, taiji, taiji_rot2,
                           const1_type='interferometer', const2_type='interferometer',
                           ntheta=32, nphi=64)
print(f"  Taiji(0) x Taiji_rot(0,45): <G^I>={gI:.6f}, G^V={gV:.6e}")

print("\nTest 10: LISA(0) x Taiji(0) - same inclination")
lisa0 = Constellation('LISA_0', 2.5e9, inclination_rad=0.0)
gI, gV = compute_cross_orf(None, lisa0, taiji,
                           const1_type='interferometer', const2_type='interferometer',
                           ntheta=32, nphi=64)
print(f"  LISA(0) x Taiji(0): <G^I>={gI:.6f}, G^V={gV:.6e}")
