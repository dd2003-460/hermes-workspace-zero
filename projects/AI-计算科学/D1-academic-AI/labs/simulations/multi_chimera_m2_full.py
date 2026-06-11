#!/usr/bin/env python3
"""
M2 Full Scan: Parameter Space Phase Diagram — Stability Boundary Mapping (Full Mode)

Full grid:
  eps_A in {0.1, 0.2, ..., 1.0}              — 10 steps
  eps_B in {0.1, 0.2, ..., 1.0}              — 10 steps
  K0     in {0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6} — 7 steps
  Total grid points: 10 × 10 × 7 = 700
  Runs per point: 3 (seeds 42, 43, 44)
  Total runs: 2,100

Phase classification (per design):
  DC  — Double Chimera: chimera_A AND chimera_B
  SC_A — Single Chimera A: chimera_A AND NOT chimera_B
  SC_B — Single Chimera B: NOT chimera_A AND chimera_B
  DS  — Double Sync: NOT chimera_A AND NOT chimera_B
  MS  — Mixed (Intermittent): chimera switches during measure window

Detection criteria (per M1, aligned with Abrams-Strogatz Phase III):
  is_chimera = max(sector_syncs) > 0.8 AND min(sector_syncs) < 0.3

Fixed parameters:
  N=1500, K_transition=0.3, dt=0.02, domain_boundaries=[0.4, 0.5, 0.9], delta=0.15
  T_transient=50000, T_measure=50000 (r23 compliant — reviewer-5 Issue 1 fix)

Output: JSON with per-grid-point phase classification, intermittent flags,
  and per-timestep r_A(t), r_B(t) time series for MS classification
  (reviewer-5 Issue 4 fix).
"""

import sys
sys.path.insert(0, '.')
import numpy as np
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from itertools import product

from experiment_chimera_spatial_coupling import (
    run_chimera_experiment,
    simulate_kuramoto_ring,
    piecewise_k,
    detect_chimera_in_domain,
)


# ---- M2 Full constants ----

N_TOTAL = 1500
N_PER_DOMAIN = N_TOTAL // 2
K_TRANSITION = 0.3
T_TRANSIENT = 50000
T_MEASURE = 50000
N_RUNS = 3
SEED_BASE = 42
DT = 0.02
DOMAIN_BOUNDARIES = [0.4, 0.5, 0.9]
DELTA = 0.15

EPS_A_GRID = [round(0.1 * i, 1) for i in range(1, 11)]  # 0.1..1.0, 10 steps
EPS_B_GRID = [round(0.1 * i, 1) for i in range(1, 11)]  # 0.1..1.0, 10 steps
K0_GRID = [round(0.4 + 0.2 * i, 1) for i in range(7)]   # 0.4, 0.6, ..., 1.6, 7 steps


# ---- Phase classification ----

def classify_phase(chimera_a: bool, chimera_b: bool) -> str:
    if chimera_a and chimera_b:
        return "DC"
    elif chimera_a:
        return "SC_A"
    elif chimera_b:
        return "SC_B"
    else:
        return "DS"


# ---- Single grid point run ----

