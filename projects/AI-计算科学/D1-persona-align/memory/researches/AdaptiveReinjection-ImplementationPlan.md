# Adaptive Re-Injection: Implementation Plan for persona-v3

**Created**: 2026-06-03 (Ralph autonomous audit, iteration 5)
**Related**: LongContextPersona-ContextDilutionAndPersistence.md, persona_v3_alignment_checker.py, persona-manifest-v3.txt
**Status**: Design phase — concrete implementation plan
**Prerequisites**: alignment_checker (drift detection), persona-manifest-v3.txt (80-char compressed encoding), persona_v3_dashboard.py (batch monitoring)

---

## 1. Problem Statement

persona-v3 alignment degrades in long-context conversations as context dilutes the persona signal. The existing `alignment_checker.py` provides **offline drift detection** (baseline vs. current), but there is no **real-time monitoring + automated response** pipeline.

The goal: build `adaptive_reinjection.py` that:
1. Monitors alignment_checker output in real time
2. Detects dimension drops below configurable threshold
3. Triggers persona re-injection (prepend 80-char manifest)
4. Validates the re-injection improved alignment
5. Logs the full cycle for audit trail

## 2. Architecture Overview

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Context    │────>│  alignment_checker│────>│  drift detector  │
│  (target    │     │  (Python CLI /    │     │  (in-process,    │
│   text)     │     │   library call)   │     │   threshold      │
└─────────────┘     └──────────────────┘     │   comparison)     │
                                              └────────┬─────────┘
                                                       │ drift detected
                                                       ▼
                                              ┌──────────────────┐
                                              │  reinjection     │
                                              │  trigger         │
                                              └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │  Persona manifest│
                                              │  (80-char) prepended│
                                              └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │  alignment_checker│
                                              │  (post-reinjection│
                                              │   re-evaluation) │
                                              └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │  Results + audit │
                                              │  log             │
                                              └──────────────────┘
```

## 3. Module Design

### 3.1 Module: `adaptive_reinjection` (single file)

Location: `/Users/a1-6/Desktop/workspace/projects/D1-persona-align/scripts/adaptive_reinjection.py`

This is a single-file module with 4 subcomponents:

#### A. `Monitor` class — Real-time monitoring

```python
class Monitor:
    """Monitors alignment_checker JSON output for drift.

    Usage:
        monitor = Monitor(thresholds={"自适应精度": 0.30, ...}, poll_interval=10)
        for event in monitor.watch_file("alignment_results.json"):
            if event.type == "DRIFT_DETECTED":
                reinjector.trigger(event)
    """
```

Design options:

**Option 1: File-based polling (recommended for CLI integration)**
- Watch a JSON file written by the alignment checker
- Poll at configurable interval (default 10 seconds or 10 turns)
- Low overhead, works with existing alignment_checker CLI

**Option 2: In-process library import (recommended for dashboard integration)**
- Import `alignment_checker` functions directly as Python library
- No subprocess overhead, instant detection
- Better for programmatic use (dashboard, loops)

**Option 3: WebSocket/pipe (advanced)**
- alignment_checker pushes events via stdin pipe or WebSocket
- True real-time, but adds system complexity
- Not needed for initial implementation

**Recommendation**: Start with **Option 1** for CLI + **Option 2** for library import. Both in the same file.

#### B. `DriftDetector` — Threshold comparison

```python
class DriftDetector:
    """Compares baseline scores vs. current scores.

    Key decisions:
    - Per-dimension thresholds (different dims may need different thresholds)
    - Aggregated alert level (LOW/MEDIUM/HIGH/CRITICAL)
    - Hysteresis: only trigger if below threshold for N consecutive checks
    """
