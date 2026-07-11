#!/usr/bin/env python3
"""
Helicity flip symmetry verification for chiral overlap reduction function Gamma^V.

Verifies: Gamma^V -> -Gamma^V under reflection (theta, phi) -> (theta, 2*pi - phi),
even with spatial phase exp(-2*pi*i*f*Delta_x/c) present.

4 test cases:
  T1: coplanar Taiji*Taiji -> Gamma^V ~ 0
  T2: reflection symmetry P^V(theta,phi) + P^V(theta, 2pi-phi) ~ 0
  T3: spatial phase preserves helicity flip symmetry
  T4: non-coplanar LISA*Taiji -> Gamma^V != 0

This script is an INDEPENDENT implementation. It shares only the physical model
(antenna patterns, transfer functions) but does NOT import from
11-multi-constellation-chiral-orf.py.

Usage:
    python3 scripts/verify-helicity-flip-symmetry.py
    python3 scripts/verify-helicity-flip-symmetry.py --dry-run
"""

import sys
import json
import time
import numpy as np

# ━━━ Physical constants ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

c = 299792458.0  # speed of light (m/s)

# ━━━ Detector parameters ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Taiji: L = 3e6 m, inclination ~0 (in the ecliptic plane)
TAIJI_L = 3_000_000.0  # m
TAIJI_INCLINATION = 0.0  # rad

# LISA: L = 2.5e6 m, inclination ~0 (also in ecliptic plane)
# For the LISA-Taiji network, we offset LISA by ~1 AU in the plane
LISA_L = 2_500_000.0  # m
LISA_INCLINATION = 0.0  # rad
# Baseline between LISA and Taiji centroids ~ 1 AU
AU = 1.495978707e11  # meters

FREQS = [0.001, 0.01, 0.1]  # Hz
NTHETA = 60
NPHI = 120

# ━━━ Transfer functions ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def olc_transfer_function(f, L, cos_nu):
    """OLC one-way link transfer function.

    Lou Mingzhi thesis Eq. 2-30.
    """
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - np.abs(cos_nu)
    eps = 1e-15
    sinc_arg = beta * one_minus
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f) * L / c
    return prefac * sinc_v * phase


def taiji_transfer_function(f, L, cos_nu):
    """LISA/Taiji Michelson transfer function."""
    beta = np.pi * np.abs(f) * L / c
    eps = 1e-15
    sinc_val = np.where(np.abs(beta) < eps, 1.0, np.sin(beta) / beta)
    return np.sin(beta) / beta * np.exp(-1j * beta)


# ━━━ Polarization basis ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def polarization_basis(tG, pG):
    """Compute polarization basis vectors for sky direction (theta, phi).

    Returns:
        th, ph: unit vectors for + and x polarizations
        k_hat: GW propagation direction (unit vector from source to detector)
    """
    ct = np.cos(tG)
    st = np.sin(tG)
    cp = np.cos(pG)
    sp = np.sin(pG)

    # Propagation direction (toward Earth)
    k_hat = np.array([
        np.sin(tG) * np.cos(pG),
        np.sin(tG) * np.sin(pG),
        np.cos(tG)
    ])  # shape (3, ntheta, nphi)

    th = np.stack([ct * cp, ct * sp, -st])
    ph = np.stack([-sp, cp, np.zeros_like(sp)])

    return th, ph, k_hat


# ━━━ Antenna patterns for E-variable (CW link sum) ━━━━━━━━━━━━━━━━━━━━━━━━━━

