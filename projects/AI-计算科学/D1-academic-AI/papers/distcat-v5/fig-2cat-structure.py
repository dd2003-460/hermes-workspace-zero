#!/usr/bin/env python3
"""Create DistCat 2-category structure diagram (Figure 1)."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
ax.text(7, 9.7, r'2-Category Structure of DistCat', fontsize=16, fontweight='bold',
        ha='center', va='top')

# ---- Level 0-objects (base structures) ----
colors_obj = ['#E8F4F8', '#F0E8F8', '#F8F0E8']
objects = [r'$\mathcal{B}_1$', r'$\mathcal{B}_2$', r'$\mathcal{B}_3$']
obj_labels = [
    r'$(\mathbf{C}_1, \mathcal{F}_1, \mathcal{O}_1)$',
    r'$(\mathbf{C}_2, \mathcal{F}_2, \mathcal{O}_2)$',
    r'$(\mathbf{C}_3, \mathcal{F}_3, \mathcal{O}_3)$'
]

for i, (obj, lbl, clr) in enumerate(zip(objects, obj_labels, colors_obj)):
    x = 2.5 + i * 4.2
    box = FancyBboxPatch((x-0.9, 6.8), 1.8, 1.6,
                         boxstyle="round,pad=0.08",
                         facecolor=clr, edgecolor='#444', linewidth=1.5)
    ax.add_patch(box)
    ax.text(x, 8.0, obj, fontsize=13, fontweight='bold', ha='center', va='center')
    ax.text(x, 7.1, lbl, fontsize=8.5, ha='center', va='bottom', style='italic')

ax.text(7, 8.9, '0-objects: Base Structures', fontsize=10, ha='center',
        style='italic', color='#666')

# ---- Level 1-morphisms ----
for i in range(2):
    x1, x2 = 2.5 + i * 4.2, 2.5 + (i+1) * 4.2
    mid_x = (x1 + x2) / 2

    # Arrow between objects (horizontal 1-morphism)
    arrow = FancyArrowPatch((x1+0.9, 7.6), (x2-0.9, 7.6),
                           arrowstyle='<->', mutation_scale=18,
                           linewidth=1.8, color='#2E86AB')
    ax.add_patch(arrow)
    ax.text(mid_x, 8.2, r'$\Gamma_{ij}$', fontsize=10, ha='center', color='#2E86AB')

# Vertical 1-morphisms (Φ, alpha, beta)
for i in range(3):
    x = 2.5 + i * 4.2
    arrow = FancyArrowPatch((x, 6.8), (x, 5.0),
                           arrowstyle='<-', mutation_scale=18,
                           linewidth=1.8, color='#2E86AB')
    ax.add_patch(arrow)
    ax.text(x+0.8, 5.9, r'$(\Phi, \alpha, \beta)$', fontsize=9, ha='left', va='center', color='#2E86AB')

# ---- Level 2-morphisms (eta: natural transformations) ----
ax.text(7, 4.5, r'1-morphisms: Structure-preserving $(\Phi, \alpha, \beta)$',
        fontsize=10, ha='center', style='italic', color='#2E86AB')

# Draw thick arrows (2-morphisms) between 1-morphisms
for i in range(2):
    x1, x2 = 2.5 + i * 4.2, 2.5 + (i+1) * 4.2
    mid_x = (x1 + x2) / 2
    y = 3.8

    # Use a thicker arrow to represent 2-morphism
    arrow = FancyArrowPatch((x1+0.9, y+0.3), (x2-0.9, y+0.3),
                           arrowstyle='<->', mutation_scale=20,
                           linewidth=3.5, color='#A23B72', alpha=0.7)
    ax.add_patch(arrow)
    ax.text(mid_x, y, r'$\eta: \delta_{ij} \Rightarrow \Phi(\Gamma_{ij})$',
            fontsize=9.5, ha='center', color='#A23B72', fontweight='bold')

ax.text(7, 3.3, r'2-morphisms: $\eta$ — Distance export principle',
        fontsize=10, ha='center', style='italic', color='#A23B72')

# ---- Functor D: DistCat -> Met ----
# Big box showing the functor
functor_box = FancyBboxPatch((0.3, 0.3), 13.4, 2.3,
                            boxstyle="round,pad=0.1",
                            facecolor='#FFF9E6', edgecolor='#F18F01',
                            linewidth=2, linestyle='--')
ax.add_patch(functor_box)

# Metric space targets
colors_met = ['#FDEDC8', '#FDEDC8', '#FDEDC8']
met_objs = [r'$D(\mathcal{B}_1)$', r'$D(\mathcal{B}_2)$', r'$D(\mathcal{B}_3)$']
for i, (mobj, clr) in enumerate(zip(met_objs, colors_met)):
    x = 2.5 + i * 4.2
    mbox = FancyBboxPatch((x-0.7, 1.3), 1.4, 1.0,
                         boxstyle="round,pad=0.06",
                         facecolor=clr, edgecolor='#F18F01', linewidth=1.5)
    ax.add_patch(mbox)
    ax.text(x, 1.8, mobj, fontsize=11, fontweight='bold', ha='center', va='center')

ax.text(7, 2.4, '2-category of Metric Spaces', fontsize=9, ha='center',
        style='italic', color='#F18F01')

# Functor arrows
for i in range(3):
    x = 2.5 + i * 4.2
    arrow = FancyArrowPatch((x, 5.0), (x, 2.3),
                           arrowstyle='->', mutation_scale=22,
                           linewidth=2.5, color='#F18F01')
    ax.add_patch(arrow)
    ax.text(x+0.7, 3.65, r'$D$', fontsize=11, ha='left', va='center',
            color='#F18F01', fontweight='bold')

ax.text(7, 0.7, r'2-functor $D: \mathbf{DistCat} \to \mathbf{Met}$ — $D(\mathcal{B})$ is the observation distance $\delta$',
        fontsize=9.5, ha='center', color='#D68910', fontweight='bold')

# Key equations
eq_box = FancyBboxPatch((0.3, 9.05), 13.4, 0.55,
                       boxstyle="round,pad=0.06",
                       facecolor='#F2F2F2', edgecolor='#666', linewidth=1)
ax.add_patch(eq_box)
ax.text(7, 9.32, r'$\delta \leq \Phi(\Gamma)$  (distance export principle)   |   $\delta \sim \Gamma^\alpha$  (asymptotic universality)',
        fontsize=9, ha='center', va='center', family='monospace')

plt.tight_layout()
plt.savefig('Fig1-2cat-structure.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('Fig1-2cat-structure.pdf', bbox_inches='tight', facecolor='white')
print("Created Fig1-2cat-structure.png + .pdf")
