"""Chiral (Stokes V) ORF — overlap reduction function for circular GW polarization."""
import numpy as np
from .transfer import olc_transfer_function
from .antenna import antenna_patterns
from .sky import sky_grid


def chiral_factor(n_theta, n_phi, u_theta, u_phi, v_theta, v_phi):
    """Strict chiral factor: -Im(w_1² · w_2*²) with component-wise w_i.

    w_i² = sum_k ((th_k + i·ph_k)·u_k)²  computed component-wise, NOT as dot product.

    This gives w_i² = F_plus_i + i·F_cross_i, so
    -Im(w_1² · conj(w_2²)) = F1p·F2x - F1x·F2p (exactly the antisymmetric combination).

    Args:
        n_theta, n_phi: 2D sky grids.
        u_theta, u_phi: arm direction of detector 1.
        v_theta, v_phi: arm direction of detector 2.

    Returns:
        2D array of chiral factor values.
    """
    ct, st = np.cos(n_theta), np.sin(n_theta)
    cp, sp = np.cos(n_phi), np.sin(n_phi)

    th_x, th_y, th_z = ct * cp, ct * sp, -st
    ph_x, ph_y, ph_z = -sp, cp, 0.0

    u1x = np.sin(u_theta) * np.cos(u_phi)
    u1y = np.sin(u_theta) * np.sin(u_phi)
    u1z = np.cos(u_theta)

    u2x = np.sin(v_theta) * np.cos(v_phi)
    u2y = np.sin(v_theta) * np.sin(v_phi)
    u2z = np.cos(v_theta)

    w1_sq = ((th_x + 1j * ph_x)**2 * u1x**2 +
             (th_y + 1j * ph_y)**2 * u1y**2 +
             (th_z + 1j * ph_z)**2 * u1z**2)
    w2_sq = ((th_x + 1j * ph_x)**2 * u2x**2 +
             (th_y + 1j * ph_y)**2 * u2y**2 +
             (th_z + 1j * ph_z)**2 * u2z**2)

    return -np.imag(w1_sq * np.conj(w2_sq))


def compute_orf_chiral(f, L1, L2, u_theta, u_phi, v_theta, v_phi,
                       d, theta_s, phi_s,
                       ntheta=60, nphi=120):
    """Chiral ORF using antisymmetric polarization combination.

    Uses F1p·F2x - F1x·F2p instead of F1p·F2p + F1x·F2x.

    Args:
        f: frequency (Hz).
        L1, L2: arm lengths (m).
        u_theta, u_phi: arm direction of detector 1.
        v_theta, v_phi: arm direction of detector 2.
        d: baseline distance (m).
        theta_s, phi_s: GW propagation direction.

    Returns:
        Normalized chiral ORF value (real, dimensionless).
    """
    tG, pG, dO, nx, ny, nz = sky_grid(ntheta, nphi)

    u1 = np.array([np.sin(u_theta)*np.cos(u_phi),
                   np.sin(u_theta)*np.sin(u_phi),
                   np.cos(u_theta)])
    v1 = np.array([np.sin(v_theta)*np.cos(v_phi),
                   np.sin(v_theta)*np.sin(v_phi),
                   np.cos(v_theta)])

    s = np.array([np.sin(theta_s)*np.cos(phi_s),
                  np.sin(theta_s)*np.sin(phi_s),
                  np.cos(theta_s)])

    cos_nu = nx*u1[0] + ny*u1[1] + nz*u1[2]
    cos_nv = nx*v1[0] + ny*v1[1] + nz*v1[2]

    alpha = 2.0 * np.pi * np.abs(f) * d / _consts.c
    n_s = nx*s[0] + ny*s[1] + nz*s[2]
    bp = np.exp(-1j * alpha * n_s)

    T1 = olc_transfer_function(f, L1, cos_nu)
    T2 = olc_transfer_function(f, L2, cos_nv)

    F1p, F1x = antenna_patterns(tG, pG, u_theta, u_phi)
    F2p, F2x = antenna_patterns(tG, pG, v_theta, v_phi)

    # Antisymmetric (chiral) combination
    S = (F1p * F2x - F1x * F2p) * T1 * np.conj(T2) * bp
    corr = np.sum(S * dO)

    magT1 = np.abs(T1)
    magT2 = np.abs(T2)
    auto1 = np.sum((F1p**2 + F1x**2) * magT1**2 * dO)
    auto2 = np.sum((F2p**2 + F2x**2) * magT2**2 * dO)
    denom = np.sqrt(auto1 * auto2)
    if np.abs(denom) < 1e-30:
        return 0.0
    return np.real(corr / denom)


def compute_orf_chiral_compare(f, L1, L2, u_theta, u_phi, v_theta, v_phi,
                               d, theta_s, phi_s,
                               ntheta=60, nphi=120):
    """Compute both linear and chiral ORF for comparison.

    Returns (gamma_linear, gamma_chiral) for validation.
    """
    tG, pG, dO, nx, ny, nz = sky_grid(ntheta, nphi)

    u1 = np.array([np.sin(u_theta)*np.cos(u_phi),
                   np.sin(u_theta)*np.sin(u_phi),
                   np.cos(u_theta)])
    v1 = np.array([np.sin(v_theta)*np.cos(v_phi),
                   np.sin(v_theta)*np.sin(v_phi),
                   np.cos(v_theta)])

    s = np.array([np.sin(theta_s)*np.cos(phi_s),
                  np.sin(theta_s)*np.sin(phi_s),
                  np.cos(theta_s)])

    cos_nu = nx*u1[0] + ny*u1[1] + nz*u1[2]
    cos_nv = nx*v1[0] + ny*v1[1] + nz*v1[2]

    alpha = 2.0 * np.pi * np.abs(f) * d / _consts.c
    n_s = nx*s[0] + ny*s[1] + nz*s[2]
    bp = np.exp(-1j * alpha * n_s)

    T1 = olc_transfer_function(f, L1, cos_nu)
    T2 = olc_transfer_function(f, L2, cos_nv)

    F1p, F1x = antenna_patterns(tG, pG, u_theta, u_phi)
    F2p, F2x = antenna_patterns(tG, pG, v_theta, v_phi)

    magT1 = np.abs(T1)
    magT2 = np.abs(T2)
    auto1 = np.sum((F1p**2 + F1x**2) * magT1**2 * dO)
    auto2 = np.sum((F2p**2 + F2x**2) * magT2**2 * dO)
    denom = np.sqrt(auto1 * auto2)
    if np.abs(denom) < 1e-30:
        return 0.0, 0.0

    # Linear (symmetric) combination
    S_lin = (F1p * F2p + F1x * F2x) * T1 * np.conj(T2) * bp
    gamma_lin = np.real(np.sum(S_lin * dO)) / denom

    # Chiral (antisymmetric) combination
    S_chi = (F1p * F2x - F1x * F2p) * T1 * np.conj(T2) * bp
    gamma_chi = np.real(np.sum(S_chi * dO)) / denom

    return gamma_lin, gamma_chi


# ─── late import to avoid circular dependency ────────────────────────────────
def _import_consts():
    import sys
    return sys.modules["src.core.constants"]


class _LazyConsts:
    def __getattr__(self, name):
        return _import_consts().__getattribute__(name)


_consts = _LazyConsts()
