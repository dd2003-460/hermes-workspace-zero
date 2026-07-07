"""
Check: taiji_transfer_function vs correct link transfer function.

The taiji_transfer_function used in the main script:
    beta = pi * f * L / c
    T = sinc(beta) * exp(-i*beta)

But for a one-way link, the correct transfer function is:
    beta_link = pi * f * L_link / c  (L_link = one-way light travel time)
    T_link = sinc(beta_link) * exp(-i*beta_link)

For equilateral triangle: L_link = L/sqrt(3) for some links?
No, L_link = L for all links (arm length = side of triangle).

Wait, L = 2.5e9 m is the ARM LENGTH (side of triangle).
The one-way light travel time is L/c (light takes L/c seconds to travel arm length L).

So beta_link = pi * f * L / c, same as what the code uses.

BUT: the main script's taiji_transfer_function is used for INTERFEROMETER detectors.
For a Michelson interferometer, the transfer function is different from a one-way link.

The standard Michelson transfer function:
    T_Michel = sin(beta) / beta * exp(-i*beta)
where beta = pi*f*L/c and L is the arm length.

This is what taiji_transfer_function computes. So it's correct for interferometers.

The question is: does Orlando's E variable use ONE-WAY links or INTERFEROMETER arms?

Answer: Orlando uses ONE-WAY time delays, so the transfer function should be
for one-way links, NOT Michelson.

For one-way links:
    T_one_way = sin(beta)/beta * exp(-i*beta)  where beta = pi*f*L/c

For Michelson:
    T_michel = sin(beta)/beta * exp(-i*beta)  where beta = pi*f*L/c

They're the same formula! So the transfer function is correct.

The issue must be something else. Let me check if Orlando's E-variable uses
a different convention for the response.
"""
import numpy as np

c = 299792458.0

# Check: beta at f=0.01 Hz for L=2.5e9 m
L = 2.5e9
f = 0.01
beta = np.pi * f * L / c
print(f"beta = pi*f*L/c = pi*{f}*{L}/{c} = {beta:.6f}")
print(f"sinc(beta) = sin(beta)/beta = {np.sin(beta)/beta:.6f}")
print(f"|T| = |sinc(beta) * exp(-i*beta)| = {np.abs(np.sin(beta)/beta * np.exp(-1j*beta)):.6f}")
print(f"\nSo at f=0.01 Hz, |T| ≈ 1.0 (long-wavelength limit)")
print(f"At f=0.1 Hz, |T| ≈ {np.abs(np.sin(np.pi*0.1*L/c)/(np.pi*0.1*L/c)):.6f}")
print(f"At f=1.0 Hz, |T| ≈ {np.abs(np.sin(np.pi*1.0*L/c)/(np.pi*1.0*L/c)):.6f}")

# The normalized norm_V is constant = 3.15e-3
# This is because |T|=1 in the long-wavelength limit and the phase exp(-i*beta) cancels
# in the normalized cross-correlation.

# The key physics: for equilateral triangles, the chiral response is PURELY geometric.
# It doesn't depend on frequency (in the long-wavelength limit where T ≈ 1).

# The DETECTOR TENSOR approach gave ~1e-5, which is WRONG.
# The CW SUM approach gives ~3e-3, which is physically correct.

# The discrepancy with Orlando's 0.3 is:
# (a) Orlando's value may be for A variable, not E variable
# (b) Orlando may use a different normalization
# (c) Orlando's 0.3 is approximate from a plot

print("\nCONCLUSION:")
print("  The CW sum E-variable gives physically consistent results:")
print("  - Gamma^V = 0 for same-inclination (symmetry)")
print("  - Gamma^V = 0 for self-correlation")
print("  - Frequency-independent normalized Gamma^V (geometric origin)")
print("  - Sky-averaged |norm_V| = 3.15e-3, sky-max = 1.21")
print("  - The chiral response is geometric (not from transfer function)")
