#!/usr/bin/env python3
"""
M1 Go/No-Go 扫描驱动 — 双 chimera 域共存验证

流程:
1. 对 K_transition in [0.0, 0.8] step 0.1 逐一扫描
2. 每个值 3 次独立种子重复
3. 统计同时存在 2 个 chimera 域的比例
4. 输出 phase diagram + verdict

Failure condition: ALL K_transition values produce <2 chimera domains → M1 FAIL
"""

import sys
sys.path.insert(0, '.')
import numpy as np
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

from experiment_chimera_spatial_coupling import (
    run_chimera_experiment,
    simulate_kuramoto_ring,
    piecewise_k,
    detect_chimera_in_domain,
    compute_cross_domain_correlation,
)
from chimera_diagnostic_v2 import ChimeraDiagnosticV2
from chimera_detector import ChimeraDetector


# ---- M1 constants ----

N_TOTAL = 1500
N_PER_DOMAIN = N_TOTAL // 2
K_TRANSITION_SCAN = [round(v, 1) for v in np.arange(0.0, 0.81, 0.1)]
T_TRANSIENT = 50000
T_MEASURE = 50000
N_RUNS = 3
SEED_BASE = 42
DT = 0.02
DOMAIN_BOUNDARIES = [0.4, 0.5, 0.9]
EPS_A = 0.6
EPS_B = 0.6
DELTA = 0.15


