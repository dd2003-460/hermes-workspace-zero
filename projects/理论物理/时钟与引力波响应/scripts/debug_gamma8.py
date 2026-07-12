#!/usr/bin/env python3
"""Deep trace: why does JCAP gamma_I have opposite sign to numerical?"""
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
        'name': name, 'positions': rotated, 'centroid': centroid,
        'inclination': inclination, 'reference_position': reference_position, 'L': L
    }

const_lisa = make_triangle_constellation('LISA', LISA_L, LISA_INCLINATION, reference_position=np.array([0, 0, 0]))
const_taiji = make_triangle_constellation('Taiji', TAIJI_L, TAIJI_INCLINATION, reference_position=np.array([AU, 0, 0]))

# Key setup: understand the JCAP formula
# In JCAP, the detectors are at different locations
# The separation vector s_hat goes FROM detector 1 TO detector 2
# The sky average is over GW propagation direction k_hat

# Numerical: R_plus = theta^T D theta, R_cross = theta^T D phi
# The numerical cross ORF: <R1+*R2+ + R1x*R2x> / sqrt(<R1+^2+R1x^2> * <R2+^2+R2x^2>)

# JCAP formula: gamma_I = 4*(b0*I + b1*II + b2*III)
# where I, II, III are contractions of D tensors with s_hat

# The b coefficients: bI = (1/7) * M_inv * [j0, j2, j4]^T
# At f=0: j0=1, j2=0, j4=0, so bI = (1/7) * M_inv[:, 0]
# M_inv[:, 0] = first column of M_inv = [0, -1/21, -2/735]^T (approximately)

# Wait, let me recheck. The actual M_inv from numpy:
M = np.array([[14, -21, 0], [1, 0, 0], [60, -10, 35/2]])
M_inv = np.linalg.inv(M)
print("M_inv:")
print(M_inv)
print(f"\nM_inv @ M:")
print(M_inv @ M)

# M_inv[:, 0] = [0, -1/21, -2/735] approximately
# bI[0] = (1/7) * 0 = 0
# bI[1] = (1/7) * (-1/21) = -1/147 = -0.00680272...
# bI[2] = (1/7) * (-2/735) = -2/5145 = -0.0003887...
# Wait, the output showed b2 = -0.00388727, which is -2/514.5...
# Let me check: M_inv[2,0] = ?

print(f"\nM_inv[2,0] = {M_inv[2,0]:.15f}")
print(f"-2/735/7 = {-2/735/7:.15f}")
print(f"-2/105 = {-2/105:.15f}")

# From M_inv @ M = I:
# M_inv[2,:] @ M[:,0] = M_inv[2,0]*14 + M_inv[2,1]*1 + M_inv[2,2]*60 = 0
# M_inv[2,:] @ M[:,1] = M_inv[2,0]*(-21) + M_inv[2,1]*0 + M_inv[2,2]*(-10) = 0
# M_inv[2,:] @ M[:,2] = M_inv[2,0]*0 + M_inv[2,1]*0 + M_inv[2,2]*(35/2) = 1

# From eq 3: M_inv[2,2] = 2/35 = 0.05714...
print(f"\nExpected M_inv[2,2] = 2/35 = {2/35:.15f}")
print(f"Actual M_inv[2,2] = {M_inv[2,2]:.15f}")

# From eq 2: -21*M_inv[2,0] - 10*M_inv[2,2] = 0
# => M_inv[2,0] = -10/21 * M_inv[2,2] = -10/21 * 2/35 = -20/735 = -4/147
print(f"Expected M_inv[2,0] = -4/147 = {-4/147:.15f}")
print(f"Actual M_inv[2,0] = {M_inv[2,0]:.15f}")

# From eq 1: 14*M_inv[2,0] + M_inv[2,1] + 60*M_inv[2,2] = 0
# => M_inv[2,1] = -14*M_inv[2,0] - 60*M_inv[2,2] = -14*(-4/147) - 60*(2/35)
# = 56/147 - 120/35 = 56/147 - 504/147 = -448/147 = -32/10.5 = -64/21
print(f"Expected M_inv[2,1] = -64/21 = {-64/21:.15f}")
print(f"Actual M_inv[2,1] = {M_inv[2,1]:.15f}")

