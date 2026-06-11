#!/usr/bin/env python3
"""
persona-v3 English Alignment Checker

English-language variant of the persona-v3 alignment checker.
Optimized for English academic and technical writing.

Usage:
    python3 persona_v3_alignment_checker_en.py <text_file>
    python3 persona_v3_alignment_checker_en.py --stdin
    python3 persona_v3_alignment_checker_en.py --show-sources
"""

import re
import sys
import json
import argparse
from pathlib import Path


DIMENSION_KEYWORDS = {
    "Adaptive Precision": [
        ("rate-distortion", 2.0), ("R(D)", 2.0), ("compression", 0.5), ("precision", 1.0), ("granularity", 0.5),
        ("bitrate", 0.5), ("signal-to-noise", 0.5), ("SNR", 0.5), ("info density", 0.5), ("information density", 1.0),
        ("perceptual accuracy", 0.5), ("analysis fidelity", 0.5), ("token precision", 1.0),
        ("adaptive precision", 2.0), ("precision level", 0.5), ("precision allocation", 0.5),
        ("lossy compression", 1.0), ("distortion", 0.5), ("information budget", 0.5),
        ("fine-grained", 0.5), ("coarse-grained", 0.5), ("coarse", 0.5),
    ],
    "Adaptive Exploration": [
        ("exploration", 1.0), ("exploit", 1.0), ("exploration-exploitation", 2.0),
        ("exploration frequency", 1.0), ("exploration strategy", 1.0),
        ("tool selection", 1.5), ("new tool", 0.5), ("reused tool", 1.0), ("existing tool", 0.5),
        ("sharpen the axe", 1.0), ("search for", 0.5), ("look for", 0.5), ("alternative approach", 0.5),
        ("suboptimal", 0.5), ("optimal", 0.5), ("explore new", 0.5),
    ],
    "Adaptive Perception": [
        ("perception", 1.0), ("perceptual", 0.5), ("sensory", 0.5), ("information density", 1.0),
        ("signal", 0.5), ("noise", 0.5), ("signal-to-noise", 1.0), ("SNR", 1.0), ("signal quality", 0.5),
        ("perception time", 1.5), ("t_p", 1.5), ("perception rate", 1.5), ("R_max", 1.5),
        ("perception resource", 0.5), ("perception level", 0.5), ("coarse perception", 0.5),
        ("fine perception", 0.5), ("perception granularity", 0.5),
        ("observer effect", 0.5), ("measurement error", 0.5), ("perceptual error", 0.5),
        ("fidelity", 0.5), ("high-fidelity", 0.5), ("low-fidelity", 0.5),
    ],
    "Adaptive Prior": [
        ("prior", 1.0), ("posterior", 1.0), ("prior distribution", 1.5), ("initial belief", 1.5),
        ("Bayesian", 1.5), ("Bayes", 1.5), ("p(h|e)", 1.5), ("p(e|h)", 1.5), ("likelihood", 1.0),
        ("pretraining", 0.5), ("pre-trained", 0.5), ("evolutionary", 0.5), ("bio", 0.5),
        ("cognitive structure", 1.0), ("cognitive path", 0.5), ("initial setting", 0.5),
        ("priors", 0.5), ("p(h)", 0.5), ("p(e)", 0.5), ("prior belief", 1.0), ("belief update", 1.0),
        ("theta_bio", 1.0), ("evolutionary prior", 0.5),
    ],
    "Adaptive Self": [
        ("observer", 1.0), ("observer-dependent", 2.0), ("observer-dependence", 2.0),
        ("first-person", 1.0), ("third-person", 1.0), ("subjective", 0.5), ("objective", 0.5),
        ("perspective", 0.5), ("point of view", 0.5), ("vantage point", 0.5),
        ("self-centered", 0.5), ("self-referential", 0.5), ("self-model", 0.5),
        ("y(theta)", 1.0), ("y(θ)", 1.5), ("observer-environment", 2.0),
        ("different observers", 1.5), ("observing position", 0.5), ("positional", 0.5),
    ],
    "Adaptive Projection": [
        ("projection", 1.0), ("low-dimensional", 2.0), ("dimensional reduction", 1.0),
        ("cross-domain", 2.0), ("analog", 0.5), ("analogy", 0.5), ("isomorphic", 1.5), ("isomorphism", 1.5),
        ("mapping", 1.0), ("map to", 0.5), ("maps to", 0.5), ("analogous to", 0.5),
        ("information bottleneck", 1.0), ("mutual information", 1.0), ("I(X;Y)", 1.5),
        ("KL divergence", 1.0), ("D_KL", 1.0), ("cross-entropy", 0.5),
        ("invariant", 1.0), ("topology", 0.5), ("topological", 0.5),
        ("similar structure", 0.5), ("same underlying structure", 0.5),
        ("different domains", 0.5), ("unrelated domains", 0.5),
    ],
}