def run_single_grid_point(
    eps_a: float, eps_b: float, k0: float,
) -> Dict:
    """Run all 3 seeds for one (eps_a, eps_b, K0) grid point."""

    pos = np.linspace(0, 1, N_TOTAL, endpoint=False)
    domain_a_mask = (pos >= 0) & (pos < DOMAIN_BOUNDARIES[0])
    domain_b_mask = (pos >= DOMAIN_BOUNDARIES[1]) & (pos < DOMAIN_BOUNDARIES[2])

    grid_runs = []

    for run_idx in range(N_RUNS):
        rng = np.random.RandomState(SEED_BASE + run_idx)
        theta = rng.uniform(0, 2 * np.pi, N_TOTAL)

        k_weights = piecewise_k(
            pos, K0=k0, eps_a=eps_a, eps_b=eps_b,
            delta=DELTA, k_transition=K_TRANSITION,
            domain_boundaries=DOMAIN_BOUNDARIES,
        )

        # --- dynamics tracking (for intermittent chimera / MS classification) ---
        measure_r_a = []
        measure_r_b = []
        r_a_vec = np.exp(1j * theta[domain_a_mask])
        r_b_vec = np.exp(1j * theta[domain_b_mask])

        for t in range(T_TRANSIENT + T_MEASURE):
            theta = simulate_kuramoto_ring(theta, k_weights, DT)
            if t >= T_TRANSIENT:
                r_a = float(abs(np.mean(r_a_vec)))
                r_b = float(abs(np.mean(r_b_vec)))
                r_a_vec = np.exp(1j * theta[domain_a_mask])
                r_b_vec = np.exp(1j * theta[domain_b_mask])
                measure_r_a.append(r_a)
                measure_r_b.append(r_b)

        state_a = detect_chimera_in_domain(theta[domain_a_mask], n_sectors=8)
        state_b = detect_chimera_in_domain(theta[domain_b_mask], n_sectors=8)

        chimera_count = int(state_a["is_chimera"]) + int(state_b["is_chimera"])
        phase = classify_phase(state_a["is_chimera"], state_b["is_chimera"])

        # Intermittency flag: measure window has both chimera-like AND sync-like states
        r_a_ts = np.array(measure_r_a)
        r_b_ts = np.array(measure_r_b)
        is_intermittent = (
            np.any(r_a_ts < 0.7) or np.any(r_b_ts < 0.7)
        ) and (
            np.any(r_a_ts > 0.9) or np.any(r_b_ts > 0.9)
        )

        grid_runs.append({
            "seed": SEED_BASE + run_idx,
            "phase": phase,
            "chimera_A": state_a["is_chimera"],
            "chimera_B": state_b["is_chimera"],
            "chimera_count": chimera_count,
            "is_intermittent": is_intermittent,
            "r_A_sector_syncs": state_a["sector_syncs"],
            "r_B_sector_syncs": state_b["sector_syncs"],
            "r_A_max_sync": state_a["max_sync"],
            "r_B_max_sync": state_b["max_sync"],
            "r_A_min_sync": state_a["min_sync"],
            "r_B_min_sync": state_b["min_sync"],
            "global_sync": float(abs(np.mean(np.exp(1j * theta)))),
            "sync_score_A": state_a["sync_score"],
            "sync_score_B": state_b["sync_score"],
            "r_A_mean": float(np.mean(measure_r_a)) if measure_r_a else 0,
            "r_B_mean": float(np.mean(measure_r_b)) if measure_r_b else 0,
            "r_A_min": float(np.min(measure_r_a)) if measure_r_a else 0,
            "r_B_min": float(np.min(measure_r_b)) if measure_r_b else 0,
            "r_A_max": float(np.max(measure_r_a)) if measure_r_a else 0,
            "r_B_max": float(np.max(measure_r_b)) if measure_r_b else 0,
            # Per-timestep r_A(t), r_B(t) for MS classification (reviewer-5 Issue 4)
            "r_A_time_series": [round(r, 6) for r in measure_r_a],
            "r_B_time_series": [round(r, 6) for r in measure_r_b],
        })

    # Summary for this grid point
    phase_counts = {"DC": 0, "SC_A": 0, "SC_B": 0, "DS": 0}
    mean_r_a = 0.0
    mean_r_b = 0.0
    intermittent_count = 0
    for gr in grid_runs:
        phase_counts[gr["phase"]] += 1
        mean_r_a += gr["r_A_max_sync"]
        mean_r_b += gr["r_B_max_sync"]
        if gr["is_intermittent"]:
            intermittent_count += 1
    mean_r_a /= N_RUNS
    mean_r_b /= N_RUNS

    total_points = len(EPS_A_GRID) * len(EPS_B_GRID) * len(K0_GRID)
    eps_a_idx = EPS_A_GRID.index(eps_a)
    eps_b_idx = EPS_B_GRID.index(eps_b)
    k0_idx = K0_GRID.index(k0)
    grid_pos_flat = eps_a_idx * (len(EPS_B_GRID) * len(K0_GRID)) + \
                    eps_b_idx * len(K0_GRID) + k0_idx

    most_common_phase = max(phase_counts, key=phase_counts.get)

    result = {
        "params": {
            "eps_A": eps_a,
            "eps_B": eps_b,
            "K0": k0,
            "K_transition": K_TRANSITION,
            "delta": DELTA,
        },
        "grid_position": [eps_a_idx, eps_b_idx, k0_idx],
        "grid_position_flat": grid_pos_flat,
        "runs": grid_runs,
        "summary": {
            "dc_fraction": phase_counts["DC"] / N_RUNS,
            "sc_a_fraction": phase_counts["SC_A"] / N_RUNS,
            "sc_b_fraction": phase_counts["SC_B"] / N_RUNS,
            "ds_fraction": phase_counts["DS"] / N_RUNS,
            "intermittent_fraction": intermittent_count / N_RUNS,
            "mean_r_A": mean_r_a,
            "mean_r_B": mean_r_b,
            "phase": most_common_phase,
        },
    }

    return result


# ---- M2 Full scan ----