# So M_inv =
# [[0, 1, 0],
#  [-1/21, 2/3, 0],
#  [-4/147, -64/21, 2/35]]

# Let me verify: M_inv[0,:] @ M = [1, 0, 0]
# [0, 1, 0] @ [14, -21, 0] = -21 => wrong!
# Wait, we need M_inv @ M = I.
# M_inv[0,:] = [0, 1, 0]
# M_inv[0,0]*14 + M_inv[0,1]*1 + M_inv[0,2]*60 = 0 + 1 + 0 = 1 ✓
# M_inv[0,0]*(-21) + M_inv[0,1]*0 + M_inv[0,2]*(-10) = 0 ✓
# M_inv[0,0]*0 + M_inv[0,1]*0 + M_inv[0,2]*(35/2) = 0 ✓
# So M_inv[0,:] = [0, 1, 0] gives [1, 0, 0] ✓

# M_inv[1,:] = [-1/21, 2/3, 0]
# (-1/21)*14 + (2/3)*1 + 0*60 = -2/3 + 2/3 = 0 ✓
# (-1/21)*(-21) + (2/3)*0 + 0*(-10) = 1 + 0 = 1 ✓
# (-1/21)*0 + (2/3)*0 + 0*(35/2) = 0 ✓

# M_inv[2,:] = [-4/147, -64/21, 2/35]
# (-4/147)*14 + (-64/21)*1 + (2/35)*60 = -56/147 - 64/21 + 120/35
# = -4/10.5 - 64/21 + 24/7
# = -8/21 - 64/21 + 72/21 = 0 ✓
# (-4/147)*(-21) + (-64/21)*0 + (2/35)*(-10) = 84/147 - 20/35 = 4/7 - 4/7 = 0 ✓
# (-4/147)*0 + (-64/21)*0 + (2/35)*(35/2) = 1 ✓

# Good, the M_inv is confirmed correct.

# Now the issue: at f=0, bI[0] = 0, bI[1] = -1/147, bI[2] = -4/1029
# gamma_I(0) = 4 * (-1/147 * term_s - 4/1029 * term_ss)

# Both b1 and b2 are negative. The contractions term_s and term_ss are positive.
# So gamma_I(0) is negative.

# But the numerical result is positive! Why?

# Let me think about this physically.
# R_plus = theta^T D theta (response to plus polarization)
# For coplanar detectors in xy plane:
# R_plus = theta_x^2 - theta_y^2 (when arms are in xy plane)
# Actually no, for CW links, R_plus = sum (theta . u_l)^2 for each arm direction u_l
# Wait, R_plus = theta^T D theta = sum_l (theta . u_l)^2
# where u_l are the unit arm vectors.
# For a triangle in xy plane: u1 = (1,0,0), u2 = (-1/2, sqrt(3)/2, 0), u3 = (-1/2, -sqrt(3)/2, 0)
# R_plus = theta_x^2 + (-1/2 theta_x + sqrt(3)/2 theta_y)^2 + (-1/2 theta_x - sqrt(3)/2 theta_y)^2
# = theta_x^2 + 1/4 theta_x^2 - sqrt(3)/2 theta_x theta_y + 3/4 theta_y^2
#       + 1/4 theta_x^2 + sqrt(3)/2 theta_x theta_y + 3/4 theta_y^2
# = theta_x^2 + theta_x^2/4 + 3/4 theta_y^2 + theta_x^2/4 + 3/4 theta_y^2
# = 3/2 theta_x^2 + 3/2 theta_y^2
# = 3/2 (1 - theta_z^2)

# R_cross = theta^T D phi = sum (theta . u_l)(phi . u_l)
# For coplanar: = 3/2 theta_x phi_x + 3/2 theta_y phi_y
# = 3/2 (theta . phi - theta_z phi_z)
# Since theta . phi = 0: = -3/2 theta_z phi_z

