#!/usr/bin/env python3
"""
Adaptive Re-Injection for persona-v3

Monitors alignment_checker output, detects drift, and triggers
persona re-injection when alignment drops below threshold.

Usage:
    # Single-run mode (compare baseline vs target)
    python3 adaptive_reinjection.py --file <response_file> --baseline <baseline_file>

    # Library mode
    from adaptive_reinjection import AdaptiveReinjectionMonitor

    # Configuration mode
    python3 adaptive_reinjection.py --config
"""

import argparse
import hashlib
import json
import os
import sys
import time
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).parent
_PROJECT_DIR = _SCRIPTS_DIR.parent
sys.path.insert(0, str(_SCRIPTS_DIR))

import persona_keywords


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    # Dimension-level thresholds (score below this = breach)
    "thresholds": {
        "自适应精度": 0.30,
        "自适应探索": 0.25,
        "自适应感知": 0.25,
        "自适应先验": 0.25,
        "自适应自我": 0.20,
        "自适应投影": 0.25,
    },

    # Hysteresis — require N consecutive breaches before triggering
    "min_breaches": 3,

    # Monitoring
    "poll_interval_seconds": 10,
    "max_context_tokens": 200000,

    # Severity escalation
    "severity_thresholds": {
        "LOW": {"min_breach": 1, "max_drift": 0.10},
        "MEDIUM": {"min_breach": 2, "max_drift": 0.20},
        "HIGH": {"min_breach": 3, "max_drift": 0.35},
        "CRITICAL": {"min_breach": 4},
    },

    # Reinjection strategies by severity
    # Values must match Strategy enum member names (e.g. "PREPEND_MANIFEST")
    "strategy_by_severity": {
        "LOW": "PREPEND_MANIFEST",
        "MEDIUM": "PREPEND_FULL",
        "HIGH": "PREPEND_FULL",
        "CRITICAL": "RESET",
    },
}


class Severity(Enum):
    NORMAL = "NORMAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Strategy(Enum):
    STRATEGY_PREPEND_MANIFEST = "PREPEND_MANIFEST"
    STRATEGY_PREPEND_FULL = "PREPEND_FULL"
    STRATEGY_RESET = "RESET"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DimensionBreach:
    dimension: str
    baseline_score: float
    current_score: float
    delta: float
    threshold: float
    breached: bool


@dataclass
class DriftEvent:
    timestamp: str
    severity: Severity
    breaches: list  # list[DimensionBreach]
    total_drift: float
    pre_scores: dict
    baseline_scores: dict


@dataclass
class ReinjectionEvent:
    trigger_event: DriftEvent
    strategy: Strategy
    context_modified: str
    context_modified_length: int
    manifest_included: bool
    full_prompt_included: bool
    reinjection_text: str = ""


@dataclass
class AuditEntry:
    cycle_id: int
    timestamp: str
    trigger: dict
    action: dict
    result: dict


# ---------------------------------------------------------------------------
# Alignment checker helper — run dimension score computation inline
# ---------------------------------------------------------------------------

def compute_alignment_scores(text: str) -> dict:
    """Compute alignment scores for text using persona_keywords.

    Returns dict with:
        - dimension_scores: {dim: score 0-1}
        - core_scores: {dim: score 0-1}
    """
    dim_scores = persona_keywords.compute_dimension_scores(text)
    core_scores = persona_keywords.compute_core_scores(text)

    scores = {
        "dimension_scores": {k: round(v, 4) for k, v in dim_scores.items()},
        "core_scores": {k: round(v, 4) for k, v in core_scores.items()},
    }

    return scores


def score_text_from_file(filepath: str) -> dict:
    """Compute alignment scores for a file."""
    text = Path(filepath).read_text(encoding="utf-8")
    return compute_alignment_scores(text)


# ---------------------------------------------------------------------------
# DriftDetector
# ---------------------------------------------------------------------------

