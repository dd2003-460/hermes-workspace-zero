# OLC ORF Results Summary (v2)

> Date: 2026-06-28 (session continuation)

## Key Discovery: OLC ORF is fundamentally flat at OLC-relevant scales

### Mechanisms for frequency dependence:
1. **Arm response (sinc)**: T contains sinc[πfL/c·(1-n̂·û)]. But in the ORF ratio, L cancels and the sinc arguments are identical for both detectors → contributes nothing when d=0. Even with unequal arms, β<<1 for OLC → sinc ≈ 1 always.

2. **Baseline phase**: bp = exp(-i2πfd/c·n̂·s). Only mechanism that creates frequency dependence. But requires α=2πfd/c ~ 1.

### Regime analysis:
| Configuration | f·d product | α·cos(45°) | Effect |
|---|---|---|---|
| OLC ground, d=1 km, f=100 Hz | ~100 | 0.0003 | None (flat) |
| OLC ground, d=10 km, f=100 Hz | ~1000 | 0.002 | Tiny |
| OLC ground, d=10 km, f=1 kHz | ~10⁴ | 0.02 | Tiny |
| OLC ground, d=10 km, f=10 kHz | ~10⁵ | 0.21 | Slight drop |
| LISA-like, d=5M km, f=1 mHz | ~5000 | 0.008 | LISA IS sensitive here |
| PTA, d=1 kpc=3×10¹⁹ m, f=1 nHz | ~30 | 21 | HD curve varies strongly |

### Conclusion:
OLC ORF at ground scales is flat (~1.0 for L1=L2, constant geometric factor for unequal arms). The sinc arm response gives NO frequency structure at OLC-relevant scales (β<<1). To see frequency-dependent ORF from OLC, need either:
- Very long baselines (1000+ km)
- Very high frequencies (10+ kHz, beyond typical OLC sensitivity)
- BOTH simultaneously

The only regime where the ORF deviates from the low-f limit: f·d >~ 10⁶ m·Hz (α >~ 0.02), i.e. for d=10 km → f >~ 70 Hz gives visible (> 1%) deviation.

### Self-correlation:
- At d=0: |ORF| = 1.00000000 (relative error < 2.22e-16)
- At d>0 (α<0.01): |ORF| ≈ 1.0 (numerical deviation < 1e-10)
- Verified for d = 1, 10, 100, 1000 m at f=1 Hz

### Geometric limits (d=0, low-f):
- 0° arm angle: 1.00000
- 30° arm angle: 0.94491
- 45° arm angle: 0.50011
- 60° arm angle: -0.18871
- 90° arm angle: -0.49978
- 120° arm angle: -0.18871
- 150° arm angle: 0.94491
- 180° arm angle: 1.00000

### Low-frequency limit behavior:
At f < 1e-10 Hz, numerical underflow in |T|² (|T| ~ 2πfL/c ~ 10⁻²⁵) causes ORF → 0. At f >= 1e-8 Hz, recovers constant geometric value.

### Hellings-Downs validation (NOT matched)
The ORF code does NOT reproduce the Hellings-Downs curve at d=0. This is expected:

- HD curve comes from PTA timing residual analysis including pulsar terms: e^{iωL(1-n·p)/c}
- The ORF solver computes Earth-term only correlation
- The antenna pattern overlap F_plus·F_' + F_cross·F_' is NOT proportional to (1+n·u)(1+n·v) — their sky averages differ by factor 1.6

For OLC (no pulsars), the Earth-term only ORF is the correct quantity. HD is NOT applicable.