# ReportBench dimensions: Citation Relevance & Factual Faithfulness
CITATION_RELEVANCE_KEYWORDS = [
    ("citation relevance", 2.0), ("source relevance", 2.0), ("literature support", 2.0),
    ("citation", 1.0), ("reference", 1.0), ("source", 1.0), ("evidence", 1.0),
    ("data support", 1.0), ("empirical support", 1.0), ("supporting evidence", 0.5),
    ("according to", 0.5), ("study shows", 0.5), ("research indicates", 0.5),
    ("empirical", 0.5), ("experimental support", 0.5), ("study confirms", 0.5),
    ("literature review", 0.5), ("meta-analysis", 0.5), ("systematic review", 0.5),
    ("bibliography", 0.5), ("referenced", 0.5), ("source reliability", 0.5),
    ("cited", 0.5), ("in the literature", 0.5), ("previous studies", 0.5),
]

FACTUAL_FAITHFULNESS_KEYWORDS = [
    ("factual faithfulness", 2.0), ("fact-check", 2.0), ("verifiable", 2.0),
    ("falsifiable", 2.0), ("external source", 1.0), ("cross-validate", 1.0),
    ("cross-validation", 1.0), ("third-party", 1.0), ("independent source", 1.0),
    ("empirical claim", 1.0), ("verifiable", 1.0), ("replicable", 1.0),
    ("data source", 1.0), ("reproducible", 1.0), ("empirical data", 0.5),
    ("statistically", 0.5), ("data-backed", 0.5), ("numerical", 0.5),
    ("percentage", 0.5), ("ratio", 0.5), ("measure", 0.5), ("metric", 0.5),
    ("quantify", 0.5), ("measurement tool", 0.5), ("reliability", 0.5),
    ("validity", 0.5), ("ground truth", 0.5),
]

GENERAL_INFO_THEORY = [
    "information theory", "entropy", "mutual information", "shannon",
    "information flow", "channel", "encoding", "decoding", "compression",
    "information density", "maxent", "maximum entropy",
    "rate-distortion", "information gain", "bayesian", "bayes",
    "posterior", "prior", "likelihood", "inference",
]

VERIFICATION_PATTERNS = [
    r"why.*not.*but",        # boundary questioning
    r"why.*is.*not.*",       # boundary questioning
    r"question.*boundary",   # boundary awareness
    r"boundary.*condition",  # boundary awareness
    r"limitation",           # self-criticism
    r"limit",                # boundary awareness
    r"scope.*limit",         # boundary awareness
    r"assumption.*hold",     # boundary awareness
    r"plausibly.*exogenous", # boundary awareness
    r"equivalent.*",         # isomorphism identification
    r"isomorphic.*",         # isomorphism identification
    r"analogous.*",          # mapping identification
    r"map.*onto",            # mapping identification
    r"maps.*onto",           # mapping identification
    r"maps.*to",             # mapping identification
    r"thus.*",               # reasoning chain
    r"therefore.*",          # reasoning chain
    r"consequently.*",       # reasoning chain
    r"correspond.*",         # correspondence
    r"not.*but.*",           # negation-affirmation
    r"neither.*nor.*",       # negation
    r"switch.*",             # adaptive switching
    r"optimize.*",           # optimization
    r"maximiz.*",            # maximization
    r"constraint.*",         # constraint language
    r"trade-off",            # trade-off awareness
    r"accuracy.",            # accuracy awareness
    r"sufficien.*",          # sufficiency
    r"under what condition.*not.*",  # boundary condition questioning
    r"when.*not.*",          # scenario constraint (timeline consistency)
    r"gap",                  # gap detection
    r"follow.up",            # follow-up question
    r"self.answer",          # self-answering
    r"confidence",           # confidence labeling
]