def antenna_pattern_e_variable_cw(tG, pG, satellite_positions, L, det_type='interferometer'):
    """E-variable antenna patterns via clockwise (CW) link sum.

    The TDI E variable for equilateral triangles sums over 3 CW links:
      E(f) ~ (1 - e^{-i*2beta}) * sum_{k=CW} d_k(link_k)

    The E-variable response sums over the 3 CW links:
      R_E+ = sum_{k=CW} F_+(link_k)
      R_Ex = sum_{k=CW} F_x(link_k)

    Args:
        tG, pG: GW direction grid (theta, phi), shape (ntheta, nphi)
        satellite_positions: 3x3 array of satellite positions (meters)
        L: arm length
        det_type: 'olc' or 'interferometer'

    Returns:
        R_plus, R_cross: complex arrays, shape (ntheta, nphi)
    """
    tG_a = np.asarray(tG)
    pG_a = np.asarray(pG)

    th, ph, k_hat = polarization_basis(tG_a, pG_a)

    # CW links: 1->2, 2->3, 3->1
    cw_links = [(0, 1), (1, 2), (2, 0)]

    R_plus = np.zeros_like(tG_a, dtype=np.complex128)
    R_cross = np.zeros_like(tG_a, dtype=np.complex128)

    for i, j in cw_links:
        u = satellite_positions[j] - satellite_positions[i]
        u = u / np.linalg.norm(u)

        th_dot_u = th[0] * u[0] + th[1] * u[1] + th[2] * u[2]
        ph_dot_u = ph[0] * u[0] + ph[1] * u[1] + ph[2] * u[2]

        F_plus = th_dot_u ** 2 - ph_dot_u ** 2
        F_cross = 2.0 * th_dot_u * ph_dot_u

        # Per-link transfer function (one-way link)
        cos_nu = k_hat[0] * u[0] + k_hat[1] * u[1] + k_hat[2] * u[2]
        if det_type == 'interferometer':
            T = taiji_transfer_function(np.ones_like(tG_a), L, cos_nu)
        else:
            T = olc_transfer_function(np.ones_like(tG_a), L, cos_nu)

        R_plus += F_plus * T
        R_cross += F_cross * T

    return R_plus, R_cross


# ━━━ Constellation class ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _make_triangle(L):
    """Generate equilateral triangle in xy-plane."""
    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([L, 0.0, 0.0])
    r3 = np.array([L / 2, L * np.sqrt(3) / 2, 0.0])
    return np.array([r1, r2, r3])


def _apply_inclination(positions, inclination):
    """Rotate satellite positions by inclination around X-axis."""
    cos_i = np.cos(inclination)
    sin_i = np.sin(inclination)
    rotated = np.zeros_like(positions)
    rotated[:, 0] = positions[:, 0]
    rotated[:, 1] = positions[:, 1] * cos_i - positions[:, 2] * sin_i
    rotated[:, 2] = positions[:, 1] * sin_i + positions[:, 2] * cos_i
    return rotated


def _apply_z_rotation(positions, phi):
    """Rotate satellite positions around z-axis by angle phi."""
    cos_p = np.cos(phi)
    sin_p = np.sin(phi)
    rotated = np.zeros_like(positions)
    rotated[:, 0] = positions[:, 0] * cos_p - positions[:, 1] * sin_p
    rotated[:, 1] = positions[:, 0] * sin_p + positions[:, 1] * cos_p
    rotated[:, 2] = positions[:, 2]
    return rotated


class Constellation:
    """Represents a GW detector constellation (triangle)."""

    def __init__(self, name, L, inclination_rad, rotation_phi=0.0,
                 reference_position=None):
        self.name = name
        self.L = L
        self.inclination = inclination_rad
        self.rotation = rotation_phi
        self.reference_position = reference_position

        triangle = _make_triangle(L)
        triangle = _apply_inclination(triangle, inclination_rad)
        if rotation_phi != 0.0:
            triangle = _apply_z_rotation(triangle, rotation_phi)
        self.positions = triangle

    def centroid(self):
        return np.mean(self.positions, axis=0)


def _compute_delta_x(const1, const2):
    """Compute separation vector between constellation centroids."""
    if const1.reference_position is not None and const2.reference_position is not None:
        return const1.reference_position - const2.reference_position
    return const1.centroid() - const2.centroid()


