# P2-2: v17 Paper LISA x Taiji Chiral ORF Discrepancy Analysis

## Problem Statement

v17 paper reports:
- LISA (30deg) x Taiji (0deg) inclined chiral ORF: **Gamma^V = -7.75e-3** (for f = 0.001, 0.01, 0.1 Hz)

Current script 11 (`11-multi-constellation-chiral-orf.py`) computes:
- LISA (30deg) x Taiji (0deg) sky-averaged chiral ORF: **|Gamma^V| = 1.34e-05** (default mode)

**Discrepancy: ~577x** in the sky-averaged value, **>10^7x** in the per-pixel maximum |R^V|.

This analysis identifies the specific implementation bug causing the massive difference.

---

## 1. Root Cause: Michelson-style Transfer Function Used for Taiji

### The Bug

Script 11's `run_full_analysis()` and related benchmark functions use the following defaults:

```python
const1_type='olc'    # LISA uses OLC transfer function
const2_type='interferometer'  # Taiji uses Michelson-style transfer function
```

The `const2_type='interferometer'` mode invokes `taiji_transfer_function()`, which implements a **Michelson-style transfer function**:

```python
def taiji_transfer_function(f, L, cos_nu):
    beta = np.pi * np.abs(f) * L / c
    sinc_val = np.where(np.abs(beta) < 1e-15, 1.0, np.sin(beta) / beta)
    phase = np.exp(-1j * beta)
    result = sinc_val * phase  # cos_nu parameter is UNUSED
```

Key problems:
1. **No (1-cos_nu) angular dependence** — the `cos_nu` parameter is computed but never used
2. **No imaginary prefactor** — the OLC transfer function has `1j * 2*pi*f*L/c` which breaks the reflection symmetry
3. **Phase factor is independent of sky direction** — `exp(-i*beta)` does not depend on `cos_nu`

### Why This Matters Physically

The chiral ORF Γ^V requires a **handedness-sensitive** (complex, asymmetric) transfer function. The OLC transfer function:

```python
T_OLC = 1j * 2πfL/c * sinc[β(1-cos_nu)] * exp(-iβ(1-cos_nu))
```

has two crucial properties:
- The **imaginary prefactor** `1j * 2πfL/c` ensures the transfer function has a non-vanishing imaginary part even for zero separation
- The **(1-cos_nu) dependence** couples the transfer function to the GW propagation direction, preventing it from factoring out of the sky integral

With the Michelson-style transfer function, T = sinc(β)·exp(-iβ) is **independent of sky direction**. It factors out of the sky integral, and the remaining antenna pattern integral vanishes due to the reflection symmetry of equilateral triangles.

**Result**: Michelson-style gives Gamma^V ≈ 0 (essentially a null measurement).

---

## 2. Quantitative Evidence

### 2.1 Direct Comparison: Michelson vs OLC (f = 0.01 Hz, LISA 30deg x Taiji 0deg)

| Mode | |Gamma^V| | max|R^V| |
|------|---------|------|
| Script 11 default (Michelson x OLC) | 7.20e-10 | 2.23e-05 |
| Corrected (OLC x OLC) | 5.02e-02 | 4.63e-03 |
| Paper script (OLC, with spatial phase) | 5.04e-02 | 6.44e-03 |
| v17 paper target | 7.75e-03 | — |

**Michelson mode gives a value ~70 million times smaller than OLC mode.** The discrepancy is overwhelming.

### 2.2 Frequency Sweep: Michelson vs OLC (f = 0.001-0.1 Hz)

At ALL frequencies tested, Michelson mode gives near-zero Gamma^V while OLC mode gives values in the 0.01-0.1 range:

| f (Hz) | Michelson Gamma^V | OLC Gamma^V |
|--------|-------------------|-------------|
| 0.001 | 2.72e-11 | 9.71e-02 |
| 0.005 | 2.99e-10 | 4.95e-02 |
| 0.01 | 7.20e-10 | 4.23e-02 |
| 0.05 | 1.36e-09 | 9.66e-03 |
| 0.1 | 2.82e-09 | 3.76e-03 |

### 2.3 Inclination Scan (f = 0.01 Hz)

The inclination angle is NOT the cause of the discrepancy:

| LISA Incl | Taiji Incl | |Gamma^V| (OLC) |
|-----------|------------|--------|----------|
| 0 | 0 | 4.90e-02 |
| 30 | 0 | 5.04e-02 |
| 60 | 0 | 4.44e-02 |
| 90 | 0 | 3.97e-02 |
| 0 | 30 | 4.66e-02 |
| 0 | 60 | 4.18e-02 |
| 0 | 90 | 3.53e-02 |