# Now, the cross-correlation:
# R1_plus * R2_plus + R1_cross * R2_cross
# = (3/2)(1 - theta_z1^2) * (3/2)(1 - theta_z2^2) + (-3/2 theta_z1 phi_z1)(-3/2 theta_z2 phi_z2)
#
# Wait, both detectors are at different locations but have the same orientation convention.
# The theta and phi vectors are defined relative to k_hat (GW propagation direction).
# For both detectors, the basis is:
# theta: in the plane of k and z-axis (or defined similarly)
# phi: perpendicular to both k and theta

# Actually, in the numerical computation, both detectors use the same sky basis.
# theta(k) and phi(k) are the same for both detectors (defined by GW direction).
# The only difference is the detector tensor D.

# For coplanar detectors (both in xy plane, same orientation):
# R1_plus = 3/2 (1 - theta_z^2) = 3/2 (sin^2 theta)  [in spherical coords]
# R2_plus = 3/2 (1 - theta_z^2) = same
# R1_cross = 3/2 (-theta_z phi_z)
# R2_cross = 3/2 (-theta_z phi_z)

# Wait, both have the same D if they're coplanar and coplanar in the same way?
# No, LISA has inclination 30 deg, Taiji has 0 deg.

# OK let me be more careful.
# LISA at (0,0,0) with inclination 30 deg: the triangle is tilted.
# Taiji at (AU, 0, 0) with inclination 0: the triangle is in xy plane.

# So the D tensors are DIFFERENT even for coplanar detectors.

# Let me compute the contractions explicitly
def compute_detector_tensor_dimensionless(constellation):
    pos = constellation['positions']
    D = np.zeros((3, 3))
    cw_links = [(0, 1), (1, 2), (2, 0)]
    for i, j in cw_links:
        arm = pos[j] - pos[i]
        arm_len = np.linalg.norm(arm)
        if arm_len < 1e-30: continue
        u = arm / arm_len
        D += np.outer(u, u)
    return D

D1 = compute_detector_tensor_dimensionless(const_lisa)
D2 = compute_detector_tensor_dimensionless(const_taiji)

delta_x = const_lisa['centroid'] - const_taiji['centroid']
delta_r = np.linalg.norm(delta_x)
s_hat = delta_x / delta_r

print(f"\n=== Explicit D tensors ===")
print(f"D1 (LISA, 30 deg):")
print(D1)
print(f"\nD2 (Taiji, 0 deg):")
print(D2)
print(f"\ns_hat = {s_hat}")

# D1 should be tilted 30 degrees from xy plane
# D2 should be in xy plane

# For D2 (coplanar, in xy plane):
# The three arm directions are:
# u1: (0,0,0) -> (L,0,0): u = (1,0,0)
# u2: (L,0,0) -> (L/2, L*sqrt(3)/2, 0): u = (-1/2, sqrt(3)/2, 0)
# u3: (L/2, L*sqrt(3)/2, 0) -> (0,0,0): u = (-1/2, -sqrt(3)/2, 0)
# D = sum u_l u_l^T = [[1,0,0] + [1/4,-sqrt(3)/4,0] + [1/4,sqrt(3)/4,0], ...]
# D2 = [[1+1/4+1/4, -sqrt(3)/4+sqrt(3)/4, 0],
#        [-sqrt(3)/4+sqrt(3)/4, 3/4+3/4, 0],
#        [0, 0, 0]]
#    = [[3/2, 0, 0], [0, 3/2, 0], [0, 0, 0]]
# trace = 3, det = 0 (coplanar) ✓

# For D1 (tilted 30 degrees):
# Original triangle in xy plane, then rotated about x-axis by 30 deg.
# After rotation, the arms are no longer purely in xy plane.

# Now let's compute the contractions:
tr = np.einsum('ab,ab->', D1, D2)
D1s = D1 @ s_hat
D2s = D2 @ s_hat
term_s = np.dot(D1s, D2s)
sD1s = np.dot(s_hat, D1 @ s_hat)
sD2s = np.dot(s_hat, D2 @ s_hat)
term_ss = sD1s * sD2s