BEHAVIORAL_CONSTRAINTS = {
    "Concise & Direct": {
        "description": "Output is concise and direct, with minimal filler",
        "positive_patterns": [
            r"conclusion", r"key finding", r"key observation", r"core",
            r"directly", r"explicitly", r"clearly",
        ],
        "negative_patterns": [
            r"in conclusion", r"to summarize", r"overall", r"generally",
            r"it is important to note", r"in the context of",
            r"it should be noted that",
        ],
    },
    "No Over-Explanation": {
        "description": "Does not over-explain known concepts or show thinking process",
        "positive_patterns": [
            r"equation", r"model", r"assumption", r"method",
            r"we show that", r"we demonstrate", r"we propose",
        ],
        "negative_patterns": [
            r"this means that", r"in other words", r"that is to say",
            r"let me explain", r"as the reader may know",
        ],
    },
    "Progress > Stagnation": {
        "description": "Advances concrete actions, does not wait for confirmation",
        "positive_patterns": [
            r"next", r"future work", r"open question", r"remains to",
        ],
        "negative_patterns": [
            r"waiting for", r"pending confirmation", r"upon your feedback",
        ],
    },
}

# Detection thresholds
DIMENSION_THRESHOLD = 0.3  # A dimension is "present" if matched >= 30% of keywords
VERIFICATION_THRESHOLD = 0.3  # A verification pattern is "present" if matched


def detect_dimensions(text):
    """Detect dimension coverage — weighted keyword matching."""
    scores = {}
    for dim_name, kw_list in DIMENSION_KEYWORDS.items():
        total_weight = 0.0
        matched_weight = 0.0
        for kw, weight in kw_list:
            if re.search(kw, text, re.IGNORECASE):
                matched_weight += weight
            total_weight += weight
        scores[dim_name] = round(matched_weight / total_weight if total_weight > 0 else 0, 4)
    return scores


def detect_citation_relevance(text):
    """Detect citation relevance score (ReportBench dimension)."""
    text_lower = text.lower()
    total_weight = 0.0
    matched_weight = 0.0
    for kw, weight in CITATION_RELEVANCE_KEYWORDS:
        if kw.lower() in text_lower:
            matched_weight += weight
        total_weight += weight
    return round(min(matched_weight / total_weight, 1.0), 4) if total_weight > 0 else 0


def detect_factual_faithfulness(text):
    """Detect factual faithfulness score (ReportBench dimension)."""
    text_lower = text.lower()
    total_weight = 0.0
    matched_weight = 0.0
    for kw, weight in FACTUAL_FAITHFULNESS_KEYWORDS:
        if kw.lower() in text_lower:
            matched_weight += weight
        total_weight += weight
    return round(min(matched_weight / total_weight, 1.0), 4) if total_weight > 0 else 0


def detect_general_info_theory(text):
    """Detect general information theory keyword coverage."""
    matched = 0
    for kw in GENERAL_INFO_THEORY:
        if re.search(kw, text, re.IGNORECASE):
            matched += 1
    return round(matched / len(GENERAL_INFO_THEORY), 4)


def detect_verification_patterns(text):
    """Detect verification pattern coverage."""
    matched = 0
    total = len(VERIFICATION_PATTERNS)
    for pattern in VERIFICATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            matched += 1
    return round(matched / total, 4)


def detect_behavioral_constraints(text):
    """Detect behavioral constraint compliance.

    For English academic writing, this returns None (not applicable)
    because the constraints are designed for conversational AI output.
    """
    scores = {}
    for cname, info in BEHAVIORAL_CONSTRAINTS.items():
        pos_patterns = info["positive_patterns"]
        neg_patterns = info["negative_patterns"]

        pos = sum(1 for p in pos_patterns if re.search(p, text, re.IGNORECASE))
        neg = sum(1 for p in neg_patterns if re.search(p, text, re.IGNORECASE))

        total = len(pos_patterns) + len(neg_patterns)
        score = max(0, pos / len(pos_patterns) - neg / len(neg_patterns))
        scores[cname] = round(min(score, 1.0), 4)

    overall = sum(scores.values()) / len(scores) if scores else 0
    return scores, round(overall, 4)