class DriftDetector:
    """Detects persona drift and classifies severity."""

    def __init__(self, config: dict = None):
        self.config = config or DEFAULT_CONFIG
        self.thresholds = self.config["thresholds"]
        self.min_breaches = self.config["min_breaches"]
        self.breach_history = {}

    def evaluate(self, baseline_scores: dict, current_scores: dict) -> Optional[DriftEvent]:
        """Compare baseline vs. current scores. Returns DriftEvent if triggered.

        Parameters:
            baseline_scores: {dim: score} — the reference state
            current_scores: {dim: score} — the current state to evaluate

        Returns:
            DriftEvent if any dimensions breach, None otherwise.
        """
        breaches = []
        for dim, threshold in self.thresholds.items():
            baseline = baseline_scores.get(dim, 0.0)
            current = current_scores.get(dim, 0.0)
            delta = current - baseline
            breached = current < threshold

            if dim not in self.breach_history:
                self.breach_history[dim] = []
            self.breach_history[dim].append(breached)

            # Keep bounded history
            max_history = self.min_breaches * 3
            self.breach_history[dim] = self.breach_history[dim][-max_history:]

            consecutive = 0
            for b in reversed(self.breach_history[dim]):
                if b:
                    consecutive += 1
                else:
                    break

            if breached and consecutive >= self.min_breaches:
                breaches.append(DimensionBreach(
                    dimension=dim,
                    baseline_score=baseline,
                    current_score=current,
                    delta=delta,
                    threshold=threshold,
                    breached=True,
                ))

        if not breaches:
            return None

        total_drift = sum(b.delta for b in breaches) / len(breaches) if breaches else 0
        severity = self._classify_severity(len(breaches), total_drift)
        pre_scores = {dim: current_scores.get(dim, 0.0) for dim in self.thresholds}

        return DriftEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            severity=severity,
            breaches=breaches,
            total_drift=round(total_drift, 4),
            pre_scores=pre_scores,
            baseline_scores={k: round(v, 4) for k, v in baseline_scores.items()},
        )

    def reset_history(self):
        """Clear breach history — call after successful reinjection validation."""
        self.breach_history = {}

    def _classify_severity(self, n_breaches: int, total_drift: float) -> Severity:
        thresh = self.config["severity_thresholds"]
        if n_breaches >= thresh["CRITICAL"]["min_breach"]:
            return Severity.CRITICAL
        if n_breaches >= thresh["HIGH"]["min_breach"] or abs(total_drift) >= thresh["HIGH"]["max_drift"]:
            return Severity.HIGH
        if n_breaches >= thresh["MEDIUM"]["min_breach"] or abs(total_drift) >= thresh["MEDIUM"]["max_drift"]:
            return Severity.MEDIUM
        return Severity.LOW


# ---------------------------------------------------------------------------
# ReinjectionEngine
# ---------------------------------------------------------------------------