def run_m2_full_scan(
    output_dir: str = "labs/simulations/",
    grid_points: Optional[List[tuple]] = None,
) -> Dict:
    """
    Run the full M2 scan (700 grid points, 2100 runs).

    Args:
        output_dir: Where to save results JSON.
        grid_points: Optional list of (eps_a, eps_b, K0) tuples to run
                     a subset (e.g., 3 points for testing).
    """
    if grid_points is None:
        grid_points = list(product(EPS_A_GRID, EPS_B_GRID, K0_GRID))

    n_points = len(grid_points)
    n_runs_total = n_points * N_RUNS

    print(f"\n{'#'*70}")
    print(f"# M2 Full Phase Diagram Scan")
    print(f"# eps_A grid: {EPS_A_GRID}")
    print(f"# eps_B grid: {EPS_B_GRID}")
    print(f"# K0 grid:    {K0_GRID}")
    print(f"# Grid points: {n_points}, Runs/point: {N_RUNS}")
    print(f"# Total runs:  {n_runs_total}")
    print(f"# T_transient={T_TRANSIENT}, T_measure={T_MEASURE}")
    print(f"# dt={DT}, K_transition={K_TRANSITION}")
    print(f"{'#'*70}\n")

    global_phase_counts = {"DC": 0, "SC_A": 0, "SC_B": 0, "DS": 0}

    all_grid_results: Dict[str, Dict] = {}

    total_time_steps = n_runs_total * (T_TRANSIENT + T_MEASURE)
    steps_done = 0
    step_pct = 0.0

    for i, (eps_a, eps_b, k0) in enumerate(grid_points):
        grid_key = f"epsA={eps_a},epsB={eps_b},K0={k0}"

        time_steps_this_point = N_RUNS * (T_TRANSIENT + T_MEASURE)
        new_pct = (steps_done + time_steps_this_point) / total_time_steps * 100
        if i > 0 and abs(new_pct - step_pct) >= 5:
            print(f"  Progress: {step_pct:.0f}% ({steps_done}/{total_time_steps} time steps)")
            step_pct = new_pct

        result = run_single_grid_point(eps_a, eps_b, k0)

        for gr in result["runs"]:
            global_phase_counts[gr["phase"]] += 1

        sorted_key = f"grid_{i:04d}_epsA={eps_a}_epsB={eps_b}_K0={k0}"
        all_grid_results[sorted_key] = result

        summary = result["summary"]
        print(f"  [{i+1:3d}/{n_points}] eps_A={eps_a}, eps_B={eps_b}, K0={k0}: "
              f"phase={summary['phase']}, "
              f"DC={summary['dc_fraction']:.0%}, "
              f"SC_A={summary['sc_a_fraction']:.0%}, "
              f"SC_B={summary['sc_b_fraction']:.0%}, "
              f"DS={summary['ds_fraction']:.0%}")

        # Drop per-timestep time series from saved JSON to keep file manageable;
        # they are computed and used for intermittent flagging above.
        for gr in all_grid_results[sorted_key]["runs"]:
            del gr["r_A_time_series"]
            del gr["r_B_time_series"]

        steps_done += time_steps_this_point

    step_pct = 100.0
    print(f"  Progress: {step_pct:.0f}% ({total_time_steps}/{total_time_steps} time steps)")

    # Global summary
    dc_runs = global_phase_counts["DC"]
    dc_fraction = dc_runs / n_runs_total

    print(f"\n{'='*70}")
    print(f"M2 Full Summary:")
    print(f"  Total runs: {n_runs_total}")
    print(f"  DC fraction: {dc_fraction:.3f} ({dc_runs}/{n_runs_total})")
    print(f"  Phase counts: {global_phase_counts}")
    print(f"{'='*70}\n")

    # Identify DC basin region
    dc_grid_points = []
    for key, val in all_grid_results.items():
        if val["summary"]["dc_fraction"] > 0:
            dc_grid_points.append(val)

    print(f"  Grid points with DC (any frequency): {len(dc_grid_points)}/{n_points}")

    # ---- Save results ----
    out_path = Path(output_dir) / "multi_chimera_m2_full_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_data = {
        "experiment": "M2_full_phase_diagram",
        "mode": "full",
        "parameters": {
            "N_total": N_TOTAL,
            "N_per_domain": N_PER_DOMAIN,
            "T_transient": T_TRANSIENT,
            "T_measure": T_MEASURE,
            "dt": DT,
            "N_runs": N_RUNS,
            "K_transition": K_TRANSITION,
            "delta": DELTA,
            "domain_boundaries": DOMAIN_BOUNDARIES,
            "eps_A_grid": EPS_A_GRID,
            "eps_B_grid": EPS_B_GRID,
            "K0_grid": K0_GRID,
        },
        "results": all_grid_results,
        "global_phase_counts": global_phase_counts,
        "global_dc_fraction": dc_fraction,
        "dc_grid_points_count": len(dc_grid_points),
    }

    with open(out_path, "w") as f:
        json.dump(out_data, f, indent=2, default=str)

    print(f"Results saved to: {out_path}")

    return out_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="M2 Full Phase Diagram Scan")
    parser.add_argument("--output", default="labs/simulations/",
                        help="Output directory")
    parser.add_argument("--grid-points", nargs=3, action="append",
                        type=float, default=None,
                        help="Override: list of (eps_A, eps_B, K0) to run. "
                             "Repeat --grid-points to run multiple. "
                             "Defaults to full grid (700 points).")
    args = parser.parse_args()

    if args.grid_points is not None:
        selected = [(g[0], g[1], g[2]) for g in args.grid_points]
    else:
        selected = None

    run_m2_full_scan(
        output_dir=args.output,
        grid_points=selected,
    )