print(f"\n=== Contractions ===")
print(f"tr(D1D2) = {tr}")
print(f"(D1@s).**(D2@s) = {term_s}")
print(f"s^T D1 s = {np.dot(s_hat, D1 @ s_hat)}")
print(f"s^T D2 s = {np.dot(s_hat, D2 @ s_hat)}")
print(f"(s^T D1 s)(s^T D2 s) = {term_ss}")

# Now: the JCAP formula says gamma_I = 4*(b0*I + b1*II + b2*III)
# At f=0: b0=0, b1=-1/147, b2=-4/1029
# gamma_I(0) = 4*(-1/147*0.6137 - 4/1029*0.2731) = 4*(-0.004175 - 0.001060) = -0.02313...

# Hmm, let me compute this exactly:
b1_f0 = -1/147
b2_f0 = -4/1029
gamma_I_f0 = 4 * (b1_f0 * term_s + b2_f0 * term_ss)
print(f"\n=== JCAP gamma_I at f=0 (with exact fractions) ===")
print(f"b1 = {b1_f0}")
print(f"b2 = {b2_f0}")
print(f"gamma_I(0) = 4 * ({b1_f0} * {term_s} + {b2_f0} * {term_ss})")
print(f"         = 4 * ({b1_f0 * term_s} + {b2_f0 * term_ss})")
print(f"         = {gamma_I_f0}")

# This matches our numerical result of -0.0209 (close, slight difference from floating point)

# The KEY question: WHY IS THE NUMERICAL RESULT POSITIVE?

# Let me check the numerical parity-even integral directly
# by computing the integrand value at various sky directions
ntheta, nphi = 20, 40
thetas = np.linspace(0, np.pi, ntheta)
phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
tG, pG = np.meshgrid(thetas, phis, indexing='ij')
dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)

th = np.stack([np.cos(tG)*np.cos(pG), np.cos(tG)*np.sin(pG), -np.sin(tG)])
ph = np.stack([-np.sin(pG), np.cos(pG), np.zeros_like(np.sin(pG))])

def response(a, b, D):
    result = np.zeros_like(a[0])
    for i in range(3):
        for j in range(3):
            result += D[i, j] * a[i] * b[j]
    return result

R1_plus = response(th, th, D1)
R1_cross = response(th, ph, D1)
R2_plus = response(th, th, D2)
R2_cross = response(th, ph, D2)

parity_even = R1_plus * R2_plus + R1_cross * R2_cross
print(f"\n=== Numerical integrand statistics ===")
print(f"Min integrand = {np.min(parity_even):.6f}")
print(f"Max integrand = {np.max(parity_even):.6f}")
print(f"Mean integrand = {np.mean(parity_even):.6f}")
print(f"Integral = {np.sum(parity_even * dO):.6f}")

# Check individual products:
prod1 = R1_plus * R2_plus
prod2 = R1_cross * R2_cross
print(f"\nMean(R1_plus * R2_plus) = {np.mean(prod1):.6f}")
print(f"Mean(R1_cross * R2_cross) = {np.mean(prod2):.6f}")
print(f"Integral(R1_plus * R2_plus) = {np.sum(prod1 * dO):.6f}")
print(f"Integral(R1_cross * R2_cross) = {np.sum(prod2 * dO):.6f}")

# R1_plus * R2_plus = (th^T D1 th) * (th^T D2 th)
# This is a 4th-order polynomial in theta components
# th = (cos_theta*cos_phi, cos_theta*sin_phi, -sin_theta)
# For z-parallel GW (theta=0): th = (0, 0, -1), so R_plus = -z^T D (-z) = z^T D z
# For both detectors, D has z-z component...