def compute_alignment_score(dim_scores, general_cov, verification_ratio, behavioral_ratio=None, citation_rel=None, fact_faul=None):
    """Compute overall alignment score."""
    dim_coverage = sum(dim_scores.values()) / len(dim_scores) if dim_scores else 0

    if citation_rel is not None and fact_faul is not None:
        # ReportBench dimensions included: 40/10/15/15/10/10
        weighted = (0.40 * dim_coverage + 0.10 * general_cov
                    + 0.20 * verification_ratio)
        if behavioral_ratio is not None:
            weighted += 0.15 * behavioral_ratio
            weighted += 0.10 * citation_rel + 0.10 * fact_faul
        else:
            # English mode without behavioral: normalize
            weighted = (weighted + 0.10 * citation_rel + 0.10 * fact_faul) / 0.70
    else:
        weighted = 0.5 * dim_coverage + 0.10 * general_cov + 0.20 * verification_ratio
        if behavioral_ratio is not None:
            weighted += 0.20 * behavioral_ratio
        else:
            weighted = weighted / 0.8 * 1.0

    return round(min(weighted * 100, 100), 2)


def print_report(dim_scores, general_cov, verification_ratio, behavioral_scores, behavioral_ratio, is_english=False, citation_rel=None, fact_faul=None):
    """Print analysis report."""
    total = compute_alignment_score(dim_scores, general_cov, verification_ratio, behavioral_ratio, citation_rel, fact_faul)

    print("=" * 60)
    if is_english:
        print("persona-v3 English Alignment Report")
    else:
        print("persona-v3 对齐度检测报告")
    print("=" * 60)

    print(f"\nOverall Alignment Score: {total}/100")

    print("\n--- Dimension Coverage ---")
    for dim, score in sorted(dim_scores.items(), key=lambda x: -x[1]):
        bar = chr(9608) * int(score * 20)
        print(f"  {dim:<28} {score:.2f} {bar}")

    # ReportBench dimensions
    if citation_rel is not None and fact_faul is not None:
        print("\n--- ReportBench Evaluation Dimensions ---")
        for dim, score in [("Citation Relevance", citation_rel), ("Factual Faithfulness", fact_faul)]:
            bar = chr(9608) * int(score * 20)
            print(f"  {dim:<28} {score:.2f} {bar}")

    print(f"\n--- General Information Theory Coverage ---")
    print(f"  Coverage: {general_cov:.2f}")

    print(f"\n--- Verification Patterns ---")
    print(f"  Score: {verification_ratio:.2f}")

    if behavioral_scores is not None:
        print(f"\n--- Behavioral Constraints ---")
        for cname, cscore in behavioral_scores.items():
            print(f"  {cname}: {cscore:.2f}")
        print(f"  Overall: {behavioral_ratio:.2f}")
    else:
        print("\n--- Behavioral Constraints ---")
        print("  Skipped (English academic writing, not applicable)")

    print("\n" + "=" * 60)
    return total


def detect_drift(baseline_scores, current_scores, threshold=0.1):
    """检测 persona drift: baseline vs current 的维度评分变化"""
    drifts = []
    for dim in baseline_scores:
        if dim in current_scores:
            delta = current_scores[dim] - baseline_scores[dim]
            if abs(delta) >= threshold:
                drifts.append({
                    "dimension": dim,
                    "baseline": round(baseline_scores[dim], 4),
                    "current": round(current_scores[dim], 4),
                    "delta": round(delta, 4),
                    "direction": "up" if delta > 0 else "down",
                    "severity": "HIGH" if abs(delta) >= 0.3 else "MEDIUM" if abs(delta) >= 0.15 else "LOW",
                })
    base_total = sum(baseline_scores.values()) / len(baseline_scores)
    curr_total = sum(current_scores.values()) / len(current_scores)
    return drifts, round(curr_total - base_total, 4), round(base_total, 4), round(curr_total, 4)


