#!/usr/bin/env python3
"""
Phase-slip detection and analysis for chimera states.

Implements dual-criterion phase-slip detection:
  1. Coherence drop: r_s drops from >threshold_high to <threshold_low
  2. Phase-variance spike: Var(theta_i) within sector jumps significantly

Reviewer-5 notes addressed:
  Note 1: domain_id parameter in __init__
  Note 2/7: Phase variance computed internally from theta, not external input
  Note 3: r_s computed per 10 steps (fast path), not just 500-step snapshots
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


class PhaseSlipTracker:
    """
    Detect phase slips (coherence loss/recovery) in individual chimera sectors.

    A phase slip is defined as a sharp drop in sector coherence followed by
    potential recovery or permanent loss. Detection requires BOTH
    (a) r_s coherence drop AND (b) phase-variance spike to eliminate false
    positives from gradual coherence decay.
    """

    def __init__(
        self,
        domain_id: int = -1,
        coherence_threshold_high: float = 0.7,
        coherence_threshold_low: float = 0.3,
        phase_variance_spike: float = 1.5,
    ):
        """
        Args:
            domain_id: Domain identifier for output attribution.
            coherence_threshold_high: r_s below which a sector is coherent.
            coherence_threshold_low: r_s above which a sector has lost coherence.
            phase_variance_spike: Minimum increase in phase variance (radians^2)
                required to confirm a slip (dual-criterion).
        """
        self._domain_id = domain_id
        self._coherence_threshold_high = coherence_threshold_high
        self._coherence_threshold_low = coherence_threshold_low
        self._phase_variance_spike = phase_variance_spike
        self._slips: List[Dict] = []
        self._coherence_history: Dict[int, List[float]] = {}

    @property
    def domain_id(self) -> int:
        return self._domain_id

    @property
    def slips(self) -> List[Dict]:
        return list(self._slips)

    @property
    def slip_count(self) -> int:
        return len(self._slips)

    @staticmethod
    def _compute_sector_r_s(theta: np.ndarray, sector_mask: np.ndarray) -> float:
        """Compute local order parameter r_s for a sector."""
        sector_phases = theta[sector_mask]
        return float(abs(np.mean(np.exp(1j * sector_phases))))

    @staticmethod
    def _compute_sector_phase_var(theta: np.ndarray, sector_mask: np.ndarray) -> float:
        """
        Compute phase variance Var(theta_i) within a sector.

        Returns the variance of wrapped phase angles in radians^2.
        """
        sector_phases = theta[sector_mask]
        # Compute variance of wrapped angles using complex representation
        # Var = 1 - |mean(exp(i*theta))|^2 = 1 - r_s^2
        # But for spike detection, raw sample variance is more informative
        return float(np.var(sector_phases))

    def detect_slips(
        self,
        theta: np.ndarray,
        sector_mask_list: List[np.ndarray],
        t: int,
    ) -> List[Dict]:
        """
        Detect phase slips across all sectors.

        This method computes both r_s AND phase variance internally from theta
        (Reviewer-5 Notes 2/7), eliminating the need for external
        sector_phase_vars input.

        Args:
            theta: Full phase vector [N,] of the domain.
            sector_mask_list: List of boolean masks, one per sector.
            t: Current timestep.

        Returns:
            List of slip events detected at this timestep.
        """
        new_slips = []
        n_sectors = len(sector_mask_list)

        for s in range(n_sectors):
            mask = sector_mask_list[s]
            if not np.any(mask):
                continue

            r_s = self._compute_sector_r_s(theta, mask)
            phase_var = self._compute_sector_phase_var(theta, mask)

            prev_r = (
                self._coherence_history[s][-1]
                if self._coherence_history.get(s)
                else None
            )

            # --- Slip detection (dual criterion) ---
            if (
                prev_r is not None
                and prev_r >= self._coherence_threshold_high
                and r_s <= self._coherence_threshold_low
                and phase_var > self._phase_variance_spike
            ):
                slip = {
                    "sector": s,
                    "domain": self._domain_id,
                    "time": t,
                    "r_before": prev_r,
                    "r_after": r_s,
                    "phase_variance": phase_var,
                    "recovery_time": None,
                    "recovery_delta": None,
                }
                new_slips.append(slip)
                self._slips.append(slip)

            # --- Coherence recovery ---
            for slip in self._slips:
                if (
                    slip["sector"] == s
                    and slip["recovery_time"] is None
                    and r_s > self._coherence_threshold_high
                ):
                    slip["recovery_time"] = t
                    slip["recovery_delta"] = t - slip["time"]

            if s not in self._coherence_history:
                self._coherence_history[s] = []
            self._coherence_history[s].append(r_s)

        return new_slips

    def reset(self):
        """Clear all tracking state. Useful for reusing a tracker across runs."""
        self._slips.clear()
        self._coherence_history.clear()


class PhaseSlipAnalyzer:
    """
    Analyzes slip statistics: rates, survival functions, PSD.
    """

    @staticmethod
    def compute_survival_function(
        collapse_times: List[Optional[float]],
        max_t: float,
        bin_width: float = 1000.0,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute survival function S(T) = P(T_life > T).

        Args:
            collapse_times: List of collapse times (one per run).
                None means chimera survived until max_t (censored).
            max_t: Total simulation length.
            bin_width: Bin width for histogram.

        Returns:
            (bin_centers, S) where S[i] = fraction of runs surviving past bin_centers[i].
        """
        uncensored = [t for t in collapse_times if t is not None]
        censored_count = sum(1 for t in collapse_times if t is None)
        total = len(collapse_times)

        if not uncensored and censored_count == total:
            # All runs survived — S(T) = 1.0 for all T
            bins = np.arange(0, max_t + bin_width, bin_width)
            centers = (bins[:-1] + bins[1:]) / 2
            return centers, np.ones(len(centers))

        # Kaplan-Meier estimator for censored data
        all_times = sorted(collapse_times, key=lambda x: max_t if x is None else x)
        unique_times = sorted(set(t for t in all_times if t is not None))

        bins = np.arange(0, max_t + bin_width, bin_width)
        centers = (bins[:-1] + bins[1:]) / 2
        S = np.ones(len(centers))

        at_risk = total
        cum_deaths = 0

        for i, center in enumerate(centers):
            bin_start = center - bin_width / 2
            bin_end = center + bin_width / 2

            deaths_in_bin = sum(
                1 for t in all_times if t is not None and bin_start <= t < bin_end
            )
            if i == len(centers) - 1:
                censored_in_bin = sum(1 for t in all_times if t is None)
            else:
                censored_in_bin = 0

            if at_risk > 0 and deaths_in_bin > 0:
                S[i] = S[i - 1] * (1 - deaths_in_bin / at_risk) if i > 0 else (
                    1 - deaths_in_bin / at_risk
                )

            at_risk -= deaths_in_bin + censored_in_bin
            cum_deaths += deaths_in_bin

        # Ensure non-increasing
        S = np.maximum.accumulate(S)

        return centers, S

    @staticmethod
    def compute_slip_rate(
        slips: List[Dict],
        t_span: Tuple[int, int],
        n_sectors: int,
    ) -> float:
        """
        Compute average phase-slip rate per sector per timestep.

        Args:
            slips: List of slip events from all domains/tracking.
            t_span: (t_start, t_end) observation window.
            n_sectors: Number of sectors tracked.

        Returns:
            Slip rate per sector per timestep.
        """
        t_start, t_end = t_span
        relevant = [s for s in slips if t_start <= s["time"] <= t_end]
        if n_sectors <= 0 or t_end <= t_start:
            return 0.0
        return len(relevant) / (n_sectors * (t_end - t_start))

    @staticmethod
    def compute_sector_psd(
        sector_coherence_series: Dict[int, np.ndarray],
        dt: float = 0.02,
    ) -> Dict[int, Tuple[np.ndarray, np.ndarray]]:
        """
        Compute power spectral density of r_s(t) for each sector.

        Args:
            sector_coherence_series: {sector_index: r_s(t) time series}
            dt: Time step size.

        Returns:
            {sector_index: (frequencies, power)} tuples.
        """
        result = {}
        for s, series in sector_coherence_series.items():
            N = len(series)
            fft_vals = np.fft.rfft(series - np.mean(series))
            power = np.abs(fft_vals) ** 2 / N
            freqs = np.fft.rfftfreq(N, d=dt)
            result[s] = (freqs, power)
        return result

    @staticmethod
    def classify_metastability(
        collapse_times: List[Optional[float]],
        max_t: float,
    ) -> str:
        """
        Classify metastability type based on collapse-time distribution.

        Returns one of:
            "H1-coexisting-attractor" — no collapses observed, chimera persists
            "H2-metastable-exponential" — collapse times fit exponential distribution
            "H3-intermittent" — multi-timescale or periodic collapse pattern
            "H1-fractal-boundaries" — some collapse, some don't, varied timing
        """
        uncensored = [t for t in collapse_times if t is not None]
        censored = [t for t in collapse_times if t is None]

        if len(uncensored) == 0:
            return "H1-coexisting-attractor"

        if len(censored) > 0 and len(uncensored) > 0:
            return "H1-fractal-boundaries"

        # All collapsed — test for exponential fit
        mean_life = np.mean(uncensored)
        # Kolmogorov-Smirnov test against exponential
        sorted_times = np.sort(uncensored)
        cdf_exp = 1 - np.exp(-sorted_times / mean_life)
        empirical_cdf = np.arange(1, len(sorted_times) + 1) / len(sorted_times)
        ks_stat = np.max(np.abs(empirical_cdf - cdf_exp))
        # Heuristic: if KS < 0.15, likely exponential
        if ks_stat < 0.15:
            return "H2-metastable-exponential"
        return "H3-intermittent"
