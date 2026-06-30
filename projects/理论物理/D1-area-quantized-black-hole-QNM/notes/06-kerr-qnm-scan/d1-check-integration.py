#!/usr/bin/env python3
"""Diagnostic: check the integration by comparing to analytical solutions."""
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

def shoot_test(w, l, c, N=10000, start=-50.0, dir=1):
    """Shoot from boundary. At r* near ±infinity (V=0), check if solution
    matches exp(+-i*w*r*)."""
    rs_end = 0.0
    dr = (rs_end - start) / N

    # Set BC
    ps = np.exp(-1j*w*start)  # incoming BC
    dps = -1j*w*ps
    h = dr

    # Step 0: first RK4 step to compute V at rstar=0 as well
    # Track where we stop
    for i in range(N):
        rs = start + i*dr
        r = r_from_rstar(rs)
        Vr = V(r, l, c)

        k1_y = dps; k1_d = -(w**2 - Vr)*ps

        rm = r_from_rstar(rs+h/2); Vm = V(rm, l, c)
        k2_y = dps+h/2*k1_d; k2_d = -(w**2-Vm)*(ps+h/2*k1_y)

        k3_y = dps+h/2*k2_d; k3_d = -(w**2-Vm)*(ps+h/2*k2_y)

        re = r_from_rstar(rs+h); Ve = V(re, l, c)
        k4_y = dps+h*k3_d; k4_d = -(w**2-Ve)*(ps+h*k3_y)

        ps += h/6*(k1_y+2*k2_y+2*k3_y+k4_y)
        dps += h/6*(k1_d+2*k2_d+2*k3_d+k4_d)

    return ps, dps

# Test: for V=0 (constant), the ODE is psi'' + w^2*psi = 0
# Solution: psi = exp(i*w*r*) or exp(-i*w*r*)
# The solution from r*=-50 should be psi(-50+L) = exp(-i*w*L)*psi(-50)
# where L is the distance traveled in r* space.

# Actually, if V=0 exactly (which happens at r=2M → r*=-∞), the solution is exp(-i*w*r*).
# When we start at r*=-50 and integrate to r*=0 (distance L=50), the analytical solution is:
# psi(r*=0) = exp(-i*w*0) = 1 (normalized to psi(-50) = exp(i*w*50) → actually:

# At horizon BC: psi(r*=-50) = exp(-i*w*(-50)) = exp(i*w*50)
# At r*=0: psi(0) = exp(-i*w*0) * psi(-50) = psi(-50) * exp(-i*w*50)? No...
# The ODE solution from -50: psi(r*) = psi(-50) * exp(-i*w*(r*+50))
# At r*=0: psi(0) = psi(-50) * exp(-i*w*50) = exp(i*w*50) * exp(-i*w*50) = exp(0) = 1

# Similarly, dpsi/dr* = -i*w*psi, so dpsi(0) = -i*w

# Test this: integrate with V≈0 (r=large → r*=large → can't integrate to horizon)
# Actually let's test with a HIGH r value where V is small
# At r=100, V ≈ 0 for any l, c
# r*(100) ≈ 100 + 2*ln(100/2) ≈ 100 + 2*3 ≈ 106

# Instead, test from r*=106 to r*=110 (pure vacuum where V=0):
w_test = 0.37367 - 0.08896j
rstar_test_start = 106.0
rstar_test_end = 110.0
N_test = 40

# At V=0, solution should be exp(-i*w*(r* - rstar_start))
psi0_num = np.exp(1j*w_test*rstar_test_start)  # outgoing
dpsi0_num = 1j*w_test*psi0_num

# Integrate from 106 to 110
r = r_from_rstar(rstar_test_start)
Vr = V(r, 2, 6)
print(f"  At r*={rstar_test_start}: r={r:.4f}, V={Vr:.8f}")
print(f"  V is negligible: {abs(Vr):.8e}")

# Integrate forward
h = (rstar_test_end - rstar_test_start) / N_test
ps = psi0_num
dps = dpsi0_num

for i in range(N_test):
    rs = rstar_test_start + i*h
    r = r_from_rstar(rs)
    Vr = V(r, 2, 6)
    k1_y = dps; k1_d = -(w_test**2 - Vr)*ps
    rm = r_from_rstar(rs+h/2); Vm = V(rm, 2, 6)
    k2_y = dps+h/2*k1_d; k2_d = -(w_test**2-Vm)*(ps+h/2*k1_y)
    k3_y = dps+h/2*k2_d; k3_d = -(w_test**2-Vm)*(ps+h/2*k2_y)
    re = r_from_rstar(rs+h); Ve = V(re, 2, 6)
    k4_y = dps+h*k3_d; k4_d = -(w_test**2-Ve)*(ps+h*k3_y)
    ps += h/6*(k1_y+2*k2_y+2*k3_y+k4_y)
    dps += h/6*(k1_d+2*k2_d+2*k3_d+k4_d)