class ReinjectionEngine:
    """Executes persona re-injection strategies."""

    def __init__(self, manifest_path: Optional[Path] = None,
                 prompt_path: Optional[Path] = None, config: dict = None):
        self.config = config or DEFAULT_CONFIG
        self.manifest_path = manifest_path or _PROJECT_DIR / "persona-manifest-v3.txt"
        self.prompt_path = prompt_path or _PROJECT_DIR / "persona-v3-prompt.txt"
        self._manifest_text = None
        self._prompt_text = None
        self._load_persona_resources()

    def _load_persona_resources(self):
        """Load persona resources, tolerating missing files."""
        try:
            self._manifest_text = self.manifest_path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            warnings.warn(f"Manifest not found: {self.manifest_path}")
            self._manifest_text = ""

        try:
            self._prompt_text = self.prompt_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            warnings.warn(f"Persona prompt not found: {self.prompt_path}")
            self._prompt_text = ""

    def execute(self, event: DriftEvent) -> ReinjectionEvent:
        """Execute the strategy matching event severity."""
        strategy_map = self.config["strategy_by_severity"]
        strategy_name = strategy_map.get(event.severity.value, "STRATEGY_PREPEND_MANIFEST")
        strategy = Strategy(strategy_name)

        reinjection_text = self._build_reinjection(event, strategy)
        context_hash = hashlib.sha256(
            event.timestamp.encode() + reinjection_text.encode()
        ).hexdigest()[:12]

        manifest_included = strategy == Strategy.STRATEGY_PREPEND_MANIFEST
        full_prompt_included = strategy in (Strategy.STRATEGY_PREPEND_FULL, Strategy.STRATEGY_RESET)

        return ReinjectionEvent(
            trigger_event=event,
            strategy=strategy,
            context_modified=context_hash,
            context_modified_length=len(reinjection_text),
            manifest_included=manifest_included,
            full_prompt_included=full_prompt_included,
            reinjection_text=reinjection_text,
        )

    def get_reinjection_text(self, event: DriftEvent) -> str:
        """Build reinjected text for a given event and current config."""
        strategy_map = self.config["strategy_by_severity"]
        strategy_name = strategy_map.get(event.severity.value, "STRATEGY_PREPEND_MANIFEST")
        strategy = Strategy(strategy_name)
        return self._build_reinjection(event, strategy)

    def _build_reinjection(self, event: DriftEvent, strategy: Strategy) -> str:
        """Build the reinjected text based on strategy."""
        parts = []

        if strategy == Strategy.STRATEGY_PREPEND_MANIFEST:
            if self._manifest_text:
                parts.append(self._manifest_text)

        elif strategy == Strategy.STRATEGY_PREPEND_FULL:
            if self._prompt_text:
                parts.append(self._prompt_text)
            if self._manifest_text:
                parts.append(self._manifest_text)

        elif strategy == Strategy.STRATEGY_RESET:
            if self._prompt_text:
                parts.append(self._prompt_text)
            parts.append("--- NEW CONTEXT START ---")
            breach_dims = [b.dimension for b in event.breaches]
            parts.append(
                f"[Context reset triggered: dimensions below threshold: {', '.join(breach_dims)}]"
            )

        return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# AuditLogger
# ---------------------------------------------------------------------------

class AuditLogger:
    """Logs reinjection events to JSONL file."""

    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or _PROJECT_DIR / "audit" / "adaptive_reinjection.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._cycle_id = self._load_next_cycle_id()

    def _load_next_cycle_id(self) -> int:
        if self.log_path.exists() and self.log_path.stat().st_size > 0:
            with open(self.log_path) as f:
                lines = f.readlines()
                if lines:
                    last = json.loads(lines[-1])
                    return last["cycle_id"] + 1
        return 1

    def log(self, reinjection: ReinjectionEvent,
            post_scores: Optional[dict] = None, recovered: Optional[bool] = None) -> AuditEntry:
        """Write audit entry. Returns the entry for inspection."""
        entry = AuditEntry(
            cycle_id=self._cycle_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trigger={
                "severity": reinjection.trigger_event.severity.value,
                "dims_breached": [b.dimension for b in reinjection.trigger_event.breaches],
                "pre_scores": reinjection.trigger_event.pre_scores,
                "baseline_scores": reinjection.trigger_event.baseline_scores,
                "total_drift": reinjection.trigger_event.total_drift,
            },
            action={
                "strategy": reinjection.strategy.value,
                "context_hash": reinjection.context_modified,
                "context_length": reinjection.context_modified_length,
                "manifest_included": reinjection.manifest_included,
                "full_prompt_included": reinjection.full_prompt_included,
            },
            result={
                "post_scores": post_scores,
                "recovered": recovered,
            },
        )

        with open(self.log_path, "a") as f:
            f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")

        self._cycle_id += 1
        return entry

    def read_log(self) -> list:
        if not self.log_path.exists():
            return []
        entries = []
        with open(self.log_path) as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        return entries


