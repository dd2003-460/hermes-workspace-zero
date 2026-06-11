#!/usr/bin/env python3
"""
persona-v3 全局对齐度仪表盘

扫描 memory/ 下所有 idea 分析文件，运行 alignment_checker 并生成
全局报告：按对齐度排名、维度覆盖率统计、漂移检测（可选基线）。

用法:
    python3 persona_v3_dashboard.py                  # 运行全部扫描 + 文本报告
    python3 persona_v3_dashboard.py --json           # JSON 输出
    python3 persona_v3_dashboard.py --baseline <file> # 漂移检测
    python3 persona_v3_dashboard.py --html output.html # 生成 HTML 报告
    python3 persona_v3_dashboard.py --top 5           # 只查看 top/bottom 5
    python3 persona_v3_dashboard.py --file memory/idea-01-*.md  # 指定文件
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Inline dimension keywords (same as alignment_checker) to avoid subprocess calls.
# Memory-efficient: no fork, no subprocess overhead.

DIMENSION_KEYWORDS = {
    "自适应精度": [
        ("rate-distortion", 2.0), ("R(D)", 2.0), ("压缩", 0.5), ("精度", 0.5), ("粒度", 0.5), ("比特率", 0.5),
        ("信噪比", 0.5), ("SNR", 0.5), ("信息密度", 1.0), ("perceptual accuracy", 0.5),
        ("analysis fidelity", 0.5), ("token precision", 1.0), ("adaptive precision", 2.0),
        ("precision level", 0.5), ("precision allocation", 0.5), ("有损压缩", 1.0), ("失真", 0.5),
        ("信息预算", 0.5), ("fine-grained", 0.5), ("粗粒度", 0.5), ("coarse", 0.5),
    ],
    "自适应探索": [
        ("探索", 1.0), ("利用", 1.0), ("exploration-exploitation", 2.0), ("探索频率", 1.0),
        ("探索策略", 1.0), ("工具选择", 1.5), ("新工具", 0.5), ("复用", 1.0), ("已有工具", 0.5),
        ("磨刀", 1.5), ("search for", 0.5), ("look for", 0.5), ("替代方案", 0.5),
        ("次优", 0.5), ("optimal", 0.5), ("explore", 0.5), ("exploit", 0.5),
    ],
    "自适应感知": [
        ("感知", 1.0), ("perceptual", 0.5), ("感官", 0.5), ("信息密度", 1.0), ("信号", 0.5),
        ("噪声", 0.5), ("信噪比", 0.5), ("SNR", 0.5), ("信号质量", 0.5), ("感知时间", 1.5),
        ("t_p", 1.5), ("感知速率", 1.5), ("R_max", 1.5), ("感知资源", 0.5), ("感知级别", 0.5),
        ("粗感知", 0.5), ("细感知", 0.5), ("感知粒度", 0.5), ("观测者效应", 0.5),
        ("测量误差", 0.5), ("perceptual error", 0.5), ("保真度", 0.5), ("high-fidelity", 0.5),
        ("low-fidelity", 0.5),
    ],
    "自适应先验": [
        ("先验", 1.0), ("后验", 1.0), ("先验分布", 1.5), ("初始信念", 1.5), ("贝叶斯", 1.5), ("Bayes", 1.5),
        ("p(h|e)", 1.5), ("p(e|h)", 1.5), ("似然", 1.0), ("预训练", 0.5), ("pretraining", 0.5),
        ("pre-trained", 0.5), ("进化", 0.5), ("evolutionary", 0.5), ("bio", 0.5),
        ("认知结构", 1.0), ("认知路径", 0.5), ("初始设定", 0.5), ("priors", 0.5), ("p(h)", 0.5),
        ("p(e)", 0.5), ("prior belief", 1.0), ("belief update", 1.0), ("theta_bio", 1.0),
        ("evolutionary prior", 0.5),
    ],
    "自适应自我": [
        ("观测者", 1.0), ("observer", 1.0), ("observer-dependent", 2.0), ("observer-dependence", 2.0),
        ("第一人称", 1.0), ("third-person", 1.0), ("主观", 0.5), ("客观", 0.5), ("perspective", 0.5),
        ("视角", 0.5), ("point of view", 0.5), ("vantage point", 0.5), ("自我中心", 0.5),
        ("self-centered", 0.5), ("self-referential", 0.5), ("self-model", 0.5),
        ("y(theta)", 1.0), ("y(θ)", 1.5), ("观测者-环境", 2.0),
        ("不同观测者", 1.5), ("observing position", 0.5), ("positional", 0.5),
    ],
    "自适应投影": [
        ("投影", 1.0), ("低维", 2.0), ("dimensional reduction", 1.0), ("跨域", 2.0),
        ("类比", 0.5), ("analogy", 0.5), ("同构", 1.5), ("isomorphic", 1.5), ("isomorphism", 1.5),
        ("映射", 1.0), ("映射到", 0.5), ("map to", 0.5), ("maps to", 0.5), ("analogous to", 0.5),
        ("信息瓶颈", 1.0), ("mutual information", 1.0), ("I(X;Y)", 1.5),
        ("KL 散度", 1.0), ("KL divergence", 1.0), ("D_KL", 1.0), ("交叉熵", 0.5),
        ("不变量", 1.0), ("invariant", 1.0), ("拓扑", 0.5), ("topological", 0.5),
        ("相似结构", 0.5), ("same underlying structure", 0.5),
        ("不同领域", 0.5), ("unrelated domains", 0.5),
    ],
}

GENERAL_INFO_THEORY = [
    "信息论", "entropy", "互信息", "shannon", "信息流", "channel",
    "编码", "解码", "compression", "信息密度", "maxent",
    "maximum entropy", "rate-distortion", "信息增益", "bayesian",
    "bayes", "后验", "先验", "likelihood", "inference",
]

VERIFICATION_PATTERNS = [
    r"why.*not.*but",
    r"why.*is.*not.*",
    r"question.*boundary",
    r"边界.*条件",
    r"边界意识",
    r"局限",
    r"限制",
    r"scope.*limit",
    r"assumption.*hold",
    r"plausibly.*exogenous",
    r"等价",
    r"isomorphic",
    r"类比",
    r"map.*onto",
    r"映射",
    r"thus.*",
    r"因此",
    r"consequently.*",
    r"对应",
    r"不是.*而是",
    r"既不.*也不",
    r"切换",
    r"优化",
    r"maximiz",
    r"约束",
    r"trade-off",
    r"精度",
    r"sufficien",
    r"在什么条件下不成立",  # 边界条件追问 (persona-v3 输出要求 #4)
    r"当.*时.*不.*",       # 场景约束 (timeline consistency)
    r"迭代追问",            # iterative questioning
    r"Gap\s*[:：]",        # gap detection
    r"Q\d+:",              # follow-up question
    r"A\d+:",              # self-answer
    r"置信度",             # confidence labeling
]

BEHAVIORAL_CONSTRAINTS = {
    "简洁直接": {
        "positive": [
            "结论", "关键发现", "核心", "直接", "明确", "清晰",
        ],
        "negative": [
            "总之", "总结", "overall", "generally", "值得注意的是",
            "在...的语境下", "it should be noted",
        ],
    },
    "不解释": {
        "positive": [
            "方程", "模型", "假设", "方法",
            "我们证明", "我们展示", "我们提出",
        ],
        "negative": [
            "这意味着", "换句话说", "也就是说",
            "让我解释", "正如读者所知",
        ],
    },
    "推进而非停滞": {
        "positive": [
            "下一步", "未来工作", "未解问题", "仍然",
        ],
        "negative": [
            "等待", "pending", "upon your feedback",
        ],
    },
}

# ReportBench dimensions: Citation Relevance & Factual Faithfulness
CITATION_RELEVANCE_KEYWORDS = [
    ("引用相关", 2.0), ("citation relevance", 2.0), ("文献支撑", 2.0),
    ("引用", 1.0), ("参考文献", 1.0), ("source", 1.0), ("证据", 1.0),
    ("data support", 1.0), ("empirical support", 1.0), ("佐证", 0.5),
    ("according to", 0.5), ("研究表明", 0.5), ("实证", 0.5),
    ("meta-analysis", 0.5), ("systematic review", 0.5), ("研究证实", 0.5),
    ("文献综述", 0.5), ("来源", 0.5), ("文献", 0.5), ("论据", 0.5),
]

FACTUAL_FAITHFULNESS_KEYWORDS = [
    ("事实验证", 2.0), ("factual faithfulness", 2.0), ("可验证", 2.0), ("可证伪", 2.0),
    ("external source", 1.0), ("外部来源", 1.0), ("可交叉验证", 1.0),
    ("third-party", 1.0), ("独立来源", 1.0), ("empirical claim", 1.0),
    ("可重复", 1.0), ("replicable", 1.0), ("数据来源", 1.0),
    ("statistically", 0.5), ("数据支持", 0.5), ("量化", 0.5),
    ("信度", 0.5), ("效度", 0.5), ("测量", 0.5), ("指标", 0.5),
]


def detect_dimensions(text):
    """检测维度覆盖率，返回每个维度的分数 (0-1)。加权关键词匹配。"""
    text_lower = text.lower()
    scores = {}
    for dim_name, kw_list in DIMENSION_KEYWORDS.items():
        total_weight = 0.0
        matched_weight = 0.0
        for kw, weight in kw_list:
            if re.search(re.escape(kw.lower()), text_lower):
                matched_weight += weight
            total_weight += weight
        scores[dim_name] = round(matched_weight / total_weight if total_weight > 0 else 0, 4)
    return scores


def detect_general_info_theory(text):
    """检测通用信息论关键词覆盖率。"""
    text_lower = text.lower()
    matched = sum(1 for kw in GENERAL_INFO_THEORY if kw.lower() in text_lower)
    return round(matched / len(GENERAL_INFO_THEORY), 4)


def detect_verification_patterns(text):
    """检测验证模式覆盖率。"""
    matched = sum(1 for p in VERIFICATION_PATTERNS if re.search(p, text, re.IGNORECASE))
    return round(matched / len(VERIFICATION_PATTERNS), 4)


def detect_behavioral_constraints(text):
    """检测行为约束合规性。"""
    scores = {}
    for cname, info in BEHAVIORAL_CONSTRAINTS.items():
        pos = sum(1 for p in info["positive"] if re.search(p, text))
        neg = sum(1 for p in info["negative"] if re.search(p, text))
        total_pos = len(info["positive"])
        total_neg = len(info["negative"])
        score = max(0, pos / total_pos - neg / total_neg)
        scores[cname] = round(min(score, 1.0), 4)

    overall = sum(scores.values()) / len(scores) if scores else 0
    return scores, round(overall, 4)


def detect_citation_relevance(text):
    """检测引用相关性分数 (ReportBench 维度)。"""
    text_lower = text.lower()
    total_weight = 0.0
    matched_weight = 0.0
    for kw, weight in CITATION_RELEVANCE_KEYWORDS:
        if kw.lower() in text_lower:
            matched_weight += weight
        total_weight += weight
    return round(min(matched_weight / total_weight, 1.0), 4) if total_weight > 0 else 0


def detect_factual_faithfulness(text):
    """检测事实可信度分数 (ReportBench 维度)。"""
    text_lower = text.lower()
    total_weight = 0.0
    matched_weight = 0.0
    for kw, weight in FACTUAL_FAITHFULNESS_KEYWORDS:
        if kw.lower() in text_lower:
            matched_weight += weight
        total_weight += weight
    return round(min(matched_weight / total_weight, 1.0), 4) if total_weight > 0 else 0


def compute_alignment_score(dim_scores, general_cov, verification_ratio, behavioral_ratio, citation_rel=None, fact_faul=None):
    """计算总体对齐度分数 (0-100)。"""
    dim_coverage = sum(dim_scores.values()) / len(dim_scores) if dim_scores else 0

    if citation_rel is not None and fact_faul is not None:
        weighted = (0.40 * dim_coverage + 0.10 * general_cov
                    + 0.20 * verification_ratio + 0.20 * behavioral_ratio
                    + 0.10 * citation_rel + 0.10 * fact_faul)
    else:
        weighted = 0.5 * dim_coverage + 0.10 * general_cov + 0.20 * verification_ratio + 0.20 * behavioral_ratio
    return round(min(weighted * 100, 100), 2)


def compute_drift(baseline_scores, current_scores, threshold=0.1):
    """检测 persona drift: baseline vs current 的维度评分变化。"""
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


def scan_file(file_path, baseline_scores=None):
    """扫描单个文件并返回分析结果。"""
    text = Path(file_path).read_text(encoding="utf-8", errors="ignore")

    dim_scores = detect_dimensions(text)
    general_cov = detect_general_info_theory(text)
    verification_ratio = detect_verification_patterns(text)
    behavioral_scores, behavioral_ratio = detect_behavioral_constraints(text)
    citation_rel = detect_citation_relevance(text)
    fact_faul = detect_factual_faithfulness(text)
    score = compute_alignment_score(dim_scores, general_cov, verification_ratio, behavioral_ratio, citation_rel, fact_faul)

    # Missing dimensions (score < 0.3)
    missing = [d for d, s in dim_scores.items() if s < 0.3]

    result = {
        "file": str(file_path),
        "filename": file_path.name,
        "score": score,
        "dimension_scores": dim_scores,
        "general_info_theory": general_cov,
        "verification_ratio": verification_ratio,
        "behavioral_scores": behavioral_scores,
        "behavioral_overall": behavioral_ratio,
        "citation_relevance": round(citation_rel, 4),
        "factual_faithfulness": round(fact_faul, 4),
        "missing_dimensions": missing,
        "missing_count": len(missing),
    }

    if baseline_scores:
        drifts, total_drift, base_avg, curr_avg = compute_drift(baseline_scores, dim_scores)
        result["drift_analysis"] = {
            "total_drift": total_drift,
            "base_total_avg": base_avg,
            "curr_total_avg": curr_avg,
            "drifts": drifts,
            "drift_count": len(drifts),
            "high_severity": sum(1 for d in drifts if d["severity"] == "HIGH"),
        }

    return result


def find_idea_files(root, pattern=None):
    """查找 memory/ 下的所有 idea 分析文件。"""
    memory_dir = root / "memory"
    if not memory_dir.exists():
        return []

    seen = set()
    files = []

    if pattern:
        p = Path(pattern)
        if p.is_absolute() or '..' in pattern:
            # Python 3.14+ pathlib.glob doesn't support non-relative patterns
            files = [f for f in [p] if f.exists() and f.is_file() and memory_dir in f.resolve().parents]
        else:
            files = list(memory_dir.glob(pattern))
    else:
        # Primary: standard-named idea files
        for f in memory_dir.glob("idea-*.md"):
            if f.is_file() and str(f) not in seen:
                seen.add(str(f))
                files.append(f)
        # Secondary: files with Chinese chars that still contain "idea"
        for f in memory_dir.iterdir():
            if f.is_file() and f.name.endswith(".md") and "idea" in f.name.lower() and str(f) not in seen and not f.name.startswith("iteration-"):
                seen.add(str(f))
                files.append(f)

    return sorted(files)


def print_text_report(results, top_n=10):
    """打印文本格式的全局报告。"""
    if not results:
        print("No files scanned.")
        return

    results.sort(key=lambda x: x["score"])
    ranked = results

    print("=" * 72)
    print("  persona-v3 Global Alignment Dashboard")
    print("  " + "-" * 60)
    print(f"  Files scanned: {len(ranked)}")
    scores = [r["score"] for r in ranked]
    print(f"  Score range: {min(scores):.1f} - {max(scores):.1f}")
    print(f"  Average score: {sum(scores)/len(scores):.1f}")
    print("=" * 72)

    # Dimension distribution
    print("\n--- Dimension Coverage (avg across all files) ---")
    dim_totals = {d: 0 for d in DIMENSION_KEYWORDS}
    for r in ranked:
        for d, s in r["dimension_scores"].items():
            dim_totals[d] += s
    for d, total in sorted(dim_totals.items(), key=lambda x: -x[1]):
        avg = total / len(ranked)
        bar = chr(9608) * int(avg * 20)
        print(f"  {d:<16} avg={avg:.2f} {bar}")

    # ReportBench dimension distribution
    if "citation_relevance" in ranked[0]:
        total_cr = sum(r["citation_relevance"] for r in ranked)
        total_ff = sum(r["factual_faithfulness"] for r in ranked)
        avg_cr = total_cr / len(ranked)
        avg_ff = total_ff / len(ranked)
        print(f"\n--- ReportBench Dimensions ---")
        print(f"  {'Citation Relevance':<16} avg={avg_cr:.2f} {chr(9608) * int(avg_cr * 20)}")
        print(f"  {'Factual Faithfulness':<16} avg={avg_ff:.2f} {chr(9608) * int(avg_ff * 20)}")

    # Top N best
    print(f"\n--- Top {top_n} Best Aligned ---")
    for i, r in enumerate(reversed(ranked[-top_n:])):
        print(f"  #{i+1} [{r['score']:.1f}] {r['filename'][:50]}")
        if r["missing_dimensions"]:
            print(f"       Missing: {', '.join(r['missing_dimensions'])}")

    # Bottom N worst
    print(f"\n--- Bottom {top_n} ---")
    for i, r in enumerate(ranked[:top_n]):
        print(f"  #{i+1} [{r['score']:.1f}] {r['filename'][:50]}")
        print(f"       Missing: {', '.join(r['missing_dimensions'])}")

    # Drift summary if available
    for r in ranked:
        if "drift_analysis" in r:
            da = r["drift_analysis"]
            if da["total_drift"] < 0 and da["high_severity"] > 0:
                print(f"\n  HIGH drift in {r['filename']}: drift={da['total_drift']:+.4f}")
                for d in da["drifts"]:
                    if d["severity"] == "HIGH":
                        print(f"    [{d['severity']}] {d['dimension']}: {d['baseline']:.2f} -> {d['current']:.2f} ({d['delta']:+.4f})")


def generate_html_report(results, output_path):
    """生成 HTML 格式的仪表盘报告。"""
    if not results:
        print("No files to report.")
        return

    results.sort(key=lambda x: x["score"])

    rows_html = ""
    for r in results:
        dim_row = ""
        for d, s in r["dimension_scores"].items():
            color = "#4caf50" if s >= 0.5 else "#ff9800" if s >= 0.3 else "#f44336"
            dim_row += f'<td style="color:{color};text-align:center;font-weight:{"bold" if s >= 0.5 else "normal"}">{s:.2f}</td>'
        missing_str = ", ".join(r["missing_dimensions"]) if r["missing_dimensions"] else "<span style='color:#4caf50'>All present</span>"
        rows_html += f"""
        <tr>
            <td>{r["filename"][:60]}</td>
            <td style="text-align:center;font-weight:bold;font-size:1.1em">{r["score"]:.1f}</td>
            {dim_row}
            <td style="text-align:center">{r["general_info_theory"]:.2f}</td>
            <td style="text-align:center">{r["verification_ratio"]:.2f}</td>
            <td style="text-align:center">{r["behavioral_overall"]:.2f}</td>
            <td>{missing_str}</td>
        </tr>"""

    # Stats
    scores = [r["score"] for r in results]
    avg_score = sum(scores) / len(scores)
    best = max(scores)
    worst = min(scores)
    high_drift_files = sum(1 for r in results if "drift_analysis" in r and r["drift_analysis"]["high_severity"] > 0)

    # Drift details
    drift_html = ""
    for r in results:
        if "drift_analysis" in r:
            da = r["drift_analysis"]
            if da["total_drift"] != 0:
                drift_html += f'<div style="margin:2px 0;padding:4px;background:#f5f5f5;border-radius:3px;font-size:0.85em">'
                drift_html += f'<b>{r["filename"][:50]}</b>: drift={da["total_drift"]:+.4f} '
                if da["drifts"]:
                    drift_html += "| " + " ".join(f'[{d["severity"]}] {d["dimension"]}: {d["baseline"]:.2f}->{d["current"]:.2f}' for d in da["drifts"][:3])
                drift_html += '</div>'

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>persona-v3 Alignment Dashboard</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 20px; background: #fafafa; }}
  h1 {{ color: #333; }}
  table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  th {{ background: #4a5568; color: white; padding: 8px 12px; text-align: left; font-size: 0.85em; }}
  td {{ padding: 6px 12px; border-bottom: 1px solid #e2e8f0; font-size: 0.85em; }}
  tr:hover {{ background: #f7fafc; }}
  .stats {{ display: flex; gap: 20px; margin: 16px 0; }}
  .stat {{ background: white; padding: 12px 20px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .stat-label {{ font-size: 0.8em; color: #718096; }}
  .stat-value {{ font-size: 1.5em; font-weight: bold; color: #2d3748; }}
  .drift-section {{ background: white; padding: 12px; border-radius: 6px; margin: 12px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .legend {{ font-size: 0.8em; color: #718096; margin: 8px 0; }}
</style>
</head>
<body>
<h1>persona-v3 Alignment Dashboard</h1>
<div class="stats">
  <div class="stat"><div class="stat-label">Files</div><div class="stat-value">{len(results)}</div></div>
  <div class="stat"><div class="stat-label">Avg Score</div><div class="stat-value">{avg_score:.1f}</div></div>
  <div class="stat"><div class="stat-label">Best</div><div class="stat-value" style="color:#4caf50">{best:.1f}</div></div>
  <div class="stat"><div class="stat-label">Worst</div><div class="stat-value" style="color:#f44336">{worst:.1f}</div></div>
  <div class="stat"><div class="stat-label">High Drift</div><div class="stat-value" style="color:#ff5722">{high_drift_files}</div></div>
</div>
<div class="legend">Score legend: Green &ge;0.5 = good | Orange 0.3-0.5 = partial | Red &lt;0.3 = poor</div>
<table>
<thead><tr>
    <th>File</th>
    <th style="text-align:center">Score</th>
    <th style="text-align:center">精度</th>
    <th style="text-align:center">探索</th>
    <th style="text-align:center">感知</th>
    <th style="text-align:center">先验</th>
    <th style="text-align:center">自我</th>
    <th style="text-align:center">投影</th>
    <th style="text-align:center">信息论</th>
    <th style="text-align:center">验证</th>
    <th style="text-align:center">行为</th>
    <th>Missing</th>
</tr></thead>
<tbody>
{rows_html}
</tbody>
</table>
{f'<div class="drift-section"><h3>Drift Summary</h3>{drift_html}</div>' if drift_html else ''}
</body>
</html>"""

    Path(output_path).write_text(html, encoding="utf-8")
    print(f"HTML report written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="persona-v3 Global Alignment Dashboard")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--html", help="Generate HTML report to file")
    parser.add_argument("--top", type=int, default=0, help="Limit JSON output to top/bottom N (default: all)")
    parser.add_argument("--baseline", help="Baseline file path for drift detection")
    parser.add_argument("file", nargs="?", help="Single file or pattern (default: all idea-*.md in memory/)")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    baseline_scores = None

    if args.baseline:
        baseline_text = Path(args.baseline).read_text(encoding="utf-8", errors="ignore")
        baseline_scores = detect_dimensions(baseline_text)

    files = find_idea_files(root, pattern=args.file)
    if not files:
        print(f"No files found matching: {args.file or 'memory/idea-*.md'}")
        sys.exit(1)

    print(f"Scanning {len(files)} files...", file=sys.stderr)

    results = []
    for i, f in enumerate(files):
        r = scan_file(f, baseline_scores=baseline_scores)
        results.append(r)
        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{len(files)} done", file=sys.stderr)

    if args.json:
        if args.top > 0:
            # Sort ascending (worst first), return worst N + best N
            results.sort(key=lambda x: x["score"])
            n = args.top
            worst = results[:n]
            best = results[-n:] if len(results) > n else results
            # Deduplicate: best files already in worst set won't repeat
            seen = {r["file"] for r in worst}
            extra = [r for r in best if r["file"] not in seen]
            results = worst + extra
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.html:
        generate_html_report(results, args.html)
    else:
        print_text_report(results, top_n=args.top)


if __name__ == "__main__":
    main()