psi_analytic = np.exp(1j*w_test*rstar_test_end)
dpsi_analytic = 1j*w_test*psi_analytic

print(f"\n  r*={rstar_test_end}:")
print(f"    Numerical:  psi={ps:.6e}, dpsi={dps:.6e}")
print(f"    Analytic:   psi={psi_analytic:.6e}, dpsi={dpsi_analytic:.6e}")
print(f"    Error psi:  {abs(ps-psi_analytic):.6e}")
print(f"    Error dpsi: {abs(dps-dpsi_analytic):.6e}")

# Test: for purely outgoing wave at infinity (V=0), log deriv should be +iw
# And check at r*=0 what happens when we integrate from infinity

# Now test: integrate from infinity outward
print(f"\n--- Check from infinity to r*=0 ---")
for omega_test in [0.37367-0.08896j, 0.548-0.071j]:
    N = 8000
    rs_inf = 80.0
    dr = (0.0 - rs_inf) / N

    ps = np.exp(1j*omega_test*rs_inf)  # outgoing BC
    dps = 1j*omega_test*ps

    for i in range(N):
        rs = rs_inf + i*dr
        r = r_from_rstar(rs)
        Vr = V(r, 2, 6)
        h = dr

        k1_y = dps; k1_d = -(omega_test**2 - Vr)*ps

        rm = r_from_rstar(rs+h/2); Vm = V(rm, 2, 6)
        k2_y = dps+h/2*k1_d; k2_d = -(omega_test**2-Vm)*(ps+h/2*k1_y)
        k3_y = dps+h/2*k2_d; k3_d = -(omega_test**2-Vm)*(ps+h/2*k2_y)
        re = r_from_rstar(rs+h); Ve = V(re, 2, 6)
        k4_y = dps+h*k3_d; k4_d = -(omega_test**2-Ve)*(ps+h*k3_y)

        ps += h/6*(k1_y+2*k2_y+2*k3_y+k4_y)
        dps += h/6*(k1_d+2*k2_d+2*k3_d+k4_d)

    if abs(ps) < 1e-300:
        print(f"  omega={omega_test}: psi={ps} (denormalized or overflow)")
        continue

    ln = dps / ps
    expected_ln_inf = 1j*omega_test  # pure outgoing at infinity
    # But at r*=0, there's a potential, so ln ≈?

    print(f"  omega={omega_test.real:.3f}+{omega_test.imag:.3f}i:")
    print(f"    |psi| = {abs(ps):.6e}, lnpsi = {ln.real:.4f}+{ln.imag:.4f}i")

# Check what psi(r*=-50) should be vs what we get
print(f"\n--- Horizon side check ---")
for omega_test in [0.37367-0.08896j]:
    N = 5000
    rs_hor = -50.0
    dr = (0.0 - rs_hor) / N

    ps = np.exp(-1j*omega_test*rs_hor)  # ingoing BC: exp(-iw*(-50)) = exp(iw*50)
    dps = -1j*omega_test*ps

    for i in range(N):
        rs = rs_hor + i*dr
        r = r_from_rstar(rs)
        Vr = V(r, 2, 6)
        h = dr

        k1_y = dps; k1_d = -(omega_test**2 - Vr)*ps
        rm = r_from_rstar(rs+h/2); Vm = V(rm, 2, 6)
        k2_y = dps+h/2*k1_d; k2_d = -(omega_test**2-Vm)*(ps+h/2*k1_y)
        k3_y = dps+h/2*k2_d; k3_d = -(omega_test**2-Vm)*(ps+h/2*k2_y)
        re = r_from_rstar(rs+h); Ve = V(re, 2, 6)
        k4_y = dps+h*k3_d; k4_d = -(omega_test**2-Ve)*(ps+h*k3_y)

        ps += h/6*(k1_y+2*k2_y+2*k3_y+k4_y)
        dps += h/6*(k1_d+2*k2_d+2*k3_d+k4_d)

    if abs(ps) > 1e-250:
        ps /= abs(ps)
        dps /= abs(ps)

    print(f"  After horizon->r*=0: |psi|≈{abs(ps):.2f}, |dpsi|≈{abs(dps):.2f}")
    print(f"  log deriv: {(dps/ps).real:.4f}+{(dps/ps).imag:.4f}i")
    # At r*=0, we expect to see growing mode because the potential supports it.
    # But the log derivative should reveal what the solution looks like.

print("\nDone")
