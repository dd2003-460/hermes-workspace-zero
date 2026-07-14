#!/usr/bin/env python3
"""
Final comprehensive heatmap: OLC ORF across f-d space with orientation averaging.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import time

sys.path.insert(0, '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts')
import importlib.util
spec = importlib.util.spec_from_file_location("orf_solver",
    "/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/01-olc-orf-solver.py")
solver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solver)

c = solver.c

print("Computing orientation-averaged f-d heatmap (60 deg arm angle)...")
f_vals = np.logspace(-2, 3, 60)
d_vals = np.logspace(-2, 5, 60)  # 0.01 m to 100 km

n_orient = 12
n_sky = 32

real_map = np.zeros((len(f_vals), len(d_vals)))
mag_map = np.zeros((len(f_vals), len(d_vals)))
dev_map = np.zeros((len(f_vals), len(d_vals)))

# Baseline value (d=0, orientation-averaged)
print("  Computing baseline (d=0)...")
base_vals = []
for k in range(n_orient):
    phi_s = 2*np.pi*k/n_orient
    val = solver.compute_orf_two_arm(
        0.1, 10.0, 10.0,
        np.pi/4, 0.0, np.pi/4, np.deg2rad(60),
        0.0, np.pi/4, phi_s,
        ntheta=n_sky, nphi=n_sky*2
    )
    base_vals.append(val)
base_orf = np.mean(base_vals)
print(f"  Baseline ORF = {np.real(base_orf):.6f}")

t0 = time.time()
for i, fi in enumerate(f_vals):
    if i % 10 == 0:
        print(f"    f={fi:.2e} Hz ({i+1}/{len(f_vals)})...")
    for j, di in enumerate(d_vals):
        vals = []
        for k in range(n_orient):
            phi_s = 2*np.pi*k/n_orient
            val = solver.compute_orf_two_arm(
                fi, 10.0, 10.0,
                np.pi/4, 0.0, np.pi/4, np.deg2rad(60),
                di, np.pi/4, phi_s,
                ntheta=n_sky, nphi=n_sky*2
            )
            vals.append(val)
        mean_val = np.mean(vals)
        real_map[i, j] = np.real(mean_val)
        mag_map[i, j] = abs(mean_val)
        dev_map[i, j] = (abs(mean_val) - abs(base_orf)) / abs(base_orf) if abs(base_orf) > 1e-10 else 0.0

elapsed = time.time() - t0
print(f"  Completed in {elapsed:.1f}s")

# Generate 3-panel figure
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Panel 1: Real part
ax = axes[0]
Im = ax.pcolormesh(d_vals, f_vals, real_map, cmap='RdBu_r', shading='auto',
                   vmin=-0.25, vmax=0.25)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Baseline separation d (m)')
ax.set_ylabel('Frequency f (Hz)')
ax.set_title('ORF (real part, 60 deg arms)')
plt.colorbar(Im, ax=ax, label='Re(Γ)')

# Add reference line for baseline ORF value
DD, FF = np.meshgrid(d_vals, f_vals, indexing='ij')
base_grid = np.full_like(DD, fill_value=np.real(base_orf))
ax.contour(DD, FF, base_grid,
          levels=[np.real(base_orf)], colors='white', linewidths=1, linestyles='--')

# Panel 2: Magnitude
ax = axes[1]
Im = ax.pcolormesh(d_vals, f_vals, mag_map, cmap='viridis', shading='auto')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Baseline separation d (m)')
ax.set_ylabel('Frequency f (Hz)')
ax.set_title('|ORF| (magnitude)')
plt.colorbar(Im, ax=ax, label='|Γ|')
ax.axhline(y=c/(2*np.pi*10000), color='cyan', linestyle='--', linewidth=0.8, alpha=0.5)
ax.text(5e4, c/(2*np.pi*10000)*1.5, r'$\alpha=1$  (f·d=c/2π)', color='cyan', fontsize=8)

# Panel 3: Fractional deviation
ax = axes[2]
Im = ax.pcolormesh(d_vals, f_vals, dev_map*100, cmap='RdYlBu_r', shading='auto')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Baseline separation d (m)')
ax.set_ylabel('Frequency f (Hz)')
ax.set_title('% deviation from low-f limit')
plt.colorbar(Im, ax=ax, label='(%)')

# Mark OLC-relevant region
ax.add_patch(plt.Rectangle((10, 0.01), 1e4, 100, alpha=0.1, color='green',
                          label='OLC-relevant zone'))
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_orf_complete_fd.png', dpi=200)
print(f"  Saved: olc_orf_complete_fd.png")
plt.close()

# Save data as numpy array for reference
np.save('/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/orf_f_d_data.npy',
        {'f': f_vals, 'd': d_vals, 'real': real_map, 'mag': mag_map, 'dev': dev_map})
print(f"  Saved data array")
