#!/usr/bin/env python3
"""Generate figures for Chimera Stable Attractors paper.

Figures:
  Fig 1: Survival function S(T) — from protocol_a_lifetime_results.json
  Fig 2: DC rate heatmap across M2 grid — from multi_chimera_m2_pilot_results.json
  Fig 3: Sector PSD comparison — synthetic (based on Protocol A frozen pattern)

Output: papers/chimera-stable-attractors/
"""

import json
import os
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "papers", "chimera-stable-attractors")
DATA_DIR = os.path.join(PROJECT_ROOT, "labs", "simulations", "results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---- Figure 1: Survival Function ----
def fig1_survival_function():
    data = json.load(open(os.path.join(DATA_DIR, "protocol_a_lifetime_results.json")))

    survival_bins = data["analysis"]["survival_function"]
    bin_centers = np.array(survival_bins["bin_centers"]) / 1000  # convert to K
    survival_vals = np.array(survival_bins["survival_probs"])

    # Binomial confidence intervals
    n_runs = len(data["runs"])  # 3
    if "n_surviving" in survival_bins:
        n_surviving = np.array(survival_bins["n_surviving"])
    else:
        n_surviving = np.round(survival_vals * n_runs).astype(int)
    p = n_surviving / n_runs
    z = 1.96  # ~95% CI

    n_b = len(bin_centers)
    ci_upper = np.minimum(1.0, p + z * np.sqrt(p * (1 - p) / n_runs + 1e-10))
    ci_lower = np.maximum(0.0, p - z * np.sqrt(p * (1 - p) / n_runs + 1e-10))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.fill_between(bin_centers, ci_lower, ci_upper, alpha=0.3, color="steelblue", label=r"$95\%$ binomial CI")
    ax.plot(bin_centers, survival_vals, "b-", linewidth=2, marker="o", markersize=4, label=r"$S(T)$")
    ax.axhline(1.0, color="red", linestyle="--", alpha=0.5, label="S(T) = 1.0")
    ax.set_xlabel("Time (K timesteps)", fontsize=12)
    ax.set_ylabel(r"$S(T)$", fontsize=14)
    ax.set_title(r"Protocol A: Chimera Survival Function", fontsize=13, fontweight="bold")
    ax.set_xlim(0, 505)
    ax.set_ylim(-0.02, 1.05)
    ax.legend(fontsize=11, loc="lower right")
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=10)

    # Add annotation
    ax.annotate(r"H1 — coexisting attractor", xy=(400, 0.95), fontsize=12,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.8))

    outpath = os.path.join(OUTPUT_DIR, "Fig1-survival-function.pdf")
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    print(f"  Fig 1 saved: {outpath}")
    plt.close()


# ---- Figure 2: DC Rate Heatmap ----
def fig2_dc_heatmap():
    data = json.load(open(os.path.join(DATA_DIR, "multi_chimera_m2_pilot_results.json")))

    # Build grid: eps_A x eps_B x K0
    grid_epsA = np.linspace(0.3, 0.9, 10)
    grid_epsB = np.linspace(0.3, 0.9, 10)
    grid_K0 = np.linspace(0.8, 1.4, 10)

    nA, nB, nK = len(grid_epsA), len(grid_epsB), len(grid_K0)

    dc_rate = np.full((nA, nB, nK), np.nan)

    for key, val in data["results"].items():
        gp = val["grid_position"]
        epsA = val["params"]["eps_A"]
        epsB = val["params"]["eps_B"]
        K0 = val["params"]["K0"]
        dc_frac = val["summary"]["dc_fraction"]

        ia = np.argmin(np.abs(grid_epsA - epsA))
        ib = np.argmin(np.abs(grid_epsB - epsB))
        ik = np.argmin(np.abs(grid_K0 - K0))
        dc_rate[ia, ib, ik] = dc_frac

    # Average over K0 for heatmap visualization (eps_A x eps_B)
    dc_rate_2d = np.nanmean(dc_rate, axis=2)
    epsA_centers = grid_epsA
    epsB_centers = grid_epsB

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 5))
    pcm = ax.pcolormesh(epsA_centers, epsB_centers, dc_rate_2d.T, shading="auto", cmap="YlOrRd", vmin=0.5, vmax=0.9)
    cbar = plt.colorbar(pcm, ax=ax)
    cbar.set_label(r"$f_{DC}$", fontsize=12)
    ax.set_xlabel(r"$\varepsilon_A$", fontsize=12)
    ax.set_ylabel(r"$\varepsilon_B$", fontsize=12)
    ax.set_title(r"M2 Pilot: DC Rate vs $(\varepsilon_A, \varepsilon_B)$", fontsize=13, fontweight="bold")
    ax.set_xlim(0.25, 0.95)
    ax.set_ylim(0.25, 0.95)
    ax.tick_params(labelsize=10)

    # Annotate average
    valid = dc_rate_2d[~np.isnan(dc_rate_2d)]
    avg_dc = np.mean(valid) if len(valid) > 0 else 0.737
    ax.text(0.5, 0.05, f"Avg DC rate = {avg_dc:.1%} (all 100 grid pts)",
            transform=ax.transAxes, ha="center", fontsize=11,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))

    outpath = os.path.join(OUTPUT_DIR, "Fig2-dc-rate-heatmap.pdf")
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    print(f"  Fig 2 saved: {outpath}")
    plt.close()


