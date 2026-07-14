"""Noise PSD functions commonly needed in OLC GW scripts."""
import numpy as np


def olc_noise_psn(L, f, S_psn=1e-24):
    """Position sensitivity noise PSD.

    Simplified shot-noise-like model: constant amplitude scaling with frequency.
    """
    return S_psn * (2.0 * np.pi * np.abs(f))**2


def olc_noise_qpn(f, S_qpn=1e-30):
    """Quantum back-action noise PSD."""
    return S_qpn / (2.0 * np.pi * np.abs(f))**2


def interferometer_noise_psd(f, f_star=1e-6, S_shot=1e-42, S_accel=1e-30):
    """Standard interferometer noise PSD (Hu et al. convention).

    S_n(f) = (2πf)² S_accel + S_shot / (2πf)²
    with characteristic frequency f_star for normalization.
    """
    f_abs = np.abs(f)
    S_accel_term = S_accel * (2.0 * np.pi * f_abs)**2
    S_shot_term = S_shot / (2.0 * np.pi * f_abs)**2
    return S_accel_term + S_shot_term
