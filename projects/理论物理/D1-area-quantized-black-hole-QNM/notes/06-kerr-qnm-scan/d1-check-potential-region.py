#!/usr/bin/env python3
"""
Detailed analysis: compute the local 'effective frequency' by integrating
in two steps and comparing the actual solution to exp(+/- i omega r*).
"""
import numpy as np

M = 1.0

def r_from_rstar(rs):
    r = max(rs * 0.5 + M, 2.5)
    for _ in range(30):
        f = r + 2*M*np.log(r/(2*M) - 1) - rs
        df = 1 + 2*M/(r - 2*M)
        if abs(df) < 1e-15: break
        r = r - f/df
        if r <= 2.0*M: r = 2.0*M + 1e-10
        if abs(f) < 1e-14: break
    return max(r, 2.0001)

def V(r, l, c):
    return (1 - 2*M/r)*(l*(l+1)/r**2 - c*M/r**3)

# Compute V as function of r* for reference
print("Potential V(r*) for c=6, l=2:")
for rs in [-50, -20, -10, -5, -1, 0, 1, 5, 10, 20, 50, 80]:
    r = r_from_rstar(rs)
    v = V(r, 2, 6)
    # Local frequency: omega_loc^2 = omega^2 - V
    w = complex(0.548, -0.071)
    omega_loc_sq = w**2 - v
    if omega_loc_sq.real > 0:
        omega_loc = np.sqrt(omega_loc_sq)
    else:
        omega_loc = 1j * np.sqrt(-omega_loc_sq)
    print(f"  r*={rs:4d}: r={r:7.3f}, V={v:8.6f}, sqrt(omega^2-V)={omega_loc.real:.4f}+{omega_loc.imag:.4f}i")

print("\n\nPotential V(r*) for c=2, l=2:")
for rs in [-50, -20, -10, -5, -1, 0, 1, 5, 10, 20, 50, 80]:
    r = r_from_rstar(rs)
    v = V(r, 2, 2)
    w = complex(0.37367, -0.08896)
    omega_loc_sq = w**2 - v
    try:
        omega_loc = np.sqrt(omega_loc_sq)
    except:
        omega_loc = 1j * np.sqrt(-omega_loc_sq)
    print(f"  r*={rs:4d}: r={r:7.3f}, V={v:8.6f}, sqrt(omega^2-V)={omega_loc.real:.4f}+{omega_loc.imag:.4f}i")

print("\n\nTest: integrate from r*=100 to r*=0 and check the phase.")
print("At r*=100, V is ~0. Solution should be exp(+i*omega*r*) = exp(-i*omega*(-100))...")

w = complex(0.37367, -0.08896)
rstar_start = 100.0
rstar_end = 0.0
N_steps = 8000

dr = (rstar_end - rstar_start) / N_steps
ps = np.exp(1j*w*rstar_start)  # outgoing
dps = 1j*w*ps

rs_grid = np.linspace(rstar_start, rstar_end, 101)
rs_idx = 0

for i in range(N_steps):
    rs = rstar_start + i*dr
    r = r_from_rstar(rs)
    Vr = V(r, 2, 6)
    h = dr

    k1_y = dps; k1_d = -(w**2 - Vr)*ps
    rm = r_from_rstar(rs+h/2); Vm = V(rm, 2, 6)
    k2_y = dps+h/2*k1_d; k2_d = -(w**2-Vm)*(ps+h/2*k1_y)
    k3_y = dps+h/2*k2_d; k3_d = -(w**2-Vm)*(ps+h/2*k2_y)
    re = r_from_rstar(rs+h); Ve = V(re, 2, 6)
    k4_y = dps+h*k3_d; k4_d = -(w**2-Ve)*(ps+h*k3_y)

    ps += h/6*(k1_y+2*k2_y+2*k3_y+k4_y)
    dps += h/6*(k1_d+2*k2_d+2*k3_d+k4_d)

    # Check log derivative at key points
    if rs_idx < len(rs_grid) and rs >= rs_grid[rs_idx]:
        ln = dps/ps if abs(ps) > 1e-300 else 1e50
        print(f"  r*={int(rs):3d}: |psi|={abs(ps):8.3e}, lnpsi={ln.real:6.4f}+{ln.imag:6.4f}i, exp(-i*w*{rs})=exp(?")
        rs_idx += 1

    # Periodic renormalization
    if abs(ps) > 1e80:
        ps /= abs(ps)
        dps /= abs(ps)