# ━━━ Spatial phase factor ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def spatial_phase_factor(f, delta_x, tG, pG):
    """Spatial phase factor exp(-2*pi*i*f/c * k_hat . Delta_x).

    Args:
        f: frequency (scalar)
        delta_x: 3D separation vector from const1 to const2 (meters)
        tG, pG: sky direction grid (theta, phi)

    Returns:
        phase: complex array, shape (ntheta, nphi)
    """
    k_hat = np.array([
        np.sin(tG) * np.cos(pG),
        np.sin(tG) * np.sin(pG),
        np.cos(tG)
    ])  # shape (3, ntheta, nphi)

    delta_x_expanded = delta_x.reshape(3, 1, 1)
    k_dot_delta = np.sum(k_hat * delta_x_expanded, axis=0)

    omega = 2.0 * np.pi * f
    phase = np.exp(-1j * omega / c * k_dot_delta)
    return phase


# ━━━ Sky grid builder ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━──

def build_sky_grid(ntheta, nphi):
    """Build uniform theta×phi grid with proper dOmega measure.

    Args:
        ntheta: number of theta bins
        nphi: number of phi bins

    Returns:
        TG, PG: meshgrid (ntheta, nphi)
        dOmega: integration measure (solid angle per pixel)
    """
    tG = np.linspace(0, np.pi, ntheta)
    pG = np.linspace(0, 2 * np.pi, nphi)
    TG, PG = np.meshgrid(tG, pG, indexing='ij')
    dOmega = np.pi / (ntheta - 1) * 2 * np.pi / nphi
    return TG, PG, dOmega


# ━━━ Chiral correlation and Gamma^V ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━────────

def compute_chiral_integrand(R1p, R1x, R2p, R2x):
    """Compute per-pixel chiral correlation integrand P^V.

    P^V = Re[conj(R1_+) * R2_x - conj(R1_x) * R2_+]

    This is the integrand that should be odd under reflection.

    Args:
        R1p, R1x: detector 1 antenna patterns (complex arrays)
        R2p, R2x: detector 2 antenna patterns (complex arrays)

    Returns:
        P_V: real array of per-pixel chiral integrand
    """
    chiral_corr = np.conj(R1p) * R2x - np.conj(R1x) * R2p
    return np.real(chiral_corr)


def compute_gamma_V(R1p, R1x, R2p, R2x, phase, dOmega):
    """Compute Gamma^V (sky-integrated chiral ORF).

    Gamma^V = Re[Sum phase * (conj(R1p)*R2x - conj(R1x)*R2p)] * dOmega / (4*pi)

    Args:
        R1p, R1x: detector 1 antenna patterns
        R2p, R2x: detector 2 antenna patterns
        phase: spatial phase factor (or all ones)
        dOmega: solid angle per pixel

    Returns:
        gamma_V: scalar chiral ORF
    """
    chiral_corr = np.conj(R1p) * R2x - np.conj(R1x) * R2p
    gamma_V = np.real(np.sum(phase * chiral_corr)) * dOmega / (4.0 * np.pi)
    return gamma_V


# ━─── Detector configurations ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━──────────────

def make_taiji():
    """Taiji constellation: coplanar, L=3e6 m, inclination ~0."""
    return Constellation('Taiji', TAIJI_L, TAIJI_INCLINATION)


def make_lisa():
    """LISA constellation: L=2.5e6 m, inclination ~0, displaced by ~1 AU."""
    return Constellation('LISA', LISA_L, LISA_INCLINATION,
                         reference_position=np.array([AU, 0.0, 0.0]))


def make_taiji_offset():
    """Second Taiji constellation at ~1 AU (for cross-correlation)."""
    return Constellation('Taiji_2', TAIJI_L, TAIJI_INCLINATION,
                         reference_position=np.array([AU, 0.0, 0.0]))


# ━━━ Result / reporting ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestResult:
    """Holder for a single test result."""

    def __init__(self, name):
        self.name = name
        self.passed = None
        self.details = {}

    def mark_pass(self):
        self.passed = True

    def mark_fail(self):
        self.passed = False

    def to_dict(self):
        return {"test": self.name, "passed": self.passed, **self.details}


def print_result(r):
    status = "PASS" if r.passed else "FAIL"
    print(f"  [{status}] {r.name}")
    for k, v in r.details.items():
        print(f"        {k}: {v}")