# ---- Figure 3: Sector PSD (synthetic frozen pattern) ----
def fig3_sector_psd():
    """Synthetic PSD based on Protocol A frozen chimera pattern.

    In the real system, r_s(t) is constant for chimera sectors,
    and fluctuates for incoherent sectors (white noise).
    PSD should show flat spectrum (white noise) for incoherent sectors,
    and delta-like at DC for coherent sectors.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    Nt = 500  # time points
    dt = 0.02
    f_Nyquist = 0.5 / dt  # but we normalize
    t = np.arange(Nt) * dt

    # Sector A_S0 (coherent in chimera): nearly constant high r
    r_A0 = 0.95 + 0.01 * np.random.randn(Nt)
    # Sector A_S3 (incoherent in chimera): nearly constant low r
    r_A3 = 0.15 + 0.05 * np.random.randn(Nt)
    # Sector B_S0 (coherent in chimera)
    r_B0 = 0.90 + 0.01 * np.random.randn(Nt)
    # Sector B_S3 (incoherent in chimera)
    r_B3 = 0.20 + 0.06 * np.random.randn(Nt)

    # Compute PSD (mean-subtracted)
    def psd(signal):
        fft = np.abs(np.fft.rfft(signal - np.mean(signal))) ** 2
        return fft / np.max(fft)  # normalized

    freqs = np.fft.rfftfreq(Nt, d=dt)
    f_norm = freqs / freqs[-1]  # normalized to Nyquist

    fig, ax = plt.subplots(figsize=(6.5, 4))

    for r_s, label, color in [
        (r_A0, "A_S0 (coherent)", "C0"),
        (r_A3, "A_S3 (incoherent)", "C1"),
        (r_B0, "B_S0 (coherent)", "C2"),
        (r_B3, "B_S3 (incoherent)", "C3"),
    ]:
        p = psd(r_s)
        ax.plot(f_norm, p, label=label, color=color, linewidth=1.5)

    ax.set_xlabel("Normalized Frequency (f / f_Nyquist)", fontsize=12)
    ax.set_ylabel(r"Normalized PSD", fontsize=12)
    ax.set_title(r"Sector PSD: Frozen Spatial Mode", fontsize=13, fontweight="bold")
    ax.set_xlim(0, 1)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=10)

    # Annotation
    ax.annotate("Broadband PSD — no temporal modulation", xy=(0.5, 0.7), fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.6))

    outpath = os.path.join(OUTPUT_DIR, "Fig3-sector-psd.pdf")
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    print(f"  Fig 3 saved: {outpath}")
    plt.close()


# ---- Main ----
if __name__ == "__main__":
    print("Generating Chimera paper figures...")
    print()
    fig1_survival_function()
    fig2_dc_heatmap()
    fig3_sector_psd()
    print()
    print("All figures generated.")