print(f"\n=== Integrand at z-parallel (theta=0) ===")
# th at theta=0: (0, 0, -1)
# phi at theta=0: (-1, 0, 0) [arbitrary in xy plane]
th_z = np.array([0, 0, -1])
ph_x = np.array([-1, 0, 0])
R1_p_z = np.dot(th_z, D1 @ th_z)
R1_c_z = np.dot(th_z, D1 @ ph_x)
R2_p_z = np.dot(th_z, D2 @ th_z)
R2_c_z = np.dot(th_z, D2 @ ph_x)
print(f"R1_plus = {R1_p_z}, R1_cross = {R1_c_z}")
print(f"R2_plus = {R2_p_z}, R2_cross = {R2_c_z}")
print(f"R1_plus*R2_plus = {R1_p_z * R2_p_z}")
print(f"R1_cross*R2_cross = {R1_c_z * R2_c_z}")

# For D2 (xy plane): D2 = diag(1.5, 1.5, 0)
# th_z = (0,0,-1): D2 @ th_z = (0,0,0), so R2_plus = 0, R2_cross = 0
# For D1 (tilted 30 deg): need to compute D1_zz

print(f"\n=== z-components of D tensors ===")
print(f"D1[2,2] = {D1[2,2]}")
print(f"D2[2,2] = {D2[2,2]}")

# D2[2,2] = 0 (coplanar in xy plane) - this makes R2_plus = R2_cross = 0 for z-parallel
# D1[2,2] > 0 (tilted)

# So for most sky directions, at least one detector gives a small response product.
# The integral sums over all sky directions.

# The fact that the numerical integral is POSITIVE but JCAP is NEGATIVE
# means there's a SIGN CONVENTION difference.

# In JCAP, the formula for gamma_I might use a different convention for s_hat direction.
# The paper defines s_hat as the unit vector from detector A to detector B.
# Our code uses: delta_x = const1['centroid'] - const2['centroid']
# i.e., FROM const2 TO const1.

# Let me try with reversed s_hat
s_hat_rev = -s_hat
tr_rev = np.einsum('ab,ab->', D1, D2)
D1s_r = D1 @ s_hat_rev
D2s_r = D2 @ s_hat_rev
term_s_r = np.dot(D1s_r, D2s_r)
sD1s_r = np.dot(s_hat_rev, D1 @ s_hat_rev)
sD2s_r = np.dot(s_hat_rev, D2 @ s_hat_rev)
term_ss_r = sD1s_r * sD2s_r

b0_0 = -1.2390881971262907e-19
b1_0 = -0.006802721088435373
b2_0 = -0.0038872691933916417

gamma_I_f0_rev = 4 * (b0_0 * tr_rev + b1_0 * term_s_r + b2_0 * term_ss_r)
print(f"\n=== With reversed s_hat ===")
print(f"(D1@(-s)).**(D2@(-s)) = {term_s_r}")
print(f"((-s)^T D1 (-s))((-s)^T D2 (-s)) = {term_ss_r}")
print(f"gamma_I(0, -s) = {gamma_I_f0_rev}")

# For term_s: (D1@(-s)).**(D2@(-s)) = (D1@s).(D2@s) (same sign, both reversed)
# For term_ss: ((-s)^T D1 (-s))((-s)^T D2 (-s)) = (s^T D1 s)(s^T D2 s) (same sign)
# So gamma_I is unchanged! The sign doesn't come from s_hat direction.

# Let me check: maybe the JCAP formula for gamma_I has a minus sign
# that's missing from our implementation?

# In the JCAP paper, the chiral (V) formula has:
# gamma_V = 4i * (bV0 * (...) + bV1 * (...))
# The "i" makes it imaginary, and the chiral ORF is the imaginary part.

# For the parity-even (I) formula, it should be:
# gamma_I = 4 * (bI0 * I + bI1 * II + bI2 * III)
# where I, II, III are the same contractions as in the E (parity-even) formula.

# But wait - the JCAP paper might define gamma_I differently.
# Let me check if there's a minus sign from the definition.

# Actually, I think the issue might be in the O(3) decomposition.
# The parity-even OLF uses a different O(3) decomposition than the chiral one.
# In Nishizawa et al. 2009, the parity-even OLF is:
# Gamma_E = sum_l alpha_l * integral Y_lm * Y*_l'm' dOmega
# where alpha_l are angular coefficients.

# The JCAP paper's formula in terms of D tensors might have a different sign.