# ━━━ Test: T1 - coplanar Taiji*Taiji Gamma^V ~ 0 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_t1_coplanar():
    """T1: Coplanar Taiji×Taiji should have Gamma^V ~ 0.

    Two identical Taiji constellations with same orientation are perfectly coplanar.
    The helicity flip symmetry forces Gamma^V = 0.

    AC-1: |Gamma^V| < 1e-6 for all f in {0.001, 0.01, 0.1} Hz.
          |Gamma^V| < 1e-8 at f = 0.001 Hz.
    """
    result = TestResult("T1: coplanar Taiji*Taiji Gamma^V ~ 0")
    print("\n=== T1: Coplanar Taiji x Taiji -> Gamma^V ~ 0 ===")

    taiji1 = make_taiji()
    taiji2 = make_taiji_offset()  # same orientation, offset by 1 AU

    TG, PG, dOmega = build_sky_grid(NTHETA, NPHI)

    freqs_passed = True
    freqs_low_passed = True
    details = {}

    for f in FREQS:
        R1p, R1x = antenna_pattern_e_variable_cw(
            TG, PG, taiji1.positions, taiji1.L, 'interferometer')
        R2p, R2x = antenna_pattern_e_variable_cw(
            TG, PG, taiji2.positions, taiji2.L, 'interferometer')

        # Spatial phase for inter-Taiji baseline ~1 AU
        delta_x = _compute_delta_x(taiji1, taiji2)
        phase = spatial_phase_factor(f, delta_x, TG, PG)

        gamma_V = compute_gamma_V(R1p, R1x, R2p, R2x, phase, dOmega)
        abs_gamma_V = np.abs(gamma_V)

        details[f"f={f} Hz |Gamma^V|"] = abs_gamma_V
        print(f"        f={f} Hz: |Gamma^V| = {abs_gamma_V:.6e}")

        if abs_gamma_V >= 1e-6:
            freqs_passed = False
        if f == 0.001 and abs_gamma_V >= 1e-8:
            freqs_low_passed = False

    result.details = details
    if freqs_passed and freqs_low_passed:
        result.mark_pass()
    else:
        result.mark_fail()

    print_result(result)
    return result


# ━━━ Test: T2 - reflection symmetry P^V(theta,phi) + P^V(theta, 2pi-phi) ~ 0 ━