# ---------------------------------------------------------------------------
# Monitor — single-cycle programmatic entry point
# ---------------------------------------------------------------------------

class AdaptiveReinjectionMonitor:
    """End-to-end monitor: score text -> detect drift -> reinject -> log.

    Library usage:
        monitor = AdaptiveReinjectionMonitor()
        entry = monitor.process_file("target_file.txt", "baseline_file.txt")
    """

    def __init__(self, config: dict = None,
                 manifest_path: Optional[Path] = None,
                 prompt_path: Optional[Path] = None,
                 log_path: Optional[Path] = None):
        detector = DriftDetector(config)
        engine = ReinjectionEngine(manifest_path=manifest_path, prompt_path=prompt_path, config=config)
        logger = AuditLogger(log_path)
        self.detector = detector
        self.engine = engine
        self.logger = logger
        self.config = config or DEFAULT_CONFIG

    def process_file(self, target_path: str, baseline_path: str) -> Optional[AuditEntry]:
        """Process a target file against a baseline. Returns audit entry if drift detected.

        This is the primary library API. It:
        1. Scores baseline and target
        2. Checks for drift
        3. Triggers reinjection if needed
        4. Writes audit log
        """
        baseline_scores = score_text_from_file(baseline_path)
        current_scores = score_text_from_file(target_path)

        baseline_dim = baseline_scores["dimension_scores"]
        current_dim = current_scores["dimension_scores"]

        event = self.detector.evaluate(baseline_dim, current_dim)
        if not event:
            return None

        print(f"[AdaptiveReinjection] DRIFT DETECTED — severity={event.severity.value}, "
              f"breaches={len(event.breaches)}, drift={event.total_drift:+.4f}", file=sys.stderr)

        reinjection = self.engine.execute(event)
        print(f"[AdaptiveReinjection] Strategy: {reinjection.strategy.value}", file=sys.stderr)

        print(f"[AdaptiveReinjection] Reinjection text: {reinjection.context_modified_length} chars",
              file=sys.stderr)

        entry = self.logger.log(
            reinjection,
            post_scores=current_dim,
            recovered=None,
        )

        return entry

    def process_scores(self, baseline_dim_scores: dict,
                       current_dim_scores: dict) -> Optional[AuditEntry]:
        """Process pre-computed scores directly (for dashboard integration)."""
        event = self.detector.evaluate(baseline_dim_scores, current_dim_scores)
        if not event:
            return None

        print(f"[AdaptiveReinjection] DRIFT DETECTED — severity={event.severity.value}, "
              f"breaches={len(event.breaches)}, drift={event.total_drift:+.4f}", file=sys.stderr)

        reinjection = self.engine.execute(event)
        print(f"[AdaptiveReinjection] Strategy: {reinjection.strategy.value}", file=sys.stderr)

        entry = self.logger.log(
            reinjection,
            post_scores=current_dim_scores,
            recovered=None,
        )
        return entry

    def build_reinjection(self, baseline_dim_scores: dict,
                          current_dim_scores: dict) -> Optional[tuple]:
        """Build reinjection text without logging. Returns (event, reinjection_text, strategy)."""
        event = self.detector.evaluate(baseline_dim_scores, current_dim_scores)
        if not event:
            return None
        reinjection = self.engine.execute(event)
        return event, reinjection.reinjection_text, reinjection.strategy

    def get_reinjection_for_context(self, context: str, baseline_dim_scores: dict) -> Optional[str]:
        """Build reinjection text for an arbitrary context string.

        Returns the reinjection text to prepend, or None if no drift.
        """
        scores = score_text_from_file_from_text(context)
        return self.build_reinjection(baseline_dim_scores, scores["dimension_scores"])


