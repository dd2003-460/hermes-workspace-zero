#!/usr/bin/env python3
"""Create source discrimination comparison figure for D1-grav-waves paper.

Shows:
(a) Anisotropy amplitude comparison: SMBHB (1-10%) vs cosmological (~1e-5)
(b) Discrimination power vs pulsar count (total variation distance scaling)
(c) Schematic of PTA anisotropy pattern (LSS tracing vs isotropic)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
# sph_harm not needed directly

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# ---- (a, top-left) Anisotropy amplitude comparison ----
ax1 = axes[0, 0]
source_classes = ['SMBHB\n(galaxy\nLSS)', 'Cosmological\n(inflation)', 'Cosmological\n(phase\ntransition)', 'Cosmic\nstrings']
anisotropy_levels = [0.05, 1e-5, 1e-5, 0.01]  # Fractional anisotropy
colors_a = ['#C73E1D', '#2E86AB', '#60A33F', '#F18F01']
log_levels = [np.log10(l) for l in anisotropy_levels]

bars = ax1.bar(range(len(source_classes)), log_levels, color=colors_a, alpha=0.8,
              edgecolor='#333', linewidth=0.8)
ax1.set_ylabel(r'log$_{10}$(Fractional Anisotropy)', fontsize=11, fontweight='bold')
ax1.set_title('(a) Anisotropy Amplitude Comparison', fontsize=12, fontweight='bold')
ax1.set_xticks(range(len(source_classes)))
ax1.set_xticklabels(source_classes, fontsize=9)
ax1.set_ylim(-6, 0)
ax1.axhline(y=np.log10(1e-5), color='gray', linestyle='--', alpha=0.5, linewidth=0.8,
           label=r'$\mathcal{O}(10^{-5})$ cosmic variance')
ax1.legend(fontsize=8, loc='upper right')
ax1.grid(True, alpha=0.3, axis='y')

# Add value labels
for bar, val in zip(bars, log_levels):
    if abs(val) < 1:
        label = '+1.0'
    else:
        label = f'{val:.0f}'
    ax1.text(bar.get_x() + bar.get_width()/2, val + 0.15,
            label, ha='center', fontsize=9, fontweight='bold', color=colors_a[bars.index(bar)])

# ---- (b, top-right) Discrimination power vs pulsar count ----
ax2 = axes[0, 1]
N_pulsars = np.linspace(20, 100, 100)
N_pairs = N_pulsars * (N_pulsars - 1) / 2

# Statistical uncertainty
stat_unc = N_pairs ** (-0.5)

# SMBHB anisotropy variance (Poisson shot noise)
# For N_src ~ 10^4-10^6 sources, variance ~ 1/N_src
N_src_smbhb = np.array([1e4, 1e5, 1e6])
smbhb_var = 1 / N_src_smbhb

# Plot discriminant lines
ax2.loglog(N_pulsars, stat_unc, 'k-', linewidth=2.5, label=r'Statistical uncertainty $\sim P^{-1/2}$')

for i, (nsrc, var) in enumerate(zip(N_src_smbhb, smbhb_var)):
    ax2.axhline(y=np.sqrt(var), color=colors_a[0], linestyle=':', linewidth=1.5,
               alpha=0.7, label=f'SMBHB variance $N_{{\\rm src}}={int(nsrc)}$' if i == 0 else '')

# Discrimination threshold: where stat < anisotropy
# The transition region
y_trans = np.sqrt(1 / 1e5)  # ~0.3% for 10^5 sources
x_trans = (1 / y_trans) ** 0.5 + 1  # N_pulsars where P^{-1/2} = sqrt(var)
ax2.axvline(x_trans, color='red', linestyle='--', alpha=0.5, linewidth=1,
           label=f'Discrimination threshold N~{int(x_trans)}')

ax2.set_ylabel(r'Total Variation Distance', fontsize=11, fontweight='bold')
ax2.set_xlabel('Number of Pulsars $N$', fontsize=11, fontweight='bold')
ax2.set_title('(b) Discrimination Power vs PTA Size', fontsize=12, fontweight='bold')
ax2.legend(fontsize=8, loc='upper right', framealpha=0.9)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(20, 100)
ax2.set_ylim(1e-3, 1)

# Mark the feasible region
ax2.fill_between([20, 100], [1e-3, 1e-3], [1, 1], alpha=0.1, color='green',
                label='Discrimination region (stat < anisotropy)')

# ---- (c, bottom-left) HD correlation function with anisotropic perturbation ----
ax3 = axes[1, 0]
theta = np.linspace(0, 180, 500)
theta_rad = np.radians(theta)

# Standard HD function
def hellings_downs(gamma):
    """Standard isotropic HD correlation."""
    x = gamma / 2
    result = np.where(x == 0, 0.75, (1 - x) * np.log(x) - x / 4 + 1 / 2)
    return result + 1 / 4

hd = hellings_downs(theta_rad)

# Anisotropic perturbations
# SMBHB: ~5% modulation following LSS pattern (simplified as dipole + quadrupole)
smbhb_aniso = hd * (1 + 0.05 * np.cos(theta_rad) + 0.03 * np.cos(2 * theta_rad))

# Cosmological: ~1e-5 modulation
cosmo_aniso = hd * (1 + 1e-5 * np.cos(theta_rad))

ax3.plot(theta, hd, 'k-', linewidth=2.5, label='Isotropic HD')
ax3.fill_between(theta, hd * (1 - 5e-2), hd * (1 + 5e-2), alpha=0.3, color=colors_a[0],
                label=r'SMBHB $\mathcal{O}(1\text{--}10\%)$ anisotropy')
ax3.plot(theta, smbhb_aniso, colors_a[0], linewidth=1.5, linestyle='--', alpha=0.7)
ax3.plot(theta, cosmo_aniso, colors_a[1], linewidth=1.5, linestyle=':', alpha=0.7,
        label=r'Cosmological $\mathcal{O}(10^{-5})$ anisotropy')

ax3.set_xlabel(r'Angular Separation $\theta$ (degrees)', fontsize=11, fontweight='bold')
ax3.set_ylabel(r'Correlation $\zeta(\theta)$', fontsize=11, fontweight='bold')
ax3.set_title('(c) HD Correlation with Anisotropic Perturbations', fontsize=12, fontweight='bold')
ax3.legend(fontsize=8, loc='lower left')
ax3.grid(True, alpha=0.3)
ax3.set_ylim(-0.15, 0.5)

# ---- (d, bottom-right) Schematic PTA sky anisotropy patterns ----
ax4 = axes[1, 1]

# Create sky map data (Mollweide-like projection, simplified)
N_pts = 300
np.random.seed(42)

# SMBHB: clustered along galactic plane (simulated)
angles_smbhb = np.random.randn(500, 2) * np.array([0.4, 0.15])  # Narrow band around plane
phi_smbhb = angles_smbhb[:, 0]
theta_smbhb = angles_smbhb[:, 1] * 10
x_s = np.cos(phi_smbhb) * np.cos(theta_smbhb)
y_s = np.sin(phi_smbhb) * np.cos(theta_smbhb)
z_s = np.sin(theta_smbhb)

# Cosmological: nearly isotropic
angles_cosmo = np.random.randn(500, 3)
angles_cosmo = angles_cosmo / np.linalg.norm(angles_cosmo, axis=1)[:, np.newaxis]
x_c = angles_cosmo[:, 0]
y_c = angles_cosmo[:, 1]
z_c = angles_cosmo[:, 2]

ax4.scatter(x_s, y_s, c=z_s, cmap='RdBu_r', s=15, alpha=0.6, vmin=-0.15, vmax=0.15, edgecolors='none')
ax4.scatter(x_c, y_c, c=np.full(500, 0.5), cmap='Greys', s=15, alpha=0.4, edgecolors='none')

# Draw circle boundary
circle = plt.Circle((0, 0), 1, fill=False, edgecolor='black', linewidth=1.5)
ax4.add_patch(circle)

ax4.set_xlim(-1.2, 1.2)
ax4.set_ylim(-1.2, 1.2)
ax4.set_aspect('equal')
ax4.axis('off')
ax4.text(0, -1.45, '(d) PTA Sky Anisotropy Pattern', ha='center', fontsize=12, fontweight='bold')
ax4.text(0, -1.15, 'SMBHB (colored) traces galaxy LSS', ha='center', fontsize=9, color='#C73E1D')
ax4.text(0, -0.95, 'Cosmological (gray) nearly isotropic', ha='center', fontsize=9, color='#888888')

# Add colorbar
sm = plt.cm.ScalarMappable(cmap='RdBu_r', norm=plt.Normalize(vmin=-0.15, vmax=0.15))
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax4, fraction=0.08, pad=0.04)
cbar.set_label(r'Deviation from isotropic', fontsize=8)

plt.suptitle('GW Source Discrimination: SMBHB vs Cosmological Backgrounds',
            fontsize=14, fontweight='bold', y=1.01)

plt.tight_layout(rect=[0, 0, 0.85, 0.98])
plt.savefig('Fig2-source-discrimination.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('Fig2-source-discrimination.pdf', bbox_inches='tight', facecolor='white')
print("Created Fig2-source-discrimination.png + .pdf")