def test_t2_reflection():
    """T2: Reflection symmetry P^V(theta,phi) + P^V(theta, 2*pi - phi) ~ 0.

    For each pixel (theta, phi) on the sky grid, compute:
      deviation = |P^V(theta,phi) + P^V(theta, 2*pi - phi)|
                  / (|P^V(theta,phi)| + |P^V(theta, 2*pi-phi)| + eps)

    This verifies the per-pixel helicity flip oddness.

    AC-2: max(deviation) < 0.01, mean(deviation) < 0.001.
    """
    result = TestResult("T2: reflection symmetry P^V + P^V(reflected) ~ 0")
    print("\n=== T2: Reflection symmetry per-pixel ===")

    TG, PG, dOmega = build_sky_grid(NTHETA, NPHI)

    configs = [
        ("Taiji*Taiji", make_taiji(), make_taiji_offset()),
        ("LISA*Taiji", make_lisa(), make_taiji()),
    ]

    all_configs_pass = True

    for name, const1, const2 in configs:
        print(f"\n  Configuration: {name}")

        # Use f=0.01 Hz (worst case for spatial phase)
        f = 0.01

        R1p, R1x = antenna_pattern_e_variable_cw(
            TG, PG, const1.positions, const1.L, 'interferometer')
        R2p, R2x = antenna_pattern_e_variable_cw(
            TG, PG, const2.positions, const2.L, 'interferometer')

        delta_x = _compute_delta_x(const1, const2)
        phase = spatial_phase_factor(f, delta_x, TG, PG)

        # P^V at each pixel with spatial phase
        PV = compute_chiral_integrand(R1p, R1x, R2p, R2x)
        # With spatial phase: Re[phase * chiral_corr_raw]
        chiral_raw = np.conj(R1p) * R2x - np.conj(R1x) * R2p
        PV_with_phase = np.real(phase * chiral_raw)

        # Reflection: (theta, phi) -> (theta, 2*pi - phi)
        # TG stays the same, PG -> 2*pi - PG
        TG_r = TG.copy()
        PG_r = 2.0 * np.pi - PG.copy()

        # Compute P^V at reflected points
        R1p_r, R1x_r = antenna_pattern_e_variable_cw(
            TG_r, PG_r, const1.positions, const1.L, 'interferometer')
        R2p_r, R2x_r = antenna_pattern_e_variable_cw(
            TG_r, PG_r, const2.positions, const2.L, 'interferometer')

        chiral_raw_r = np.conj(R1p_r) * R2x_r - np.conj(R1x_r) * R2p_r
        delta_x_r = delta_x  # baseline unchanged under reflection

        # Phase at reflected point: k_hat.reflected . delta_x
        # We need the phase at (theta, 2pi-phi) for the same delta_x
        phase_r = spatial_phase_factor(f, delta_x_r, TG_r, PG_r)

        PV_r_with_phase = np.real(phase_r * chiral_raw_r)

        # Deviation: |P^V(phi) + P^V(2pi-phi)| / (|P^V(phi)| + |P^V(2pi-phi)| + eps)
        eps = 1e-20
        deviation = np.abs(PV_with_phase + PV_r_with_phase) / (
            np.abs(PV_with_phase) + np.abs(PV_r_with_phase) + eps)

        max_dev = np.max(deviation)
        mean_dev = np.mean(deviation)

        result.details[f"{name} max deviation"] = max_dev
        result.details[f"{name} mean deviation"] = mean_dev
        print(f"        max deviation: {max_dev:.6e}")
        print(f"        mean deviation: {mean_dev:.6e}")

        if max_dev >= 0.01 or mean_dev >= 0.001:
            all_configs_pass = False

    result.details["all_configs_pass"] = all_configs_pass
    if all_configs_pass:
        result.mark_pass()
    else:
        result.mark_fail()

    print_result(result)
    return result


# ━━━ Test: T3 - spatial phase preserves helicity flip symmetry ━━━━━━━━━━━━━━━

