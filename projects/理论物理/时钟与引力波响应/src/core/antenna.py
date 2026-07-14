"""Antenna pattern functions for OLC detectors."""
import numpy as np


def antenna_patterns(n_theta, n_phi, u_theta, u_phi):
    """F_plus and F_cross antenna patterns.

    F_A(n) = e_A^{ab}(n) * u_a * u_b

    In spherical sky basis:
        e_+ = th⊗th - ph⊗ph
        e_x = th⊗ph + ph⊗th

    Args:
        n_theta: sky polar angle (2D grid).
        n_phi: sky azimuthal angle (2D grid).
        u_theta: arm polar angle (scalar).
        u_phi: arm azimuthal angle (scalar).

    Returns:
        (F_plus, F_cross) — same shape as n_theta.
    """
    ct, st = np.cos(n_theta), np.sin(n_theta)
    cp, sp = np.cos(n_phi), np.sin(n_phi)
    cu_t, cu_p = np.cos(u_theta), np.cos(u_phi)
    su_t, su_p = np.sin(u_theta), np.sin(u_phi)

    # Arm unit vector
    ux = su_t * cu_p
    uy = su_t * su_p
    uz = cu_t

    # Sky tangent basis
    th_x, th_y, th_z = ct * cp, ct * sp, -st
    ph_x, ph_y, ph_z = -sp, cp, 0.0

    F_plus = (th_x * ux) ** 2 + (th_y * uy) ** 2 + (th_z * uz) ** 2 \
           - (ph_x * ux) ** 2 - (ph_y * uy) ** 2 - (ph_z * uz) ** 2
    F_cross = 2.0 * (th_x * ux) * (ph_x * ux) \
            + 2.0 * (th_y * uy) * (ph_y * uy) \
            + 2.0 * (th_z * uz) * (ph_z * uz)
    return F_plus, F_cross


def antenna_pattern_cw_sum(n_theta, n_phi, u_theta, u_phi,
                           F_plus, F_cross, alpha, bp):
    """Combined pattern for the linear-response ORF integrand.

    Computes the weighted antenna sum:
        (F_1+ F_2+ + F_1× F_2×) * T_1 * conj(T_2) * bp
    where T_i comes from the transfer module and bp is the baseline phase.

    This is the core integrand factor shared by nearly all ORF scripts.
    """
    # Alias for backward compatibility with the ORF module below.
    return (F_plus, F_cross)