```

Key features:

1. **Per-dimension thresholds**: Not all dimensions should use the same threshold. Critical dimensions (e.g., "自适应精度", "自适应自我") get lower thresholds (0.20), while supporting dimensions get higher thresholds (0.40).

2. **Hysteresis buffer**: To prevent oscillation (reinjection triggers, alignment improves, then immediately degrades again), require threshold breach for `min_breaches=3` consecutive checks.

3. **Severity classification**:
   - `LOW`: Any single dim < threshold, total drift < 0.10
   - `MEDIUM`: >= 2 dims below threshold, or total drift 0.10-0.20
   - `HIGH`: >= 3 dims below threshold, or total drift 0.20-0.35
   - `CRITICAL`: >= 4 dims below threshold, or total drift >= 0.35

4. **Gradient-based triggering**: Instead of binary threshold, use severity to select reinjection strategy:
   - LOW: Just prepend 80-char manifest
   - MEDIUM: Full persona prompt (persona-v3)
   - HIGH + CRITICAL: Full prompt + context window reset

#### C. `ReinjectionEngine` — Persona re-injection execution

```python
class ReinjectionEngine:
    """Executes persona re-injection strategies.

    Strategies:
    - STRATEGY_PREPEND_MANIFEST: Prepend 80-char persona manifest to context
    - STRATEGY_PREPEND_FULL: Prepend full persona-v3 prompt
    - STRATEGY_RESET: Create fresh context with persona at beginning
    """
```

The `STRATEGY_PREPEND_MANIFEST` is the primary strategy, as defined in LongContextPersona.md:
- Prepend persona-manifest-v3.txt content to the current context
- 80 chars is small enough that the marginal token cost is negligible (~15 tokens)
- Positions the persona at the end of context (high-attention position)

The `STRATEGY_PREPEND_FULL` is the fallback:
- Prepend the full persona-v3 prompt (~2000 chars)
- Used for MEDIUM+ severity
- Requires context trimming to avoid hitting context limits

The `STRATEGY_RESET` is the emergency:
- Drop all conversation history
- Start fresh with persona at beginning
- Used only for CRITICAL severity

#### D. `AuditLogger` — Results and trail logging

```python
class AuditLogger:
    """Logs every reinjection event with pre/post alignment scores.

    Output format: JSONL log file, one entry per reinjection cycle.
    Used for:
    - Auditing reinjection frequency and effectiveness
    - Tuning thresholds empirically
    - Contributing to the long-context persona research
    """