# Now try with higher precision: integrate only where V≈0 (r* > 20)
print(f"\n--- High-precision check in V≈0 region ---")
w = complex(0.37367, -0.08896)
# From r*=80 to r*=20
rstar_start2 = 80.0
rstar_end2 = 20.0
N_steps2 = 6000

ps2 = np.exp(1j*w*rstar_start2)
dps2 = 1j*w*ps2
dr2 = (rstar_end2 - rstar_start2) / N_steps2

for i in range(N_steps2):
    rs = rstar_start2 + i*dr2
    r = r_from_rstar(rs)
    Vr = V(r, 2, 6)
    h = dr2

    k1_y = dps2; k1_d = -(w**2 - Vr)*ps2
    rm = r_from_rstar(rs+h/2); Vm = V(rm, 2, 6)
    k2_y = dps2+h/2*k1_d; k2_d = -(w**2-Vm)*(ps2+h/2*k1_y)
    k3_y = dps2+h/2*k2_d; k3_d = -(w**2-Vm)*(ps2+h/2*k2_y)
    re = r_from_rstar(rs+h); Ve = V(re, 2, 6)
    k4_y = dps2+h*k3_d; k4_d = -(w**2-Ve)*(ps2+h*k3_y)

    ps2 += h/6*(k1_y+2*k2_y+2*k3_y+k4_y)
    dps2 += h/6*(k1_d+2*k2_d+2*k3_d+k4_d)

print(f"  At r*={rstar_end2}: |psi|={abs(ps2):.6e}, lnpsi={((dps2/ps2).real):.4f}+{((dps2/ps2).imag):.4f}i")
print(f"  Expected: if V=0, lnpsi should be i*omega = {w.real:.4f}+{w.imag:.4f}i (or close to it)")

# Now compare with expected value from pure oscillatory behavior
# In the region V<<w^2, the solution behaves like exp(+/- i*omega*r*)
# With w = 0.374 - 0.089i and r*=20:
# exp(+iw*20) = exp(i*0.374*20) * exp(0.089*20) = exp(7.48i) * exp(1.78)
# This GROWS exponentially! But the actual integral doesn't grow,
# suggesting there's another mode that cancels or dominates.

# The key question: does the integration produce the outgoing mode
# or does it mix in the incoming mode?
print(f"\n--- Mixing analysis ---")
# Compare the amplitude growth rate
# If only outgoing mode: |psi(r*)| ~ exp(-Im(w)*r*) = exp(0.089*r*)
# At r*=80: |psi| = exp(0.089*80) = exp(7.12) ~ 1240
# At r*=20: |psi| = exp(0.089*20) = exp(1.78) ~ 5.9
# Ratio: 1240/5.9 ~ 210

# If incoming mode: |psi(r*)| ~ exp(Im(w)*r*) = exp(-0.089*r*)
# At r*=80: exp(-7.12) ~ 0.0008
# At r*=20: exp(-1.78) ~ 0.17
# Ratio: 0.17/0.0008 ~ 210 (inverse)

# At r*=80, the pure outgoing gives |psi| = 1 (if we normalize the exponential)
# At r*=20, the outgoing grows to ~210 (due to exp(7.12-1.78) = exp(5.34))

# But wait, we integrate from 80 BACKWARD to 20, so:
# Outgoing: |psi(80)| = 1, |psi(20)| = exp(5.34) = 209

# Let's check:
expected_ratio = np.exp(5.34)  # This should match |psi(20)|/|psi(80)| for outgoing
print(f"  Expected outgoing ratio |psi(20)|/|psi(80)| = {expected_ratio:.2f}")
print(f"  |psi(80)| was normalized to 1")

# But wait - we initialize with psi = exp(i*w*80), which already has phase exp(29.9i)
# Let me normalize
actual_ps2_at_20 = ps2  # this was integrated FROM r*=80 TO r*=20

# The integration direction is: start at r*=80, go toward r*=20
# So dr = (20 - 80) / N_steps2 = -60/N_steps2 < 0
# Actually I have dr negative... but I integrate rs = rstar_start + i*dr where i goes 0 to N_steps
# When dr < 0, rs goes from 80 DOWN to 20. So the loop is correct (going backward).

print(f"  Actual |psi(20)| = {abs(actual_ps2_at_20):.3e} (expected ~{expected_ratio:.3f})")

print("\nDone")
