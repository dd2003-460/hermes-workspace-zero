#!/usr/bin/env python3
"""Create critical exponent comparison across all five DistCat examples (Figure 2)."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Example data
examples = ['AQFT\n(HD)', 'Fisher\nInfo Geo.', 'Bayesian\nF-R', 'Control\nResonance', 'EMRI\nChaos']
alphas = [1.84, 0.50, 0.50, 1, 0.50]
colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#60A33F']
physical_interps = ['Total var.\ndistance', 'Statistical\ndistance', 'Bayesian\ncontraction', 'Pole distance\n(amplified)', 'Metric-perturb.\ndistance']

# ---- Left: Bar chart of critical exponents ----
x_pos = np.arange(len(examples))
bars = ax1.bar(x_pos, alphas[:5], color=colors, alpha=0.8, edgecolor='#333', linewidth=0.8)
ax1.set_ylabel(r'Critical Exponent $\alpha$', fontsize=12, fontweight='bold')
ax1.set_title(r'Universal Power Law: $\delta \sim \Gamma^\alpha$', fontsize=13, fontweight='bold')
ax1.set_xticks(x_pos)
ax1.set_xticklabels(examples, fontsize=10)
ax1.set_yscale('log', base=2)
ax1.grid(True, alpha=0.3, axis='y')
ax1.set_ylim(0.3, 10)

# Add value labels on bars
for i, (bar, alpha) in enumerate(zip(bars, alphas)):
    if alpha == np.inf:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.3,
                r'$\infty$', ha='center', fontsize=12, fontweight='bold', color=colors[i])
    else:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.3,
                f'{alpha:.2f}', ha='center', fontsize=11, fontweight='bold', color=colors[i])

# Legend for physical interpretations
legend_handles = [plt.Rectangle((0, 0), 1, 1, color=c, alpha=0.8) for c in colors]
ax1.legend(legend_handles, physical_interps, fontsize=8.5, loc='upper left',
          framealpha=0.9, edgecolor='#666')

# ---- Right: Log-log plot showing power law comparison ----
Gamma_vals = np.logspace(-3, 0, 500)  # Gamma from 0.001 to 1

# Plot different power laws
alpha_vals = [0.50, 1.84, 0.50, 3.0]  # EMRI, AQFT, Fisher-Bayesian, reference
alpha_labels = [r'$\alpha=0.50$ (EMRI)', r'$\alpha=1.84$ (AQFT)', r'$\alpha=0.50$ (Fisher-Bayesian)',
                r'$\alpha=3.00$ (reference)']
display_alphas = [(0.50, 0), (1.84, 1), (0.50, 2), (3.0, -1)]

for a, idx in display_alphas:
    delta_vals = Gamma_vals ** a
    ax2.loglog(Gamma_vals, delta_vals, color=colors[idx], linewidth=2.5,
              label=alpha_labels[idx], linestyle='-' if idx >= 0 else '--')

# Reference line alpha=1
ax2.loglog(Gamma_vals, Gamma_vals, 'k--', linewidth=1, alpha=0.4, label=r'$\alpha=1$ (linear)')

ax2.set_xlabel(r'Pre-distance $\Gamma$ (source)', fontsize=12, fontweight='bold')
ax2.set_ylabel(r'Observation distance $\delta$', fontsize=12, fontweight='bold')
ax2.set_title(r'Universal Scaling $\delta \sim \Gamma^\alpha$', fontsize=13, fontweight='bold')
ax2.legend(fontsize=9, loc='upper left', framealpha=0.9, edgecolor='#666')
ax2.grid(True, alpha=0.2)

# Mark critical region
ax2.axvline(x=1e-3, color='red', linestyle=':', alpha=0.4, linewidth=1)
ax2.text(1.2e-3, 0.5, 'critical\nregion', fontsize=8, color='red', alpha=0.7, rotation=90, va='center')

plt.tight_layout()
plt.savefig('Fig2-critical-exponents.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('Fig2-critical-exponents.pdf', bbox_inches='tight', facecolor='white')
print("Created Fig2-critical-exponents.png + .pdf")
