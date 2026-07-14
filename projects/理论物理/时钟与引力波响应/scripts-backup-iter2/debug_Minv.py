#!/usr/bin/env python3
"""Verify M_inv."""
import numpy as np

M = np.array([[14, -21, 0], [1, 0, 0], [60, -10, 35/2]])
M_inv = np.linalg.inv(M)

print("M:")
print(M)
print("\nM_inv (numpy):")
print(M_inv)
print("\nM_inv @ M:")
print(M_inv @ M)
print("\nM @ M_inv:")
print(M @ M_inv)

# Also try with exact fractions
from fractions import Fraction
import numpy as np

M_exact = np.array([[14, -21, 0], [1, 0, 0], [60, -10, 35/2]], dtype=np.float64)
# Use higher precision
M_high = np.array([[14, -21, 0], [1, 0, 0], [60, -10, 17.5]], dtype=np.float128)
M_inv_high = np.linalg.inv(M_high)
print("\nM_inv (float128):")
print(M_inv_high)
print("\nM_inv @ M (float128):")
print(M_inv_high @ M_high)

# Manual computation
# det(M) = 14 * (0 * 35/2 - 0 * (-10)) - (-21) * (1 * 35/2 - 0 * 60) + 0 * (...)
#        = 0 + 21 * 35/2
#        = 735/2
det_M = 735/2
print(f"\ndet(M) = {det_M}")

# Cofactor matrix (not transposed)
# C[0,0] = +(0*35/2 - 0*(-10)) = 0
# C[0,1] = -(1*35/2 - 0*60) = -35/2
# C[0,2] = +(1*(-10) - 0*60) = -10
# C[1,0] = -((-21)*35/2 - 0*(-10)) = -(-735/2) = 735/2
# C[1,1] = +(14*35/2 - 0*60) = 245
# C[1,2] = -(14*(-10) - (-21)*60) = -(-140 + 1260) = -1120
# C[2,0] = +((-21)*0 - 0*0) = 0
# C[2,1] = -(14*0 - 0*1) = 0
# C[2,2] = +(14*0 - (-21)*1) = 21

C = np.array([[0, -35/2, -10],
              [735/2, 245, -1120],
              [0, 0, 21]])

C_transposed = C.T  # This is the adjugate matrix
M_inv_manual = C_transposed / det_M

print("\nCofactor matrix:")
print(C)
print("\nAdjugate (C^T):")
print(C_transposed)
print("\nM_inv (manual):")
print(M_inv_manual)
print("\nM_inv_manual @ M:")
print(M_inv_manual @ M)

# So the correct M_inv is:
# [0, 2/7, 0]
# [-1/21, 1/3, -16/3]
# [0, 16/3, 1/7]
print("\n=== Expected M_inv entries ===")
print(f"M_inv[0,0] = {M_inv_manual[0,0]:.15f}")
print(f"M_inv[0,1] = {M_inv_manual[0,1]:.15f} (expected 2/7 = {2/7:.15f})")
print(f"M_inv[0,2] = {M_inv_manual[0,2]:.15f}")
print(f"M_inv[1,0] = {M_inv_manual[1,0]:.15f} (expected -1/21 = {-1/21:.15f})")
print(f"M_inv[1,1] = {M_inv_manual[1,1]:.15f} (expected 1/3 = {1/3:.15f})")
print(f"M_inv[1,2] = {M_inv_manual[1,2]:.15f} (expected -16/3 = {-16/3:.15f})")
print(f"M_inv[2,0] = {M_inv_manual[2,0]:.15f}")
print(f"M_inv[2,1] = {M_inv_manual[2,1]:.15f} (expected 16/3 = {16/3:.15f})")
print(f"M_inv[2,2] = {M_inv_manual[2,2]:.15f} (expected 1/7 = {1/7:.15f})")

# Compare with numpy
print("\n=== Comparison with numpy ===")
print("numpy M_inv:")
print(M_inv)
print("\nManual M_inv:")
print(M_inv_manual)
print("\nDifference:")
print(M_inv - M_inv_manual)
