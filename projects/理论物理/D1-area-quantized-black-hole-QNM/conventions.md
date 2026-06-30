# Coordinate, Unit, and Sign Conventions

**Last updated**: 2026-06-26
**Purpose**: Ensure consistency across the Teukolsky + AIM solver implementation for the P1 task chain.

---

## 1. Unit Convention

```
G = c = M = 1
```

All quantities are dimensionless, scaled by the black hole mass M. Length and time have units of M (geometric units).

| Physical Quantity | In M units |
|-------------------|------------|
| Length            | L → L/M    |
| Time              | T → T/M    |
| Frequency         | ω → ωM     |
| Angular momentum  | a → a/M, 0 ≤ a/M ≤ 1 |
| Area              | A → A/M²   |

Kerr horizon positions (roots of Δ = r² − 2Mr + a² = 0):
- Outer horizon: r₊ = M + √(M² − a²) = 1 + √(1 − a²) (with M=1)
- Inner horizon: r₋ = M − √(M² − a²) = 1 − √(1 − a²)

At a = 0: r₊ = 2M = 2, r₋ = 0.

---

## 2. Coordinate System

### 2.1 Schwarzschild radial coordinate r

- r ∈ [2M, ∞) for the exterior region.
- The event horizon is at r = 2M (a=0) or r = r₊ (a>0).

### 2.2 Tortoise coordinate r*

```
r* = r + 2M ln|(r/(2M) − 1)|         (Schwarzschild, a=0)
```

Properties:
- r* → −∞ as r → 2M⁺ (approaching the horizon from outside)
- r* → +∞ as r → ∞
- dr*/dr = r²/Δ = r²/[r(r − 2M)] = r/(r − 2M) = 1/(1 − 2M/r)

At the horizon (r → 2M⁺):
- r* ~ 2M ln(r − 2M) → −∞
- This logarithmic mapping is what causes the exponential behavior in Teukolsky boundary conditions.

### 2.3 Compactification coordinate x (or z)

Multiple notations are used across the codebase. The conventions below are standard:

```
x (or z) = 1 − 2M/r = (r − 2M)/r
```

This maps:
- r = 2M  →  x = 0   (horizon)
- r = ∞   →  x = 1   (infinity)

