"""Standard (linear) ORF computation — the skeleton shared by 40+ scripts."""
import numpy as np
from .transfer import olc_transfer_function
from .antenna import antenna_patterns
from .sky import sky_grid


def compute_orf_standard(f, L1, L2, u_theta, u_phi, v_theta, v_phi,
                         d, theta_s, phi_s,
                         ntheta=60, nphi=120):
    """Two-detector ORF with baseline separation.

    Uses OLC transfer function for each link and a single baseline
    propagation phase exp(-i·2πf·d·n̂·s/c).

    Args:
        f: frequency (Hz).
        L1, L2: arm lengths (m).
        u_theta, u_phi: arm direction of detector 1.
        v_theta, v_phi: arm direction of detector 2.
        d: baseline distance between detectors (m).
        theta_s, phi_s: sky direction of GW propagation (defines baseline direction).
        ntheta, nphi: sky grid resolution.

    Returns:
        Normalized ORF value (real, dimensionless).
    """
    tG, pG, dO, nx, ny, nz = sky_grid(ntheta, nphi)

    # Arm unit vectors
    u1 = np.array([np.sin(u_theta)*np.cos(u_phi),
                   np.sin(u_theta)*np.sin(u_phi),
                   np.cos(u_theta)])
    v1 = np.array([np.sin(v_theta)*np.cos(v_phi),
                   np.sin(v_theta)*np.sin(v_phi),
                   np.cos(v_theta)])

    # Baseline direction
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

    S = (F1p * F2p + F1x * F2x) * T1 * np.conj(T2) * bp
    corr = np.sum(S * dO)

    magT1 = np.abs(T1)
    magT2 = np.abs(T2)
    auto1 = np.sum((F1p**2 + F1x**2) * magT1**2 * dO)
    auto2 = np.sum((F2p**2 + F2x**2) * magT2**2 * dO)
    denom = np.sqrt(auto1 * auto2)
    if np.abs(denom) < 1e-30:
        return 0.0
    return corr / denom


# ─── late import to avoid circular dependency ────────────────────────────────
def _import_consts():
    import sys
    return sys.modules["src.core.constants"]


class _LazyConsts:
    def __getattr__(self, name):
        return _import_consts().__getattribute__(name)


_consts = _LazyConsts()