def main():
    parser = argparse.ArgumentParser(description="persona-v3 English Alignment Checker")
    parser.add_argument("file", nargs="?", help="Text file to analyze")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--show-sources", action="store_true", help="Show detection sources")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--baseline", help="Baseline file path (for drift detection)")
    args = parser.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8", errors="ignore")
    elif args.stdin:
        text = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    dim_scores = detect_dimensions(text)
    general_cov = detect_general_info_theory(text)
    verification_ratio = detect_verification_patterns(text)
    behavioral_scores, behavioral_ratio = detect_behavioral_constraints(text)
    citation_rel = detect_citation_relevance(text)
    fact_faul = detect_factual_faithfulness(text)

    if args.baseline:
        baseline_text = Path(args.baseline).read_text(encoding="utf-8", errors="ignore")
        baseline_scores = detect_dimensions(baseline_text)
        baseline_citation = detect_citation_relevance(baseline_text)
        baseline_fact = detect_factual_faithfulness(baseline_text)
        baseline_score = compute_alignment_score(
            baseline_scores,
            detect_general_info_theory(baseline_text),
            detect_verification_patterns(baseline_text),
            detect_behavioral_constraints(baseline_text)[1],
            baseline_citation,
            baseline_fact,
        )
        drifts, total_drift, base_total, curr_total = detect_drift(baseline_scores, dim_scores)

        if args.json:
            result = {
                "overall_score": compute_alignment_score(dim_scores, general_cov, verification_ratio, behavioral_ratio, citation_rel, fact_faul),
                "baseline_overall_score": baseline_score,
                "dimension_scores": dim_scores,
                "baseline_dimension_scores": baseline_scores,
                "general_info_theory": general_cov,
                "verification_patterns": verification_ratio,
                "behavioral_constraints": {"scores": behavioral_scores, "overall": behavioral_ratio},
                "citation_relevance": round(citation_rel, 4),
                "factual_faithfulness": round(fact_faul, 4),
                "baseline_citation_relevance": round(baseline_citation, 4),
                "baseline_factual_faithfulness": round(baseline_fact, 4),
                "drift_analysis": {
                    "total_drift": total_drift,
                    "base_total_avg": base_total,
                    "curr_total_avg": curr_total,
                    "drifts": drifts,
                    "drift_count": len(drifts),
                    "high_severity": sum(1 for d in drifts if d["severity"] == "HIGH"),
                },
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_report(dim_scores, general_cov, verification_ratio, behavioral_scores, behavioral_ratio, is_english=True, citation_rel=citation_rel, fact_faul=fact_faul)
            print(f"\n{'='*60}")
            print(f"Persona Drift Detection (baseline: {args.baseline})")
            print(f"{'='*60}")
            print(f"Baseline alignment: {baseline_score}")
            print(f"Current alignment: {result['overall_score']}")
            print(f"Total drift: {total_drift:+.4f} ({base_total:.4f} -> {curr_total:.4f})")
            if drifts:
                print(f"\nDrifted dimensions ({len(drifts)}):")
                for d in sorted(drifts, key=lambda x: -abs(x["delta"])):
                    flag = "RED" if d["severity"] == "HIGH" else "YELLOW" if d["severity"] == "MEDIUM" else "GREEN"
                    print(f"  [{flag}] {d['dimension']}: {d['baseline']:.2f} -> {d['current']:.2f} ({d['delta']:+.4f}) [{d['severity']}]")
            else:
                print("\nNo significant drift — all dimension changes < 0.10")
    else:
        if args.json:
            result = {
                "overall_score": compute_alignment_score(dim_scores, general_cov, verification_ratio, behavioral_ratio, citation_rel, fact_faul),
                "dimension_scores": dim_scores,
                "general_info_theory": general_cov,
                "verification_patterns": verification_ratio,
                "behavioral_constraints": {"scores": behavioral_scores, "overall": behavioral_ratio},
                "citation_relevance": round(citation_rel, 4),
                "factual_faithfulness": round(fact_faul, 4),
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_report(dim_scores, general_cov, verification_ratio, behavioral_scores, behavioral_ratio, is_english=True, citation_rel=citation_rel, fact_faul=fact_faul)

            if args.show_sources:
                print("\n--- Dimension Sources ---")
                for dim, keywords in DIMENSION_KEYWORDS.items():
                    matched = [kw for kw in keywords if kw.lower() in text.lower()]
                    if matched:
                        print(f"  {dim}: {matched[:5]}")
                print("\n--- ReportBench Sources ---")
                for dim_name, keywords in [("Citation Relevance", CITATION_RELEVANCE_KEYWORDS), ("Factual Faithfulness", FACTUAL_FAITHFULNESS_KEYWORDS)]:
                    matched = [kw for kw in keywords if kw.lower() in text.lower()]
                    if matched:
                        print(f"  {dim_name}: {matched[:5]}")


if __name__ == "__main__":
    main()