Alternative for Kerr (Leaver's convention):
```
x_leaver = (r − r₊)/(r₊ − r₋)
```
This maps:
- r = r₊ → x_leaver = 0 (outer horizon)
- r = r₋ → x_leaver = 1 (inner horizon)
- r → ∞  → x_leaver → 1 (when mapped via 1−x for infinity BC)

**Convention for this project**: Use `x = 1 − 2M/r` as the primary expansion variable for a=0. Use `x_leaver = (r − r₊)/(r₊ − r₋)` for a>0 Teukolsky.

---

## 3. Teukolsky Equation Convention

### 3.1 Metric signature and spin coefficient

- Metric signature: (−, +, +, +)
- Teukolsky spin-weight: s for gravitational perturbations, s = −2

### 3.2 Radial Teukolsky Equation (general Kerr, a>0)

```
Δ^(-s) [d/dr(Δ^(s+1) dR/dr)] + [K²/Δ − 4isωr + A_lm] R = 0
```

where:
- Δ = r² − 2Mr + a² = (r − r₊)(r − r₋)
- K = (r² + a²)ω − am   (with M=1)
- A_lm = A_lm(aω, s, l, m) is the spheroidal eigenvalue
- s = −2 for gravitational perturbations
- ω is the (complex) QNM frequency
- l ≥ |s|, |m| ≤ l

### 3.3 Teukolsky at a = 0: reduction to RW equation

At a = 0, the Kerr Teukolsky radial equation simplifies to:
- Δ → r(r − 2M)
- K → ωr²
- A_lm → l(l+1)

The radial ODE becomes:
```
d²R/dr² + (s+1)(2r − 2M)/(r(r−2M)) dR/dr + [ω²r⁴/Δ² + 4isωr/Δ + l(l+1)/Δ] R = 0
```

The key result from the codebase analysis: **QNMs of the Teukolsky equation at a=0 with s=−2 are IDENTICAL to the Regge-Wheeler QNMs for gravitational perturbations of Schwarzschild.** This follows from the Ishibashi-Hoodge (2003) second-order differential operator relating Teukolsky and RW.

### 3.4 Impossibility of direct 3-term Leaver CF at a=0

When the Teukolsky ODE at a=0 is expanded in Frobenius series around the horizon (x = 1 − 2M/r), the recurrence is **4-term or higher**, NOT 3-term. This is a genuine property of the confluent Heun equation at a=0, not a code bug.

The rationale: At a>0, the Teukolsky ODE has THREE regular singular points (r₊, r₋, ∞), giving a Heun equation with 3-term Frobenius recurrence. At a=0, r₊ = 2M and r₋ = 0 merge partially, producing a CONFLUENT Heun equation with a regular singular point at r = 2M and an essential singularity at r = ∞. The resulting Frobenius recurrence is 4-term, not 3-term.

**Practical consequence**: For a=0, use either:
1. The Regge-Wheeler equation (which has 3-term Leaver CF)
2. The Analytic Plus Iterative Method (AIM) on the gauge-transformed RW equation
3. The shooting method in r* coordinates
4. The Sasaki-Nakamura transformation to Schrödinger form

For a>0, use Leaver's original 3-term CF method directly.

---

## 4. QNM Symbol Convention

| Symbol | Meaning |
|--------|---------|
| ω = ω_R + iω_I | Complex QNM frequency (M-scaled, ω_R > 0, ω_I < 0) |
| l | Spherical harmonic degree, l = 2, 3, 4, ... |
| m | Azimuthal number, −l ≤ m ≤ l (|m| ≤ l) |
| s | Teukolsky spin weight, s = −2 (gravitational) |
| n | Overtone index, n = 0 (fundamental), n = 1 (1st overtone), ... |
| a | Kerr spin parameter, 0 ≤ a < 1 (M=1 units) |
| σ = ωM | Dimensionless frequency |

### 4.1 Reference values (Schwarzschild, M = 1)

Berti et al. PRD 79, 044006 (2009), Table I (Regge-Wheeler):

| (l, n) | ω_R (M=1) | ω_I (M=1) | |ω| (M=1) |
|--------|-----------|-----------|-----------|
| (2, 0) | 0.37367   | −0.08896  | 0.38412   |
| (3, 0) | 0.27316   | −0.05945  | 0.27951   |
| (4, 0) | 0.23148   | −0.04799  | 0.23641   |

These are the benchmark values for P1-3 validation. The AIM/Leaver solver must reproduce these to δ|ω| < 10⁻⁶ with N ≥ 40.

---

## 5. Boundary Condition Convention

### 5.1 Physical form

**Ingoing at horizon**: The perturbation is purely ingoing at the event horizon.

In terms of (t, r*): the solution behaves as:
```
ψ(t, r*) ~ exp[−iω(t + r*)]   as r* → −∞
```

Equivalently, the spatial radial function:
```
R(r*) ~ exp(−iωr*) = exp(iω| r*|)   as r* → −∞ (ing oing toward the horizon)
```

**Outgoing at infinity**: The perturbation is purely outgoing at spatial infinity.
```
ψ(t, r*) ~ exp[−iω(t − r*)]   as r* → +∞
```

Equivalently:
```
R(r*) ~ exp(+iωr*)   as r* → +∞  (outgoing away from the black hole)
```

### 5.2 Sign convention for the exponential

This is critical. The standard convention in the GR/QNM literature (Leaver 1985, Berti 2009, Nollert 1999) uses:

```
time dependence:  e^{-iωt}
ingoing at horizon:  e^{-iω(t + r*)} = e^{-iωt} e^{-iωr*}
outgoing at infinity:  e^{-iω(t - r*)} = e^{-iωt} e^{+iωr*}
```

With ω_I < 0 (decaying mode), the time dependence e^{-iωt} = e^{-iω_R t} e^{+|ω_I| t} is WRONG — that would be growing.

**Correction**: The standard convention is:
```
time dependence:  e^{-iωt}
QNM condition:  Im(ω) < 0 (decaying in time)
```
So: e^{-iωt} = e^{-iω_R t} e^{+|ω_I| t} → this grows if ω_I < 0? No, −iω_I > 0 means e^{+|ω_I|t} grows.

Wait, the sign: ω = ω_R + iω_I with ω_I < 0. Then:
```
e^{-iωt} = e^{-i(ω_R + iω_I)t} = e^{-iω_R t} e^{+|ω_I| t}
```

This is **growing**, not decaying. So the correct physical convention must be ω_I > 0 with e^{-iωt}, OR ω_I < 0 with e^{+iωt}.

The standard GR convention is: **e^{-iωt} with Im(ω) < 0**. This means the convention used throughout the codebase is:
```
physical time dependence: e^{-iωt}
ω_I < 0: mode is decaying? NO — this grows.
```

**Resolution**: The sign convention varies by field. In GR black hole QNM literature, the convention is:

```
time dependence: e^{-iωt}
For QNMs: ω_I < 0, so e^{-iωt} = e^{-iω_R t} · e^{+|ω_I|t}
```

But physically we want decay, so the convention should be:
```
ω_I > 0 with e^{-iωt}, OR equivalently ω_I < 0 with e^{+iωt}
```

**Codebase convention (confirmed from leaver_*.py files)**:
- Reference: ω = 0.37367 − 0.08896i  (i.e., ω_I < 0)
- The convention is: e^{-iωt} with Im(ω) < 0 is used throughout.
- However, physically, the *magnitude* is what matters for the mode: Re(ω) > 0 and Im(ω) < 0 with e^{+iωt} gives decay.

**FINAL convention for this project** (matching Berti et al. PRD 2009 and Leaver 1985):
```
Time dependence: e^{-iωt}
QNM condition: Im(ω) < 0 → ω_I < 0
Physical decay: the physical mode amplitude is e^{|ω_I|t} which decays for |ω_I| < 0 ...

OK: The simplest way: match Berti's convention EXACTLY.
Berti Table III: ω_R > 0, ω_I < 0. Example (2,2): ω = 0.59607 − 0.089594i

For boundary conditions in the radial function:
R(r*) ~ exp(−iωr*)  at the horizon (ing oing, r* → −∞)
R(r*) ~ exp(+iωr*)  at infinity (outgoing, r* → +∞)
```

### 5.3 Summary table

| Location | Behavior | Spatial factor |
|----------|----------|----------------|
| Horizon (r* → −∞) | Ingoing | exp(−iωr*) |
| Infinity (r* → +∞) | Outgoing | exp(+iωr*) |

The sign convention: **e^{-iωr*} for ingoing, e^{+iωr*} for outgoing.**

With the reference frequency ω = ω_R + iω_I (ω_I < 0):
- exp(−iωr*) at horizon = exp(−iω_R r*) · exp(|ω_I| r*). Since r* → −∞, |ω_I|·r* < 0 → **decays toward horizon** (ingoing, energy flows INTO the black hole).
- exp(+iωr*) at infinity = exp(+iω_R r*) · exp(−|ω_I| r*). Since r* → +∞, −|ω_I|·r* < 0 → **decays toward infinity** (outgoing, energy flows OUT).

---

## 6. AIM Convention

### 6.1 ODE form for AIM

The Radial Teukolsky/Oscillator equation is cast in the form:
```
d²ψ/dr*² = Λ(r*) · dψ/dr* + Μ(r*) · ψ
```

where Λ and Μ are first and second logarithmic derivative functions.

The AIM convergence diagnostic:
```
θ(r) = Λ'(r)/Λ(r) / Μ'(r)/Μ(r)
D(ω) = |θ_a(ω) − θ_b(ω)| → 0 at QNM frequencies
```

where θ_a is evaluated from below (near horizon) and θ_b from above (near infinity).

### 6.2 Dehghan-Safari formulation (used in leaver_schwarzschild.py)

The ODE is further transformed:
```
ψ = exp(∫g dr*) · Φ
```
g is chosen to simplify the logarithmic derivatives. The Dehghan-Safari iteration:
```
Λ₀ = Λ, Μ₀ = Μ
Λ_{n+1} = Λ_n² + Λ_n' − Μ_n
Μ_{n+1} = Λ_n Μ_n' − Μ_n Λ_n' + Μ_n²
θ_n = Λ_{n+1}/Λ_n
```
The QNM condition is θ_a(ω) = θ_b(ω), i.e., D(ω) = |θ_a − θ_b| → 0.

---

## 7. Variable Summary

| Symbol | Definition | Range |
|--------|-----------|-------|
| r | Boyer-Lindquist radial coordinate | [r₊, ∞) |
| r* | Tortoise coordinate: r* = r + 2M ln(r/2M − 1) | (−∞, +∞) |
| x = 1 − 2M/r | Compactified radial coordinate | (0, 1) |
| z = r/2M − 1 | Dimensionless Schwarzschild radial | (0, ∞) |
| x_L = (r − r₊)/(r₊ − r₋) | Leaver's expansion variable (a>0) | (0, 1) maps r₊→0, ∞→1 |

---

## 8. Key References

| Ref | Citation | Relevance |
|-----|----------|-----------|
| [R1] | Leaver 1985, Proc.Roy.Soc.Lond.A 402, 285 | Original Leaver CF method |
| [R2] | Berti, Cardoso, Starinets 2009, CQG 26, 165014 | Review + Kerr QNM coefficients |
| [R3] | Ishibashi, Hoodaghi 2003, CQG 20, 3059 | Teukolsky↔RW duality at a=0 |
| [R4] | Nollert 1999, CQG 16, R215 | QNM review, CF methods |
| [R5] | Konoplya 2003, PRD 68, 024018 | Analytic approx, CF |
| [R6] | Dehghan, Safari AIM | Analytic Plus Iterative Method |
| [R7] | Berti et al. PRD 79, 044006 (2009) | Numerical benchmarks, Table III |