def score_text_from_file_from_text(text: str) -> dict:
    """Compute alignment scores from a text string directly."""
    return compute_alignment_scores(text)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Adaptive Re-Injection for persona-v3")
    parser.add_argument("file", nargs="?", help="Target file to evaluate")
    parser.add_argument("--file", "-f", dest="target_file", action="append", default=None,
                        help="Target file (can specify multiple for --baseline)")
    parser.add_argument("--baseline", "-b", help="Baseline file (single file or CSV)")
    parser.add_argument("--watch", action="store_true",
                        help="Continuous file monitoring mode")
    parser.add_argument("--poll", type=int, default=10,
                        help="Poll interval in seconds (default: 10)")
    parser.add_argument("--output", help="Output reinjected text to file")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would happen without executing")
    parser.add_argument("--config", action="store_true",
                        help="Show current configuration")
    parser.add_argument("--audit", action="store_true",
                        help="Show audit log")
    parser.add_argument("--threshold", action="append", nargs=2, metavar=("DIM", "VALUE"),
                        help="Override threshold for dimension (can specify multiple)")

    args = parser.parse_args()

    # Handle both "adaptive_reinjection.py --file target --baseline base"
    # and "adaptive_reinjection.py target_file --baseline base_file" forms
    target_file = None
    baseline_file = None

    if hasattr(args, 'target_file') and args.target_file:
        if len(args.target_file) >= 2:
            target_file = args.target_file[-1]
            baseline_file = args.target_file[0] if args.target_file[0] != args.target_file[-1] else None
        else:
            target_file = args.target_file[0]
    elif hasattr(args, 'file') and args.file:
        target_file = args.file

    # Override with --baseline if not already set
    if not baseline_file and args.baseline:
        baseline_file = args.baseline

    # --config mode
    if args.config:
        print(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2))
        return

    # --audit mode
    if args.audit:
        logger = AuditLogger()
        entries = logger.read_log()
        if entries:
            print(json.dumps(entries, ensure_ascii=False, indent=2))
        else:
            print("No audit entries found.")
        return

    if not target_file:
        parser.print_help()
        return

    # Apply threshold overrides
    config = dict(DEFAULT_CONFIG)
    config["thresholds"] = dict(DEFAULT_CONFIG["thresholds"])
    if hasattr(args, 'threshold') and args.threshold:
        for dim, value in args.threshold:
            config["thresholds"][dim] = float(value)

    monitor = AdaptiveReinjectionMonitor(config=config)

    if args.watch:
        print(f"[AdaptiveReinjection] Starting continuous monitoring of {target_file}",
              file=sys.stderr)
        print("(Hit Ctrl-C to stop)", file=sys.stderr)
        try:
            while True:
                entry = monitor.process_file(target_file, baseline_file)
                if entry:
                    print(f"[AdaptiveReinjection] Cycle {entry.cycle_id}: {json.dumps(asdict(entry), ensure_ascii=False)}", file=sys.stderr)
                time.sleep(args.poll)
        except KeyboardInterrupt:
            print("\n[AdaptiveReinjection] Stopped.", file=sys.stderr)
        return

    # Single-run mode
    entry = monitor.process_file(target_file, baseline_file)

    if entry is None:
        print("[AdaptiveReinjection] No drift detected. Persona aligned.", file=sys.stderr)
        return

    if args.dry_run:
        print(json.dumps(asdict(entry), ensure_ascii=False, indent=2))
        return

    # Output results
    print("=" * 60, file=sys.stderr)
    print(f"Severity: {entry.trigger['severity']}", file=sys.stderr)
    print(f"Strategy: {entry.action['strategy']}", file=sys.stderr)
    print(f"Dims breached: {', '.join(entry.trigger['dims_breached'])}", file=sys.stderr)
    print(f"Drift: {entry.trigger['total_drift']:+.4f}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"\nReinjection text ({entry.action['context_length']} chars):", file=sys.stderr)
    print(entry.trigger["baseline_scores"])


if __name__ == "__main__":
    main()