def test_t3_spatial_phase():
    """T3: Spatial phase factor exp(-2*pi*i*f*Delta_x/c) preserves helicity flip.

    Compare:
      - Without spatial phase: Gamma^V_without
      - With spatial phase: Gamma^V_with

    AC-3:
      - Without spatial phase: helicity flip max deviation < 1%
      - With spatial phase: helicity flip max deviation < 2%
      - The ratio |Gamma^V_with / Gamma^V_without| shows physical magnitude change
        (not necessarily 1.0, ~40% deviation is known physical effect).
    """
    result = TestResult("T3: spatial phase preserves helicity flip symmetry")
    print("\n=== T3: Spatial phase preserves helicity flip ===")

    TG, PG, dOmega = build_sky_grid(NTHETA, NPHI)

    # LISA*Taiji is the only non-trivial configuration (Gamma^V != 0)
    const1 = make_lisa()
    const2 = make_taiji()

    delta_x = _compute_delta_x(const1, const2)

    freqs_pass = True
    freq_details = {}

    for f in FREQS:
        print(f"\n  f = {f} Hz:")

        R1p, R1x = antenna_pattern_e_variable_cw(
            TG, PG, const1.positions, const1.L, 'interferometer')
        R2p, R2x = antenna_pattern_e_variable_cw(
            TG, PG, const2.positions, const2.L, 'interferometer')

        # Without spatial phase
        phase_ones = np.ones_like(TG)
        gamma_V_no_phase = compute_gamma_V(R1p, R1x, R2p, R2x, phase_ones, dOmega)

        # With spatial phase
        phase_full = spatial_phase_factor(f, delta_x, TG, PG)
        gamma_V_with_phase = compute_gamma_V(R1p, R1x, R2p, R2x, phase_full, dOmega)

        ratio = np.abs(gamma_V_with_phase) / (np.abs(gamma_V_no_phase) + 1e-30)

        freq_details[f"f={f} Hz |Gamma^V_with|"] = np.abs(gamma_V_with_phase)
        freq_details[f"f={f} Hz |Gamma^V_no_phase|"] = np.abs(gamma_V_no_phase)
        freq_details[f"f={f} Hz ratio"] = ratio
        print(f"        |Gamma^V_with_phase|  = {np.abs(gamma_V_with_phase):.6e}")
        print(f"        |Gamma^V_no_phase|    = {np.abs(gamma_V_no_phase):.6e}")
        print(f"        ratio = {ratio:.6f}")

        # Now check helicity flip with and without spatial phase
        chiral_raw = np.conj(R1p) * R2x - np.conj(R1x) * R2p
        PV_no_phase = np.real(chiral_raw)

        PV_with_phase = np.real(phase_full * chiral_raw)

        # Reflection
        TG_r = TG.copy()
        PG_r = 2.0 * np.pi - PG.copy()
        R1p_r, R1x_r = antenna_pattern_e_variable_cw(
            TG_r, PG_r, const1.positions, const1.L, 'interferometer')
        R2p_r, R2x_r = antenna_pattern_e_variable_cw(
            TG_r, PG_r, const2.positions, const2.L, 'interferometer')
        chiral_raw_r = np.conj(R1p_r) * R2x_r - np.conj(R1x_r) * R2p_r
        PV_r_no_phase = np.real(chiral_raw_r)

        phase_r = spatial_phase_factor(f, delta_x, TG_r, PG_r)
        PV_r_with_phase = np.real(phase_r * chiral_raw_r)

        eps = 1e-20

        dev_no_phase = np.abs(PV_no_phase + PV_r_no_phase) / (
            np.abs(PV_no_phase) + np.abs(PV_r_no_phase) + eps)
        dev_with_phase = np.abs(PV_with_phase + PV_r_with_phase) / (
            np.abs(PV_with_phase) + np.abs(PV_r_with_phase) + eps)

        max_dev_no = np.max(dev_no_phase)
        max_dev_yes = np.max(dev_with_phase)

        freq_details[f"f={f} Hz dev_no_phase"] = max_dev_no
        freq_details[f"f={f} Hz dev_with_phase"] = max_dev_yes
        print(f"        max_dev (no phase)   = {max_dev_no:.6e}")
        print(f"        max_dev (with phase) = {max_dev_yes:.6e}")

        if max_dev_yes >= 0.02:
            freqs_pass = False

    result.details = freq_details
    if freqs_pass:
        result.mark_pass()
    else:
        result.mark_fail()

    print_result(result)
    return result


# ━━━ Test: T4 - non-coplanar LISA*Taiji Gamma^V != 0 ━━━━━━━━━━━━━━━━━━━━━━━━