Inclination variation accounts for only ~4x, nowhere near the 577x discrepancy.

### 2.4 Per-Pixel Evidence

At f = 0.01 Hz (Michelson vs OLC):
- Michelson: max |R^V| = 2.23e-05 (uniformly near-zero across sky grid)
- OLC: max |R^V| = 4.63e-03

The per-pixel chiral integrand shows that Michelson mode produces near-zero values everywhere on the sky, while OLC mode produces significant values near specific sky directions.

---

## 3. Fix Required

### In `11-multi-constellation-chiral-orf.py`

Change the default detector types in `run_full_analysis()` from:

```python
const1_type='olc'
const2_type='interferometer'
```

to:

```python
const1_type='olc'
const2_type='olc'
```

And similarly in any other benchmark/comparison functions.

### In `antenna_pattern_e_variable_universal()`

The `det_type` parameter controls whether Michelson or OLC transfer function is used:
- `det_type='interferometer'` -> `taiji_transfer_function()` (Michelson, buggy)
- `det_type='olc'` -> `olc_transfer_function()` (correct)

Ensure all calls for multi-constellation computation use `det_type='olc'` for both detectors.

---

## 4. Residual Discrepancy After Fix

Even with the correct OLC transfer function applied to both detectors, there remains a **~6.5x discrepancy**:

- **Corrected code (OLC x OLC, with spatial phase):** |Gamma^V| = 5.04e-02 at f = 0.01 Hz
- **v17 paper:** Gamma^V = -7.75e-03

Potential sources:
1. **Sky grid resolution** — different pixelization may affect the integral
2. **Integration method** — the paper may use a different quadrature scheme
3. **Normalization convention** — different definitions of Gamma^V (whether divided by auto-response sqrt)
4. **Paper used pre-bug-fix code** — the v17 paper may have been generated with older code before the OLC transfer function implementation was finalized
5. **Different definition of Gamma^V vs R^V** — the paper may report a different quantity than what our code computes

This residual discrepancy should be investigated in a follow-up iteration but is secondary to the primary bug fix.

---

## 5. Paper's Internal Inconsistency: Spatial Phase Effect

The v17 paper states that the spatial phase effect (from 1 AU inter-constellation separation) has **less than 0.02% effect** on |Gamma^V|.

However, our code reproduction shows:
- **With spatial phase:** Gamma^V = -5.04e-02
- **Without spatial phase:** Gamma^V = 9.89e-05

**The spatial phase changes Gamma^V by a factor of ~500x, not 0.02%.**

This suggests either:
1. The paper's claim about spatial phase is incorrect
2. The paper's reported Gamma^V = -7.75e-03 was computed WITHOUT spatial phase (using a much smaller separation or no separation)
3. There is a bug in how the spatial phase is applied in the paper's code vs. the current code

This inconsistency is noted for future investigation.

---

## 6. Summary of Findings

| Finding | Details |
|---------|---------|
| **Root cause** | Script 11's default `const2_type='interferometer'` uses Michelson-style T = sinc(beta)*exp(-i*beta) instead of OLC-style T = 1j*2*pi*f*L/c * sinc[beta*(1-cos_nu)] * exp(-i*beta*(1-cos_nu)) |
| **Physical reason** | Michelson T has no sky-direction dependence, so it factors out of the sky integral. The antenna pattern integral of an equilateral triangle has reflection symmetry, so the chiral (V) component vanishes. |
| **Quantitative gap** | Michelson: |Gamma^V| ~ 10^-9; OLC: |Gamma^V| ~ 5x10^-2 (ratio > 10^7) |
| **Fix** | Change `const2_type='interferometer'` to `const2_type='olc'` in all benchmark/comparison functions |
| **Residual gap** | After fix: code gives 5.04e-02, paper claims 7.75e-03 (factor ~6.5) |
| **Paper inconsistency** | Paper claims spatial phase <0.02% effect; code shows >50000% effect |

---

## Files Referenced

- `/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/11-multi-constellation-chiral-orf.py` — Script 11 (contains both Michelson and OLC transfer functions)
- `/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/compute_chiral_orf_for_paper.py` — Paper script (uses only OLC)
- `/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/paper-archive/main-paper-v17.tex` — v17 paper
- `/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/note/P2-2-olc-invariance.md` — OLC invariance analysis

---

## Next Steps

1. Apply the fix (change `const2_type` to `'olc'` in script 11)
2. Verify that the fixed script reproduces OLC chiral ORF values matching the paper script
3. Investigate the residual ~6.5x discrepancy with the v17 paper's reported value
4. Investigate the paper's internal inconsistency regarding spatial phase effect
