"""OLC transfer function — one-way link response to gravitational waves."""
import numpy as np


def olc_transfer_function(f, L, cos_nu):
    """One-way link transfer function for OLC (Lou Eq. 2-30).

    T(u·n, f) = (i * 2*pi * f * L / c)
                * sinc[pi*f*L/c * (1 - u·n)]
                * exp[-i * pi * f * L / c * (1 - u·n)]

    Args:
        f: frequency (Hz), scalar or array-like.
        L: arm length (m).
        cos_nu: cos(n·u), projection of sky direction onto arm.

    Returns:
        Same shape as f, scalar if input is scalar.
    """
    f_arr = np.atleast_1d(f)
    scalar_in = np.isscalar(f)
    beta = np.pi * np.abs(f_arr) * L / _consts.c
    one_minus = 1.0 - cos_nu
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f_arr) * L / _consts.c
    result = prefac * sinc_v * phase
    return result[0] if scalar_in else result


# ─── private: import constants without exposing full package ─────────────────
def _import_consts():
    """Late import to avoid circular deps.  Returns the constants module."""
    # Only called once; subsequent reads of _consts are via the cached module.
    from .. import core
    # If core imports this module first, the name is already on sys.modules.
    import sys
    return sys.modules["src.core.constants"]


class _LazyConsts:
    def __getattr__(self, name):
        c = _import_consts()
        return getattr(c, name)


_consts = _LazyConsts()