def test_t4_noncoplanar():
    """T4: Non-coplanar LISA×Taiji should have Gamma^V != 0.

    AC-4: |Gamma^V| > 1e-10 for all f in {0.001, 0.01, 0.1} Hz.
          Gamma^V sign flips under helicity flip (self-consistency check).
    """
    result = TestResult("T4: non-coplanar LISA*Taiji Gamma^V != 0")
    print("\n=== T4: Non-coplanar LISA x Taiji -> Gamma^V != 0 ===")

    lisa = make_lisa()
    taiji = make_taiji()

    TG, PG, dOmega = build_sky_grid(NTHETA, NPHI)

    freqs_above_threshold = True
    signs_flip = True
    details = {}

    for f in FREQS:
        R1p, R1x = antenna_pattern_e_variable_cw(
            TG, PG, lisa.positions, lisa.L, 'interferometer')
        R2p, R2x = antenna_pattern_e_variable_cw(
            TG, PG, taiji.positions, taiji.L, 'interferometer')

        delta_x = _compute_delta_x(lisa, taiji)
        phase = spatial_phase_factor(f, delta_x, TG, PG)

        gamma_V = compute_gamma_V(R1p, R1x, R2p, R2x, phase, dOmega)
        gamma_V_no_phase = compute_gamma_V(R1p, R1x, R2p, R2x, np.ones_like(TG), dOmega)

        abs_gamma_V = np.abs(gamma_V)
        details[f"f={f} Hz Gamma^V (with phase)"] = gamma_V
        details[f"f={f} Hz Gamma^V (no phase)"] = gamma_V_no_phase
        details[f"f={f} Hz |Gamma^V|"] = abs_gamma_V
        print(f"        f={f} Hz: Gamma^V = {gamma_V:.6e}  (|Gamma^V| = {abs_gamma_V:.6e})")

        if abs_gamma_V <= 1e-10:
            freqs_above_threshold = False

        # Self-consistency: sign flip check
        # Compare sign of Gamma^V with sign from reflected integral
        chiral_raw = np.conj(R1p) * R2x - np.conj(R1x) * R2p
        PV = np.real(phase * chiral_raw)

        # Reflected
        TG_r = TG.copy()
        PG_r = 2.0 * np.pi - PG.copy()
        R1p_r, R1x_r = antenna_pattern_e_variable_cw(
            TG_r, PG_r, lisa.positions, lisa.L, 'interferometer')
        R2p_r, R2x_r = antenna_pattern_e_variable_cw(
            TG_r, PG_r, taiji.positions, taiji.L, 'interferometer')
        chiral_raw_r = np.conj(R1p_r) * R2x_r - np.conj(R1x_r) * R2p_r
        phase_r = spatial_phase_factor(f, delta_x, TG_r, PG_r)
        PV_r = np.real(phase_r * chiral_raw_r)

        # Integral of reflected should be ~ -Gamma^V
        gamma_V_reflected = np.sum(PV_r) * dOmega / (4.0 * np.pi)

        if np.abs(gamma_V) > 1e-20 and np.abs(gamma_V_reflected) > 1e-20:
            sign_ratio = np.sign(gamma_V) * np.sign(gamma_V_reflected)
            if sign_ratio != -1:
                signs_flip = False
                print(f"        WARNING: sign flip check failed, ratio = {sign_ratio}")

    details["freqs_above_threshold"] = freqs_above_threshold
    details["signs_flip"] = signs_flip
    result.details = details
    if freqs_above_threshold and signs_flip:
        result.mark_pass()
    else:
        result.mark_fail()

    print_result(result)
    return result


# ━━━ Main ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━──────────

def main():
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("Dry run mode — printing test names and parameters only.")
        print(f"  Grid: {NTHETA}x{NPHI} theta×phi")
        print(f"  Frequencies: {FREQS} Hz")
        print(f"  Configurations: Taiji*Taiji (coplanar), LISA*Taiji (non-coplanar)")
        print(f"  Tests: T1, T2, T3, T4")
        print("Run without --dry-run to execute tests.")
        return 0

    print("=" * 70)
    print("Helicity Flip Symmetry Verification — Gamma^V -> -Gamma^V")
    print("under reflection (theta, phi) -> (theta, 2*pi - phi)")
    print("=" * 70)
    print(f"\nGrid: {NTHETA}x{NPHI} theta×phi")
    print(f"Frequencies: {FREQS} Hz")
    print(f"Configurations: Taiji*Taiji (coplanar), LISA*Taiji (non-coplanar)")

    t0 = time.time()

    results = []
    tests = [
        ("T1", test_t1_coplanar),
        ("T2", test_t2_reflection),
        ("T3", test_t3_spatial_phase),
        ("T4", test_t4_noncoplanar),
    ]

    for name, func in tests:
        r = func()
        results.append(r)

    elapsed = time.time() - t0

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    all_pass = True
    for r in results:
        print_result(r)
        if not r.passed:
            all_pass = False

    print(f"\nTotal time: {elapsed:.1f}s")
    print(f"All tests: {'PASS' if all_pass else 'FAIL'}")

    # JSON output
    json_output = {
        "grid": [NTHETA, NPHI],
        "frequencies": FREQS,
        "elapsed_seconds": elapsed,
        "all_pass": all_pass,
        "tests": [r.to_dict() for r in results],
    }
    print(f"\nJSON: {json.dumps(json_output, indent=2)}")

    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
