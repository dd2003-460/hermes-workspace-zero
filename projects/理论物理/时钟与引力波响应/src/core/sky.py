"""Sky grid generation and sky-averaging helpers."""
import numpy as np


def sky_grid(ntheta=60, nphi=120):
    """Generate sky grid and integration weight.

    Args:
        ntheta: number of polar bins.
        nphi: number of azimuthal bins.

    Returns:
        (tG, pG, dO, nx, ny, nz) where:
            tG, pG: 2D grid of sky angles (ij indexing).
            dO: solid-angle element for integration.
            nx, ny, nz: sky-direction unit vector components.
    """
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2 * np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing="ij")
    dO = np.sin(tG) * (2 * np.pi / nphi) * (np.pi / ntheta)
    nx = np.sin(tG) * np.cos(pG)
    ny = np.sin(tG) * np.sin(pG)
    nz = np.cos(tG)
    return tG, pG, dO, nx, ny, nz


def dOmega_element(tG, ntheta=60, nphi=120):
    """Just the solid-angle weight for custom grids."""
    return np.sin(tG) * (2 * np.pi / nphi) * (np.pi / ntheta)


def sky_average(corr):
    """Normalize by total sky solid angle (for quick sanity checks).

    Returns corr / (4π) as a rough sky-averaged value.
    """
    return corr / (4 * np.pi)