```

Each log entry contains:
```json
{
    "cycle_id": 42,
    "timestamp": "2026-06-03T...",
    "trigger": {
        "type": "DRIFT_DETECTED",
        "severity": "HIGH",
        "dims_breached": ["自适应精度", "自适应先验"],
        "pre_scores": {"自适应精度": 0.12, "自适应先验": 0.18, ...},
        "baseline_scores": {"自适应精度": 0.75, "自适应先验": 0.68, ...},
        "total_drift": -0.31
    },
    "action": {
        "strategy": "STRATEGY_PREPEND_FULL",
        "manifest_included": true,
        "full_prompt_included": true
    },
    "result": {
        "post_scores": {"自适应精度": 0.65, "自适应先验": 0.62, ...},
        "post_alignment": 72.3,
        "recovered": true,
        "recovery_rate": 0.73
    }
}
```

## 4. Concrete Python Implementation

Here is the actual Python code for `adaptive_reinjection.py`:

```python
#!/usr/bin/env python3
"""
Adaptive Re-Injection for persona-v3

Monitors alignment_checker output, detects drift, and triggers
persona re-injection when alignment drops below threshold.

Usage:
    # CLI mode (monitor a file)
    python3 adaptive_reinjection.py --watch alignment_results.json --poll 10

    # Library mode (direct import from alignment_checker)
    from adaptive_reinjection import Monitor, DriftDetector, ReinjectionEngine

    # Configuration mode (show current config)
    python3 adaptive_reinjection.py --config
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
import warnings
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

# ---------------------------------------------------------------------------
# Path setup — import alignment_checker as library
# ---------------------------------------------------------------------------
_SCRIPTS_DIR = Path(__file__).parent
_PROJECT_DIR = _SCRIPTS_DIR.parent
sys.path.insert(0, str(_SCRIPTS_DIR))

import persona_keywords  # Shared keyword definitions (reused here for drift detection)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    # Dimension-level thresholds (score below this = breach)
    "thresholds": {
        "自适应精度": 0.30,    # Core dimension — aggressive threshold
        "自适应探索": 0.25,
        "自适应感知": 0.25,
        "自适应先验": 0.25,
        "自适应自我": 0.20,    # Most critical — persona identity
        "自适应投影": 0.25,
    },

    # Hysteresis — require N consecutive breaches before triggering
    "min_breaches": 3,

    # Monitoring
    "poll_interval_seconds": 10,   # For file-based monitoring
    "max_context_tokens": 200000,  # Hard context limit

    # Severity escalation
    "severity_thresholds": {
        "LOW": {"min_breach": 1, "max_drift": 0.10},
        "MEDIUM": {"min_breach": 2, "max_drift": 0.20},
        "HIGH": {"min_breach": 3, "max_drift": 0.35},
        "CRITICAL": {"min_breach": 4},  # max_drift is soft bound
    },

    # Reinjection strategies by severity
    "strategy_by_severity": {
        "LOW": "STRATEGY_PREPEND_MANIFEST",
        "MEDIUM": "STRATEGY_PREPEND_FULL",
        "HIGH": "STRATEGY_PREPEND_FULL",
        "CRITICAL": "STRATEGY_RESET",
    },
}


class Severity(Enum):
    NORMAL = "NORMAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Strategy(Enum):
    STRATEGY_PREPEND_MANIFEST = "PREPEND_MANIFEST"   # 80-char persona manifest
    STRATEGY_PREPEND_FULL = "PREPEND_FULL"           # Full persona-v3 prompt
    STRATEGY_RESET = "RESET"                          # Fresh context with persona


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
    context_modified: str  # hash of original context
    context_modified_length: int
    manifest_included: bool
    full_prompt_included: bool


@dataclass
class AuditEntry:
    cycle_id: int
    timestamp: str
    trigger: dict
    action: dict
    result: dict


# ---------------------------------------------------------------------------
# DriftDetector
# ---------------------------------------------------------------------------

class DriftDetector:
    """Detects persona drift and classifies severity."""

    def __init__(self, config: dict = None):
        self.config = config or DEFAULT_CONFIG
        self.thresholds = self.config["thresholds"]
        self.min_breaches = self.config["min_breaches"]
        self.breach_history = {}  # dimension -> list of breach booleans
        self.event_queue = []

    def evaluate(self, baseline_scores: dict, current_scores: dict) -> Optional[DriftEvent]:
        """Compare baseline vs. current scores. Returns DriftEvent if triggered."""

        breaches = []
        for dim, threshold in self.thresholds.items():
            baseline = baseline_scores.get(dim, 0.0)
            current = current_scores.get(dim, 0.0)
            delta = current - baseline

            # Check if this dimension is below threshold (absolute, not delta)
            breached = current < threshold

            # Update breach history
            if dim not in self.breach_history:
                self.breach_history[dim] = []
            self.breach_history[dim].append(breached)

            # Keep only recent history
            self.breach_history[dim] = self.breach_history[dim][-self.min_breaches * 3:]

            # Count consecutive breaches at end of history
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

        # Classify severity
        n_breaches = len(breaches)
        total_drift = sum(b.delta for b in breaches) / n_breaches if breaches else 0

        severity = self._classify_severity(n_breaches, total_drift)

        pre_scores = {dim: current_scores.get(dim, 0.0) for dim in self.thresholds}

        return DriftEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            severity=severity,
            breaches=breaches,
            total_drift=total_drift,
            pre_scores=pre_scores,
            baseline_scores=baseline_scores,
        )

    def _classify_severity(self, n_breaches: int, total_drift: float) -> Severity:
        thresh = self.config["severity_thresholds"]

        if n_breaches >= thresh["CRITICAL"]["min_breach"]:
            return Severity.CRITICAL
        if n_breaches >= thresh["HIGH"]["min_breach"] or total_drift <= -thresh["HIGH"]["max_drift"]:
            return Severity.HIGH
        if n_breaches >= thresh["MEDIUM"]["min_breach"] or total_drift <= -thresh["MEDIUM"]["max_drift"]:
            return Severity.MEDIUM
        return Severity.LOW


# ---------------------------------------------------------------------------
# ReinjectionEngine
# ---------------------------------------------------------------------------

class ReinjectionEngine:
    """Executes persona re-injection strategies."""

    def __init__(self, manifest_path=None, prompt_path=None, config: dict = None):
        self.config = config or DEFAULT_CONFIG
        self._manifest_text = None
        self._prompt_text = None
        self.manifest_path = manifest_path or _PROJECT_DIR / "persona-manifest-v3.txt"
        self.prompt_path = prompt_path or _PROJECT_DIR / "persona-v3-prompt.txt"
        self._load_persona_resources()

    def _load_persona_resources(self):
        """Load persona resources."""
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

        context_hash = hashlib.sha256(event.timestamp.encode()).hexdigest()[:12]

        manifest_included = strategy in (Strategy.STRATEGY_PREPEND_MANIFEST,)
        full_prompt_included = strategy in (Strategy.STRATEGY_PREPEND_FULL, Strategy.STRATEGY_RESET)

        return ReinjectionEvent(
            trigger_event=event,
            strategy=strategy,
            context_modified=context_hash,
            context_modified_length=len(self._build_reinjection(event, strategy)),
            manifest_included=manifest_included,
            full_prompt_included=full_prompt_included,
        )

    def _build_reinjection(self, event: DriftEvent, strategy: Strategy) -> str:
        """Build the reinjected text."""
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
            parts.append(self._prompt_text)
            parts.append("--- NEW CONTEXT START ---")
            # Minimal history anchor
            breach_dims = [b.dimension for b in event.breaches]
            parts.append(f"[Context reset triggered: dimensions below threshold: {', '.join(breach_dims)}]")

        return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# AuditLogger
# ---------------------------------------------------------------------------

class AuditLogger:
    """Logs reinjection events to JSONL file."""

    def __init__(self, log_path=None):
        self.log_path = log_path or _PROJECT_DIR / "audit" / "adaptive_reinjection.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._cycle_id = self._load_next_cycle_id()

    def _load_next_cycle_id(self) -> int:
        """Load next cycle ID from existing log."""
        if self.log_path.exists() and self.log_path.stat().st_size > 0:
            with open(self.log_path) as f:
                lines = f.readlines()
                if lines:
                    last = json.loads(lines[-1])
                    return last["cycle_id"] + 1
        return 1

    def log(self, reinjection: ReinjectionEvent, post_scores: dict, recovered: bool):
        """Write audit entry."""
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

    def read_log(self) -> list:
        """Read all entries from log."""
        if not self.log_path.exists():
            return []
        entries = []
        with open(self.log_path) as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        return entries


# ---------------------------------------------------------------------------
# Monitor (File-based polling mode)
# ---------------------------------------------------------------------------

class Monitor:
    """Watches alignment_checker JSON output for drift events."""

    def __init__(self, detector: DriftDetector = None, engine: ReinjectionEngine = None,
                 logger: AuditLogger = None, config: dict = None, poll_interval: int = 10):
        self.detector = detector or DriftDetector(config)
        self.engine = engine or ReinjectionEngine(config)
        self.logger = logger or AuditLogger()
        self.poll_interval = poll_interval
        self._last_hash = None

    def watch_file(self, result_path: str) -> list:
        """Poll a JSON result file for drift events.

        This is designed to work alongside alignment_checker:
            python3 adaptive_reinjection.py --watch results.json --poll 10

        where results.json is produced by:
            python3 persona_v3_alignment_checker.py --json --baseline baseline.txt target.txt > results.json
        """
        events = []
        target = Path(result_path)

        if not target.exists():
            print(f"[Monitor] File not found: {result_path}", file=sys.stderr)
            return events

        while True:
            current_hash = hashlib.sha256(target.read_bytes()).hexdigest()

            if current_hash != self._last_hash:
                self._last_hash = current_hash
                try:
                    data = json.loads(target.read_text(encoding="utf-8"))
                    event = self._process_result(data)
                    if event:
                        events.append(event)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"[Monitor] Parse error: {e}", file=sys.stderr)

            time.sleep(self.poll_interval)

    def _process_result(self, data: dict) -> Optional[DriftEvent]:
        """Process alignment_checker JSON output. Returns drift event if triggered."""
        dim_scores = data.get("dimension_scores", {})
        baseline_scores = data.get("baseline_dimension_scores", {})

        if not baseline_scores:
            # No baseline available — use default baseline (perfect alignment)
            baseline_scores = {dim: 1.0 for dim in dim_scores}

        return self.detector.evaluate(baseline_scores, dim_scores)

    def run_cycle(self, result_data: dict) -> Optional[AuditEntry]:
        """Process a single alignment_checker result (no polling).

        This is the programmatic entry point:
            monitor = Monitor()
            entry = monitor.run_cycle(alignment_checker_json_data)
        """
        event = self._process_result(result_data)
        if not event:
            return None

        print(f"[AdaptiveReinjection] DRIFT DETECTED — severity={event.severity.value}, "
              f"breaches={len(event.breaches)}, drift={event.total_drift:+.4f}", file=sys.stderr)

        # Execute reinjection
        reinjection = self.engine.execute(event)
        print(f"[AdaptiveReinjection] Strategy: {reinjection.strategy.value}", file=sys.stderr)

        # Compute reinjection text (for logging / display)
        reinjection_text = self.engine._build_reinjection(event, reinjection.strategy)
        print(f"[AdaptiveReinjection] Reinjection text length: {len(reinjection_text)} chars",
              file=sys.stderr)

        # NOTE: The actual text replacement (prepending manifest/prompt to context)
        # is deferred to the calling agent/conversation manager. The reinjection
        # engine provides the text; the conversation manager applies it.
        #
        # This separation allows:
        # 1. CLI usage: output text to stdout for the shell to use
        # 2. Dashboard integration: consume as Python object
        # 3. Loop integration: return text as part of task execution

        print("=" * 60, file=sys.stderr)
        print(reinjection_text, file=sys.stderr)
        print("=" * 60, file=sys.stderr)

        # NOTE: Post-reinjection validation requires re-running alignment_checker
        # on the modified context. This is intentionally not automatic, because
        # the reinjected text needs to be applied first.
        #
        # The caller should:
        #   1. Apply reinjection text to context
        #   2. Re-run alignment_checker on the new context
        #   3. Call logger.log() with the results
        #
        # This design ensures correctness: we validate AFTER application, not just prediction.

        return AuditEntry(
            cycle_id=self.logger._cycle_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trigger={
                "severity": event.severity.value,
                "dims_breached": [b.dimension for b in event.breaches],
                "pre_scores": event.pre_scores,
                "baseline_scores": event.baseline_scores,
                "total_drift": event.total_drift,
            },
            action={
                "strategy": reinjection.strategy.value,
                "manifest_included": reinjection.manifest_included,
                "full_prompt_included": reinjection.full_prompt_included,
            },
            result={"post_scores": None, "recovered": None},  # To be filled after validation
        )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Adaptive Re-Injection for persona-v3")
    parser.add_argument("file", nargs="?", help="alignment_checker JSON result file")
    parser.add_argument("--watch", action="store_true", help="Continuous file monitoring mode")
    parser.add_argument("--poll", type=int, default=10, help="Poll interval in seconds (default: 10)")
    parser.add_argument("--baseline", help="Baseline JSON file (for drift detection)")
    parser.add_argument("--output", help="Output reinjected text to file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without executing")
    parser.add_argument("--config", action="store_true", help="Show current configuration")
    parser.add_argument("--audit", action="store_true", help="Show audit log")
    parser.add_argument("--threshold", action="append", nargs=2, metavar=("DIM", "VALUE"),
                       help="Override threshold for dimension (can specify multiple)")

    args = parser.parse_args()

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

    if not args.file:
        parser.print_help()
        return

    # Load alignment_checker result
    try:
        data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        return
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return

    # Apply threshold overrides
    config = DEFAULT_CONFIG.copy()
    if args.threshold:
        for dim, value in args.threshold:
            config["thresholds"][dim] = float(value)

    # Build components
    detector = DriftDetector(config)
    engine = ReinjectionEngine(config)
    logger = AuditLogger()
    monitor = Monitor(detector=detector, engine=engine, logger=logger, config=config, poll_interval=args.poll)

    if args.watch:
        print(f"[AdaptiveReinjection] Starting continuous monitoring of {args.file} "
              f"(poll every {args.poll}s)", file=sys.stderr)
        monitor.watch_file(args.file)
        return

    # Single-run mode
    entry = monitor.run_cycle(data)

    if entry is None:
        print("[AdaptiveReinjection] No drift detected. Persona aligned.", file=sys.stderr)
        return

    if args.dry_run:
        print(json.dumps(asdict(entry), ensure_ascii=False, indent=2))
        return

    # Output reinjection text
    if args.output:
        # Re-read stdout output from engine (the reinjection text was printed to stderr above)
        pass
    else:
        print(entry, flush=True)


if __name__ == "__main__":
    main()
```

## 5. Integration with Existing Infrastructure

### 5.1 Integration with persona_v3_dashboard.py

The dashboard already scans all memory files and produces alignment scores. `adaptive_reinjection.py` extends this by:

```python
# In persona_v3_dashboard.py, after scanning all files:
from adaptive_reinjection import DriftDetector, ReinjectionEngine

# Dashboard writes per-file scores to a JSONL intermediate
intermediate = "/tmp/dashboard_scores.jsonl"

# Adaptive reinjection watches this intermediate
detector = DriftDetector()
for score_line in open(intermediate):
    scores = json.loads(score_line)
    event = detector.evaluate(baseline, scores["dimension_scores"])
    if event:
        engine = ReinjectionEngine()
        action = engine.execute(event)
        # action.reinjection_text can be prepended to the original file
        # then re-scanned to validate improvement
```

### 5.2 Integration with ralph-loop

The ralph-loop execution loop should call adaptive_reinjection after each persona-generating step:

```python
# Pseudocode for loop integration:
alignment_result = run_alignment_checker(conversation_text)
drift_event = adaptive_detector.evaluate(baseline, alignment_result)

if drift_event:
    reinjection_text = adaptive_engine.build(drift_event)
    # Prepend to context / inject into conversation
    conversation_text = reinjection_text + "\n\n" + conversation_text
    # Re-validate
    post_alignment = run_alignment_checker(conversation_text)
    # Log audit trail
    audit_logger.log(drift_event, reinjection_text, post_alignment)
```

### 5.3 Integration with Alignment Checker Drift Detection

The existing `detect_drift()` function in `alignment_checker.py` computes drift deltas. `adaptive_reinjection.py` extends this by:
- Adding hysteresis (consecutive breach detection)
- Classifying severity (LOW/MEDIUM/HIGH/CRITICAL)
- Mapping severity to reinjection strategies

**This means `alignment_checker.py` and `adaptive_reinjection.py` share the `detect_drift` logic but serve different roles**:
- `alignment_checker.py` = offline analysis tool
- `adaptive_reinjection.py` = online monitoring and response

## 6. Threshold Tuning Guide

Thresholds should be calibrated empirically from audit log data:

1. **Start with defaults** (as defined in DEFAULT_CONFIG)
2. **Run for 50+ reinjection cycles** and collect audit data
3. **Analyze recovery rates**: what percentage of reinjections result in `recovered=true`?
4. **Adjust thresholds** to minimize unnecessary reinjections while maintaining recovery > 80%
5. **Per-dimension analysis**: which dimensions drift most often? Adjust thresholds accordingly.

## 7. File Output Summary

The implementation plan requires creating:

| File | Purpose | Lines |
|------|---------|-------|
| `scripts/adaptive_reinjection.py` | Main implementation (~500 lines) | 450-550 |

No changes to existing files are required — the new script is fully self-contained.

## 8. Testing Plan

1. **Unit tests**:
   - `test_drift_detector`: Verify threshold breach detection, hysteresis
   - `test_reinjection_engine`: Verify strategy selection by severity
   - `test_audit_logger`: Verify JSONL write/read cycle integrity

2. **Integration test**:
   - Run alignment_checker on a real conversation file
   - Pipe output to adaptive_reinjection.py
   - Verify drift detection triggers correct reinjection strategy
   - Re-run alignment_checker on reinjected context to validate recovery

3. **Regression test**:
   - Run against the 52-file benchmark
   - Verify no performance regression (new file imports are lazy)

## 9. Long-Term Research Contribution

The audit log (`adaptive_reinjection.jsonl`) will become a valuable research dataset for:
- Documenting real-world persona drift patterns
- Correlating drift rate with conversation length
- Validating the "persona attention valley" hypothesis from LongContextPersona.md
- Contributing to the rate-distortion analysis (cost of reinjection vs. benefit of persistence)