# Let me try: what if the JCAP formula should give
# gamma_I = -4 * (b0*I + b1*II + b2*III)?

print(f"\n=== With overall minus sign ===")
print(f"-gamma_I(0) = {-gamma_I_f0_rev}")
print(f"Numerical ORF = {np.sum(parity_even * dO) / np.sqrt(np.sum((R1_plus**2+R1_cross**2)*dO) * np.sum((R2_plus**2+R2_cross**2)*dO))}")

# Actually, the self-normalized ratio was -0.813 (JCAP) vs 0.775 (numerical)
# The sign flip gives +0.813 vs 0.775.
# These are close but not exact.
# Let me check if there's a normalization issue beyond the sign.

# What if the JCAP formula has a different normalization?
# JCAP might use D^{ab} normalized differently.

# In JCAP, the dimensionless detector tensor D^{ab} might be normalized as:
# D^{ab} = (1/3) * sum_l u_l^a u_l^b  (divided by number of arms)
# vs our D^{ab} = sum_l u_l^a u_l^b (not divided)

# If JCAP divides by 3 (number of arms), then the contraction I would be smaller by factor 9.
# Let me check: if we use D/3, then:
# gamma_I = 4 * (b0 * tr(D1/3, D2/3) + ...) = 4/9 * (b0 * tr(D1,D2) + ...)
# This would make gamma_I 9 times smaller, which is worse.

# Alternatively, JCAP might normalize differently.
# The key is that JCAP's gamma_I represents the sky-averaged ORF value.
# The sky average is <R1*R2> = (1/4pi) * integral(R1*R2 dOmega)
# The numerical code gives ORF = integral(R1*R2 dOmega) / sqrt(integral(R1^2)*integral(R2^2))

# For JCAP, the "normalization" should be built into the formula.
# The formula 4*(b0*I + b1*II + b2*III) gives the sky-averaged cross-correlation
# when using the dimensionless D tensors.

# But the numerical code computes a different normalization.
# The numerical code normalizes by sqrt(auto1 * auto2).

# The JCAP formula does NOT normalize this way. It directly gives the cross ORF value.

# So the comparison should be:
# numerical ORF = integral(R1*R2 dOmega) / sqrt(integral(R1^2 dOmega) * integral(R2^2 dOmega))
# JCAP gamma_I = some function of D tensors (which should equal the above when properly normalized)

# For the comparison to work, we need:
# JCAP gamma_I = integral(R1*R2 dOmega) / sqrt(integral(R1^2 dOmega) * integral(R2^2 dOmega))

# The integral of R1*R2 over sky can be expressed in terms of D tensor contractions.
# Let me compute this analytically.

# For sky average: <theta_a theta_b theta_c theta_d> = 4pi/15 * (delta_ab delta_cd + ...)
# But with the cross term <theta_a theta_b phi_c phi_d>, we get:
# <theta_a phi_b theta_c phi_d> = 4pi/15 * (delta_ac delta_bd - delta_ad delta_bc) ... hmm

# Actually, let me think about this differently.
# The response R_plus = theta^T D theta
# R_cross = theta^T D phi
# <R_plus^2> = <theta_a D_ab theta_b theta_c D_cd theta_d>
#            = D_ab D_cd <theta_a theta_b theta_c theta_d>
# For isotropic sky average:
# <theta_a theta_b theta_c theta_d> = 4pi/15 * (delta_ab delta_cd + delta_ac delta_bd + delta_ad delta_bc - 2/7 * (something))

# Wait, the sky average of 4th-order products is:
# <theta_a theta_b theta_c theta_d> = (4pi/15) * (delta_ab delta_cd + delta_ac delta_bd + delta_ad delta_bc) / 3? No...
# Actually: <theta_i theta_j theta_k theta_l> = 4pi/15 * (delta_ij delta_kl + delta_ik delta_jl + delta_il delta_jk - 2/5 * delta_ij delta_kl)?
# No, for isotropic average over unit sphere:
# <n_i n_j> = 4pi/3 * delta_ij
# <n_i n_j n_k n_l> = 4pi/15 * (delta_ij delta_kl + delta_ik delta_jl + delta_il delta_jk)

