=== SUB-5.1 FIXED REPORT ===

1. L_olc sync: **MISMATCH FOUND**
   - Code (03-olc-snr-solver.py line 45): `L_olc = 10.0` (10 meters, ground-based)
   - Paper (main-paper.tex): `L = 0.17-3 Gm` (1.7e8 - 3e9 meters, space-based)
   - The paper explicitly notes this correction at lines 444, 651, 790, 1039, 1107, 1230: the ground-based L=10m analysis was "证伪" and space-based arm lengths were adopted.
   - **However**, the SNR solver at line 60 uses `t_base = 2*pi*f*L_olc/c` with L_olc=10, giving transfer functions ~10^8 too small.
   - Lisa arm length at line 100 is correctly set to 2.5e9 m for comparison.

2. gamma_olc source: **HARDCODED**
   - Code (03-olc-snr-solver.py line 46): `gamma_olc = -0.188`
   - Comment says "flat ORF, 60 deg arm angle"
   - This value is NOT computed from sky-averaging in the code. It appears to be an empirical value from some earlier analysis.
   - The paper's sky-averaged ORF K_sky ~ 0.53 (line 604, 1111, 1230), but gamma_olc = -0.188 is a different quantity (un-normalized ORF for 60-degree arm angle).
   - **Source unknown**: There is no code path that computes this value from phi_g (azimuth) scanning. The -0.188 appears to come from a 2D projection analysis where the arm geometry is fixed and gamma is computed for a specific configuration.
   - The code does NOT perform any phi_g scan to verify or optimize gamma_olc.

3. phi_g scan: **NOT PERFORMED (in SNR solver)**
   - The SNR solver (03-olc-snr-solver.py) uses a hardcoded gamma_olc = -0.188 with no sky-averaging computation.
   - The chiral ORF scripts (10, 11) DO perform sky-averaging with full theta+phi grids: `thetas = np.linspace(0, np.pi, ntheta)` and `phis = np.linspace(0, 2*pi, nphi)`.
   - **Azimuth bug status**: The chiral ORF code (10-olc-chiral-orf-triangular.py lines 67-72) correctly computes:
     - `nx = sin(tG)*cos(pG)`, `ny = sin(tG)*sin(pG)`, `nz = cos(tG)`
     - `cos_nu = nx*sin(arm_theta)*cos(arm_phi) + ny*sin(arm_theta)*sin(arm_phi) + nz*cos(arm_theta)`
     - The `ny` term correctly includes `sin(pG)` -- NO missing azimuth bug detected.
   - The `sin(tG)` Jacobian factor is included in the integration measure `dO = np.sin(tG) * ...` (line 181).
   - Some older scripts (09-olc-chiral-orf-*) have sky grids with theta in [0,pi] and phi in [0,2pi), which is correct.

4. Chiral ORF symmetry: **Gamma^V = 0 for planar configurations**
   - The code includes an explicit test `test_coplanar_zero()` (line 280) that verifies: for an equilateral triangle in the xy-plane, Gamma^V < 1e-10.
   - This is physically correct: a planar equilateral triangle has mirror symmetry across the plane, and the chiral ORF (which measures parity-odd correlations) must vanish.
   - Test `test_nonzero_asymmetric()` (line 357) confirms: breaking symmetry (non-equilateral triangle) produces non-zero Gamma^V.
   - **Conclusion**: For the standard triangular OLC constellation (planar, equilateral), Gamma^V = 0. To detect chiral SGWB, one needs either:
     (a) Non-planar constellation (z-offset of satellites), OR
     (b) Asymmetric arm configuration breaking mirror symmetry.

5. Compatibility note with SUB-5.0: **CRITICAL INTERACTION**
   - SUB-5.0's SNR corrections are based on gamma_olc = -0.188. If gamma_olc should actually be 0 (from proper phi_g scanning of a planar equilateral triangle), then:
     - The SNR formula uses `gamma_olc^2` (line 79), so gamma = 0 would give SNR = 0.
     - This means the entire SNR estimate collapses for a single triangular constellation.
     - If the constellation is non-planar or asymmetric, gamma_olc may not be exactly 0 but would be different from -0.188.
   - **The -0.188 value may be from a non-planar configuration** (e.g., tetrahedral, or non-equilateral). Without knowing the exact geometry used, this is a blind spot.
   - **Action required**: gamma_olc must be recomputed from a proper sky-average over the actual constellation geometry before SUB-5.0's SNR values are reliable. The 10m arm length issue compounds this: the transfer function magnitude is wrong by 10^8, which propagates into the absolute SNR scale.

=== END ===
