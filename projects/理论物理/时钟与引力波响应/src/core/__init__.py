"""Shared core modules for gravitational-wave detector network analysis.

Extracted from scripts/ to eliminate duplication across 60+ scripts.
"""
from .constants import c, G, h_bar, H_0, Mpc_in_m, AU_in_m
from .geometry import arm_direction, build_constellation, make_triangle_constellation, link_direction
from .transfer import olc_transfer_function
from .antenna import antenna_patterns
from .sky import sky_grid, dOmega_element
from .orf import compute_orf_standard
from .chiral import chiral_factor, compute_orf_chiral, compute_orf_chiral_compare
from .noise import olc_noise_psn, olc_noise_qpn, interferometer_noise_psd

__all__ = [
    # constants
    "c", "G", "h_bar", "H_0", "Mpc_in_m", "AU_in_m",
    # geometry
    "arm_direction",
    "build_constellation",
    "make_triangle_constellation",
    "link_direction",
    # transfer
    "olc_transfer_function",
    # antenna
    "antenna_patterns",
    # sky
    "sky_grid",
    "dOmega_element",
    # ORF
    "compute_orf_standard",
    # chiral
    "chiral_factor",
    "compute_orf_chiral",
    "compute_orf_chiral_compare",
    # noise
    "olc_noise_psn",
    "olc_noise_qpn",
    "interferometer_noise_psd",
]
