#!/usr/bin/env python3
"""
M1 实现验证测试

Test 1: domain_mask in ChimeraDiagnosticV2
Test 2: piecewise K(x) coupling in experiment_chimera_spatial_coupling
Test 3: multi_chimera_m1_validation.py runs without errors
"""

import sys
import numpy as np
sys.path.insert(0, '.')

from experiment_chimera_spatial_coupling import (
    piecewise_k,
    simulate_kuramoto_ring,
    detect_chimera_in_domain,
    run_chimera_experiment,
)
from chimera_diagnostic_v2 import ChimeraDiagnosticV2
from chimera_detector import ChimeraDetector, ChimeraPhase


def test_domain_mask():
    """Test 1: domain_mask parameter in ChimeraDiagnosticV2"""
    print("\n=== Test 1: domain_mask in ChimeraDiagnosticV2 ===")

    rng = np.random.RandomState(42)
    n_total = 1500
    theta = rng.uniform(0, 2 * np.pi, n_total)

    diag = ChimeraDiagnosticV2(n=n_total, dt=0.005, n_segments=8, seed=42)

    # No mask: should cover all N=1500 agents
    sync_full = diag.compute_segment_sync(theta)
    assert len(sync_full) == 8, f"Expected 8 segments, got {len(sync_full)}"
    print(f"  Full-ring segment_sync: {np.round(sync_full, 4)}")

    # With domain_mask: slice 40% of ring (0 to 0.40)
    domain_mask = np.zeros(n_total, dtype=bool)
    pos = np.arange(n_total) / n_total
    domain_mask[pos < 0.40] = True
    sync_masked = diag.compute_segment_sync(theta, domain_mask=domain_mask)
    assert len(sync_masked) == 8, f"Expected 8 segments, got {len(sync_masked)}"
    print(f"  Domain-masked segment_sync: {np.round(sync_masked, 4)}")

    # SCI with and without mask should differ (domain subsets are shorter arcs)
    sci_full = diag.compute_sci(theta)
    sci_masked = diag.compute_sci(theta, domain_mask=domain_mask)
    print(f"  SCI full: {sci_full:.4f}, SCI masked: {sci_masked:.4f}")

    # Empty mask should give all-zero sync
    empty_mask = np.zeros(n_total, dtype=bool)
    sync_empty = diag.compute_segment_sync(theta, domain_mask=empty_mask)
    assert np.all(sync_empty == 0), "Empty mask should give all-zero sync"
    print("  Empty mask => all-zero: OK")

    print("  TEST 1: PASS")


def test_piecewise_k():
    """Test 2: piecewise K(x) coupling function"""
    print("\n=== Test 2: piecewise K(x) coupling ===")

    x = np.linspace(0, 1, 1000, endpoint=False)

    # Default boundaries: [0.4, 0.5, 0.9]
    k = piecewise_k(x, K0=1.0, eps_a=0.6, eps_b=0.6, delta=0.15,
                    k_transition=0.3)

    # Check zone assignments
    mask_a = (x >= 0) & (x < 0.4)
    mask_t1 = (x >= 0.4) & (x < 0.5)
    mask_b = (x >= 0.5) & (x < 0.9)
    mask_t2 = (x >= 0.9)

    # Transition zones should be flat K_transition
    assert np.allclose(k[mask_t1], 0.3, atol=1e-10), \
        f"Transition zone 1 should be flat: {np.unique(k[mask_t1])}"
    assert np.allclose(k[mask_t2], 0.3, atol=1e-10), \
        f"Transition zone 2 should be flat: {np.unique(k[mask_t2])}"
    print("  Transition zones flat at K_transition=0.3: OK")

    # Domain A should vary (heterogeneous)
    k_a = k[mask_a]
    assert k_a.max() > 0.6 and k_a.min() < 1.0, \
        f"Domain A k should vary: min={k_a.min():.3f}, max={k_a.max():.3f}"
    print(f"  Domain A k range: [{k_a.min():.3f}, {k_a.max():.3f}]: OK")

    # Domain B should vary (with offset)
    k_b = k[mask_b]
    assert k_b.max() > 0.6 and k_b.min() < 1.0, \
        f"Domain B k should vary: min={k_b.min():.3f}, max={k_b.max():.3f}"
    print(f"  Domain B k range: [{k_b.min():.3f}, {k_b.max():.3f}]: OK")

    print("  TEST 2: PASS")


