"""Constellation / arm geometry helpers used across scripts."""
import numpy as np


def arm_direction(u_theta, u_phi):
    """Unit vector of an arm from spherical angles."""
    return np.array([
        np.sin(u_theta) * np.cos(u_phi),
        np.sin(u_theta) * np.sin(u_phi),
        np.cos(u_theta),
    ])


def build_constellation(points, inclination=0.0):
    """Rotate a list of 3D points by an inclination about the x-axis.

    Args:
        points: (N, 3) array of satellite positions.
        inclination: rotation angle in radians around the x-axis.

    Returns:
        Dict with 'positions' (rotated, N×3), 'centroid', 'L' (mean arm length).
    """
    cos_i, sin_i = np.cos(inclination), np.sin(inclination)
    rotated = np.zeros_like(points)
    rotated[:, 0] = points[:, 0]
    rotated[:, 1] = points[:, 1] * cos_i - points[:, 2] * sin_i
    rotated[:, 2] = points[:, 1] * sin_i + points[:, 2] * cos_i
    centroid = np.mean(rotated, axis=0)

    arms = []
    for i in range(len(points)):
        j = (i + 1) % len(points)
        arms.append(np.linalg.norm(rotated[j] - rotated[i]))
    L = np.mean(arms)

    return {"positions": rotated, "centroid": centroid, "L": L}


def make_triangle_constellation(name, L, inclination, reference_position=None):
    """Right-equilateral triangle with inclination rotation.

    Used by LISA, Taiji, and many 3-satellite network scripts.
    """
    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([L, 0.0, 0.0])
    r3 = np.array([L / 2, L * np.sqrt(3) / 2, 0.0])
    points = np.array([r1, r2, r3])
    return {
        "name": name,
        **build_constellation(points, inclination),
        "inclination": inclination,
        "reference_position": reference_position,
        "L": L,
    }


def link_direction(pos, i, j):
    """Unit vector from satellite i → j.

    Returns:
        (direction_vector, arm_length)
    """
    arm = pos[j] - pos[i]
    length = np.linalg.norm(arm)
    return arm / length, length