def run_m1_scan(
    output_dir: str = "labs/simulations/",
    k_transition_values: Optional[List[float]] = None,
    faster_mode: bool = False,
) -> Dict:
    """
    运行完整的 M1 扫描。
    """
    if k_transition_values is None:
        k_transition_values = K_TRANSITION_SCAN

    if faster_mode:
        # Fast sweep: 3×10⁴ transient + 3×10³ measure for prototyping
        t_transient, t_measure = 30000, 3000
    else:
        t_transient, t_measure = T_TRANSIENT, T_MEASURE

    print(f"\n{'#'*70}")
    print(f"# M1 Multi-Chimera Validation Scan")
    print(f"# N={N_TOTAL}, T_transient={t_transient}, T_measure={t_measure}")
    print(f"# K_transition scan: {k_transition_values}")
    print(f"# Runs per K: {N_RUNS}, seeds: {[SEED_BASE+r for r in range(N_RUNS)]}")
    print(f"{'#'*70}\n")

    # Data structures for results
    # key: k_transition (float)
    #   run_results: list of {"is_chimera_a", "is_chimera_b", "chimera_count"}
    all_results: Dict[float, Dict] = {}

    for ktrans in k_transition_values:
        run_results = []
        for run_idx in range(N_RUNS):
            rng = np.random.RandomState(SEED_BASE + run_idx)
            theta = rng.uniform(0, 2 * np.pi, N_TOTAL)
            pos = np.linspace(0, 1, N_TOTAL, endpoint=False)

            k_weights = piecewise_k(
                pos, K0=1.0, eps_a=EPS_A, eps_b=EPS_B,
                delta=DELTA, k_transition=ktrans,
                domain_boundaries=DOMAIN_BOUNDARIES,
            )

            domain_a_mask = (pos >= 0) & (pos < DOMAIN_BOUNDARIES[0])
            domain_b_mask = (pos >= DOMAIN_BOUNDARIES[1]) & (pos < DOMAIN_BOUNDARIES[2])

            for t in range(t_transient + t_measure):
                theta = simulate_kuramoto_ring(theta, k_weights, DT)

        # --- post-run diagnostics ---

        # 1. Sector-based domain sync (primary)
        state_a_primary = detect_chimera_in_domain(theta[domain_a_mask], n_sectors=8)
        state_b_primary = detect_chimera_in_domain(theta[domain_b_mask], n_sectors=8)

        chimera_count_primary = int(state_a_primary["is_chimera"]) + int(state_b_primary["is_chimera"])

        # 2. ChimeraDetector per domain (secondary)
        detector_a = ChimeraDetector(n_windows=8, gamma=0.5)
        detector_b = ChimeraDetector(n_windows=8, gamma=0.5)
        det_a_result = detector_a.detect(theta[domain_a_mask])
        det_b_result = detector_b.detect(theta[domain_b_mask])

        chimera_count_detector = 0
        if str(det_a_result["phase"]) == "ChimeraPhase.PHASE_III_CHIMERA_STABLE":
            chimera_count_detector += 1
        if str(det_b_result["phase"]) == "ChimeraPhase.PHASE_III_CHIMERA_STABLE":
            chimera_count_detector += 1

        # 3. ChimeraDiagnosticV2 per domain (tertiary) — subsampled for memory
        diag_v2_a = ChimeraDiagnosticV2(n=N_PER_DOMAIN, dt=DT, n_segments=8, seed=SEED_BASE)
        diag_v2_b = ChimeraDiagnosticV2(n=N_PER_DOMAIN, dt=DT, n_segments=8, seed=SEED_BASE + 1)

        # For efficiency, we compute SCI without full theta history
        diag_sci_a = diag_v2_a.compute_sci(theta[domain_a_mask])
        diag_sci_b = diag_v2_b.compute_sci(theta[domain_b_mask])

        # 4. Cross-domain correlation
        r_a_final = state_a_primary["max_sync"]
        r_b_final = state_b_primary["max_sync"]

        run_results.append({
            "run_idx": run_idx,
            "k_transition": ktrans,
            # Primary method
            "is_chimera_a_primary": state_a_primary["is_chimera"],
            "is_chimera_b_primary": state_b_primary["is_chimera"],
            "chimera_count_primary": chimera_count_primary,
            # Secondary method
            "det_a_phase": str(det_a_result["phase"]),
            "det_b_phase": str(det_b_result["phase"]),
            "chimera_count_detector": chimera_count_detector,
            # Tertiary method
            "diag_sci_a": float(diag_sci_a),
            "diag_sci_b": float(diag_sci_b),
            # Cross-domain
            "r_a_final": r_a_final,
            "r_b_final": r_b_final,
            "global_sync": float(abs(np.mean(np.exp(1j * theta)))),
        })

        all_results[ktrans] = run_results

        # Aggregate this K_transition
        primary_double = sum(1 for rr in run_results if rr["chimera_count_primary"] >= 2)
        detector_double = sum(1 for rr in run_results if rr["chimera_count_detector"] >= 2)
        print(f"K_transition={ktrans:.1f}: primary_double={primary_double}/{N_RUNS}, "
              f"detector_double={detector_double}/{N_RUNS}, "
              f"r_A={r_a_final:.3f}, r_B={r_b_final:.3f}")

    # ---- Phase diagram ----
    phase_diagram = []
    for ktrans in sorted(all_results):
        data_list = all_results[ktrans]
        avg_chimera_primary = np.mean([rr["chimera_count_primary"] for rr in data_list])
        avg_chimera_detector = np.mean([rr["chimera_count_detector"] for rr in data_list])
        primary_double_frac = sum(1 for rr in data_list if rr["chimera_count_primary"] >= 2) / N_RUNS
        phase_diagram.append({
            "k_transition": ktrans,
            "avg_chimera_count_primary": float(avg_chimera_primary),
            "avg_chimera_count_detector": float(avg_chimera_detector),
            "double_chimera_fraction_primary": float(primary_double_frac),
        })

    # ---- Go/No-Go verdict ----
    any_double = any(pd["double_chimera_fraction_primary"] > 0 for pd in phase_diagram)

    verdict = {
        "m1_pass": any_double,
        "description": "GO" if any_double else "NO-GO",
        "phase_diagram": phase_diagram,
        "summary": {
            "total_k_values_tested": len(k_transition_values),
            "runs_per_k": N_RUNS,
            "max_double_chimera_fraction": max(
                pd["double_chimera_fraction_primary"] for pd in phase_diagram
            ),
            "k_values_with_double": [
                pd["k_transition"] for pd in phase_diagram
                if pd["double_chimera_fraction_primary"] > 0
            ],
        },
    }

    # ---- Save results ----
    out_path = Path(output_dir) / "multi_chimera_m1_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_data = {
        "experiment": "M1_multi_chimera_validation",
        "parameters": {
            "N_total": N_TOTAL,
            "N_per_domain": N_PER_DOMAIN,
            "T_transient": t_transient,
            "T_measure": t_measure,
            "dt": DT,
            "N_runs": N_RUNS,
            "domain_boundaries": DOMAIN_BOUNDARIES,
            "eps_a": EPS_A,
            "eps_b": EPS_B,
            "delta": DELTA,
        },
        "results": all_results,
        "phase_diagram": phase_diagram,
        "verdict": verdict,
    }

    with open(out_path, "w") as f:
        json.dump(out_data, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print(f"M1 VERDICT: {verdict['description']}")
    if verdict["m1_pass"]:
        print(f"GO — double chimera observed at K_transition: "
              f"{verdict['summary']['k_values_with_double']}")
    else:
        print(f"NO-GO — no K_transition produced 2 simultaneous chimera domains")
        print(f"Multi-chimera coexistence is ruled out under this configuration.")
    print(f"Results saved to: {out_path}")
    print(f"{'='*70}\n")

    return verdict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="M1 Multi-Chimera Go/No-Go Scan")
    parser.add_argument("--output", default="labs/simulations/",
                        help="Output directory")
    parser.add_argument("--fast", action="store_true",
                        help="Use reduced T_transient/T_measure for prototyping")
    parser.add_argument("--k-values", nargs="+", type=float, default=None,
                        help="Override K_transition scan values")
    args = parser.parse_args()

    run_m1_scan(
        output_dir=args.output,
        k_transition_values=args.k_values,
        faster_mode=args.fast,
    )