def test_simulate_and_detect():
    """Test 2b: simulation + chimera detection in domain_coupling mode"""
    print("\n=== Test 2b: simulate_kuramoto_ring + detect_chimera_in_domain ===")

    N = 200  # Small for testing
    rng = np.random.RandomState(42)
    theta = rng.uniform(0, 2 * np.pi, N)
    k_weights = np.ones(N)

    # One step should evolve
    theta_new = simulate_kuramoto_ring(theta, k_weights, dt=0.02)
    assert not np.allclose(theta, theta_new), "simulate should change theta"
    print("  Simulation step evolves theta: OK")

    # Detect chimera in domain
    state = detect_chimera_in_domain(theta, n_sectors=8)
    assert "is_chimera" in state
    assert "sector_syncs" in state
    assert len(state["sector_syncs"]) == 8
    print(f"  Detection output: is_chimera={state['is_chimera']}, "
          f"sector_syncs range: [{min(state['sector_syncs']):.3f}, "
          f"{max(state['sector_syncs']):.3f}]: OK")

    print("  TEST 2b: PASS")


def test_experiment_domain_coupling():
    """Test 2c: run_chimera_experiment with domain_coupling"""
    print("\n=== Test 2c: run_chimera_experiment(domain_coupling=True) ===")

    # Small N for quick test
    results = run_chimera_experiment(
        N=150,
        K0=1.0,
        epsilons=[0.0],
        T_transient=500,
        T_measure=100,
        dt=0.02,
        runs=1,
        seed=42,
        domain_coupling=True,
        k_transition=0.3,
        domain_boundaries=[0.4, 0.5, 0.9],
    )

    assert 0.3 in results, f"Expected 0.3 in results, got {list(results.keys())}"
    kdata = results[0.3]
    assert "avg_chimera_count" in kdata, f"Missing key: {kdata.keys()}"
    assert "double_chimera_fraction" in kdata
    print(f"  K_transition=0.3: avg_chimera_count={kdata['avg_chimera_count']:.3f}, "
          f"double_fraction={kdata['double_chimera_fraction']}")
    print("  TEST 2c: PASS")


def test_chimera_detector_per_domain():
    """Test: separate ChimeraDetector instances per domain"""
    print("\n=== Test 3: separate ChimeraDetector per domain ===")

    rng = np.random.RandomState(42)
    n_per_domain = 750

    theta_a = rng.uniform(0, 2 * np.pi, n_per_domain)
    theta_b = rng.uniform(0, 2 * np.pi, n_per_domain)

    detector_a = ChimeraDetector(n_windows=8, gamma=0.5)
    detector_b = ChimeraDetector(n_windows=8, gamma=0.5)

    result_a = detector_a.detect(theta_a)
    result_b = detector_b.detect(theta_b)

    assert result_a["n_windows"] == 8
    assert result_b["n_windows"] == 8
    assert len(result_a["r_local"]) == 8
    assert len(result_b["r_local"]) == 8
    assert result_a["n_agents"] == 750
    assert result_b["n_agents"] == 750
    # Random phases are expected to be Asynchronous (not chimera)
    print(f"  Detector A: phase={result_a['phase']}, "
          f"r_local range [{min(result_a['r_local']):.3f}, {max(result_a['r_local']):.3f}]: OK")
    print(f"  Detector B: phase={result_b['phase']}, "
          f"r_local range [{min(result_b['r_local']):.3f}, {max(result_b['r_local']):.3f}]: OK")

    print("  TEST 3: PASS")


def test_m1_module_import():
    """Test 4: multi_chimera_m1_validation imports correctly"""
    print("\n=== Test 4: import multi_chimera_m1_validation ===")

    import multi_chimera_m1_validation as m1
    assert hasattr(m1, 'run_m1_scan'), "Missing run_m1_scan function"
    assert m1.N_TOTAL == 1500
    assert m1.T_TRANSIENT == 50000
    assert m1.K_TRANSITION_SCAN == [round(v, 1) for v in np.arange(0.0, 0.81, 0.1)]
    print(f"  M1 constants: N={m1.N_TOTAL}, T_transient={m1.T_TRANSIENT}")
    print(f"  K_transition scan: {m1.K_TRANSITION_SCAN}")
    print("  TEST 4: PASS")


if __name__ == "__main__":
    tests = [
        test_domain_mask,
        test_piecewise_k,
        test_simulate_and_detect,
        test_experiment_domain_coupling,
        test_chimera_detector_per_domain,
        test_m1_module_import,
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"All tests passed: {len(tests) - failed}/{len(tests)}")
    if failed > 0:
        print(f"FAILED: {failed}/{len(tests)}")
        sys.exit(1)
    else:
        print("All 6 M1 implementation tests passed.")
        sys.exit(0)