# But theta and phi are NOT isotropic - they depend on k (the GW propagation direction).
# The basis vectors change with sky direction.
# theta(k) and phi(k) are orthogonal to k.

# <theta_a theta_b> = <(delta_ak - k_a k_k)(delta_bl - k_b k_l)> / 3 ... this is getting complicated.

# Let me just compute the expected sky integrals numerically and compare.
print(f"\n=== Expected vs actual sky integrals ===")
# For auto detector 1:
auto1 = np.sum((R1_plus**2 + R1_cross**2) * dO)
auto2 = np.sum((R2_plus**2 + R2_cross**2) * dO)
cross = np.sum(parity_even * dO)
print(f"auto1 = {auto1}")
print(f"auto2 = {auto2}")
print(f"cross = {cross}")

# What does JCAP formula give for auto1?
# Using D1 with itself:
tr11 = np.einsum('ab,ab->', D1, D1)
D1s2 = D1 @ s_hat
term_s11 = np.dot(D1s2, D1s2)
sD1s2 = np.dot(s_hat, D1 @ s_hat)

gi_auto1 = 4 * (b0_0 * tr11 + b1_0 * term_s11 + b2_0 * sD1s2**2)
print(f"\nJCAP auto1 = {gi_auto1}")
print(f"Ratio auto1/JCAP_auto1 = {auto1 / gi_auto1}")

# For auto2:
tr22 = np.einsum('ab,ab->', D2, D2)
D2s2 = D2 @ s_hat
term_s22 = np.dot(D2s2, D2s2)
sD2s2 = np.dot(s_hat, D2 @ s_hat)

gi_auto2 = 4 * (b0_0 * tr22 + b1_0 * term_s22 + b2_0 * sD2s2**2)
print(f"JCAP auto2 = {gi_auto2}")
print(f"Ratio auto2/JCAP_auto2 = {auto2 / gi_auto2}")

# If the ratios are the same, then self-normalizing the JCAP formula should work:
# ORF = JCAP_cross / sqrt(JCAP_auto1 * JCAP_auto2) * constant
# where constant = sqrt(Ratio_auto1 * Ratio_auto2)

ratio1 = auto1 / gi_auto1
ratio2 = auto2 / gi_auto2
print(f"\nRatio1 = {ratio1}")
print(f"Ratio2 = {ratio2}")
print(f"Geometric mean = {np.sqrt(ratio1 * ratio2)}")

# The expected numerical ORF would be:
# expected = JCAP_cross / sqrt(JCAP_auto1 * JCAP_auto2) * sqrt(Ratio_auto1 * Ratio_auto2)
expected_orf = gi_auto1 * 0  # placeholder
# Actually: expected = cross / sqrt(auto1 * auto2)
#            = (JCAP_cross * common_ratio) / sqrt(JCAP_auto1 * common_ratio * JCAP_auto2 * common_ratio)
#            = JCAP_cross / sqrt(JCAP_auto1 * JCAP_auto2)
# provided the common_ratio is the same for both auto detectors.

if abs(ratio1 - ratio2) < 0.01 * min(ratio1, ratio2):
    print("Ratios are approximately equal - self-normalized JCAP should match numerical!")
else:
    print(f"Ratios differ by {abs(ratio1 - ratio2)/min(ratio1, ratio2)*100:.1f}% - different responses")

# Now the self-normalized JCAP:
sn_jcap = gi_auto1  # placeholder - need correct calculation
sn_jcap = gi_auto1 * 0
sn_jcap_val = -0.02094569933629711 / np.sqrt((-0.01768160146710165) * (-0.03752723520148646))
print(f"\nSelf-normalized JCAP = {sn_jcap_val}")
print(f"Numerical ORF = {cross / np.sqrt(auto1 * auto2)}")
print(f"Sign difference: {np.sign(sn_jcap_val)} vs {np.sign(cross / np.sqrt(auto1 * auto2))}")
print(f"Relative sign flip test: {-sn_jcap_val} vs {cross / np.sqrt(auto1 * auto2)}")
