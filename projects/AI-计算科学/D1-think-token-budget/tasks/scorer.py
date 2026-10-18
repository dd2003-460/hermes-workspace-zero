# origin: ai
# Scorer: reads raw subagent outputs (<cond>__<taskid>.txt) from a raw dir,
# measures surfaced-output length (chars; ~tokens/4 as a rough proxy) and
# scores correctness against taskset ground truth. Prints a table + CSV.
# 'fmt' = whether the run emitted a 'FINAL:' line (format compliance).
# Usage: python3 scorer.py <raw_dir> [csv_out]
import os, sys, glob, csv
sys.path.insert(0, os.path.dirname(__file__))
from taskset import TASKS, has_final

BYID = {t["id"]: t for t in TASKS}

def main(raw_dir, csv_out):
    rows = []
    files = sorted(glob.glob(os.path.join(raw_dir, "*.txt")))
    for f in files:
        name = os.path.basename(f)[:-4]
        if "__" not in name:
            continue
        cond, tid = name.split("__", 1)
        if tid not in BYID:
            continue
        text = open(f, encoding="utf-8").read()
        task = BYID[tid]
        chars = len(text)
        toks_est = round(chars / 4)   # rough; CJK-heavy would differ
        ok = bool(task["check"](text))
        fmt = bool(has_final(text))
        rows.append(dict(cond=cond, task=tid, cat=task["cat"], diff=task["diff"],
                         correct=ok, fmt=fmt, chars=chars, toks_est=toks_est))

    rows.sort(key=lambda r: (r["cond"], r["task"]))

    # per-condition aggregate
    agg = {}
    for r in rows:
        a = agg.setdefault(r["cond"], dict(n=0, ok=0, fmt=0, chars=0))
        a["n"] += 1; a["ok"] += int(r["correct"]); a["fmt"] += int(r["fmt"])
        a["chars"] += r["chars"]

    print(f"{'cond':<6} {'task':<5} {'cat':<16} {'diff':<8} {'ok':<4} {'fmt':<4} {'chars':>6} {'~tok':>5}")
    print("-" * 64)
    for r in rows:
        print(f"{r['cond']:<6} {r['task']:<5} {r['cat']:<16} {r['diff']:<8} "
              f"{'Y' if r['correct'] else 'N':<4} {'Y' if r['fmt'] else 'N':<4} "
              f"{r['chars']:>6} {r['toks_est']:>5}")
    print("-" * 64)
    print("\nPER-CONDITION AGGREGATE (mean chars = surfaced-output proxy):")
    print(f"{'cond':<6} {'n':>3} {'acc':>7} {'fmt%':>6} {'mean_chars':>11} {'mean_toks':>10}")
    for c, a in sorted(agg.items()):
        acc = a["ok"]/a["n"]*100 if a["n"] else 0
        fpc = a["fmt"]/a["n"]*100 if a["n"] else 0
        mc = a["chars"]/a["n"]
        print(f"{c:<6} {a['n']:>3} {acc:>6.0f}% {fpc:>5.0f}% {mc:>11.1f} {round(mc/4):>10}")

    if csv_out:
        with open(csv_out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        print(f"\nWrote {csv_out}")

if __name__ == "__main__":
    raw = sys.argv[1] if len(sys.argv) > 1 else "results/round1/raw"
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(raw), "scores.csv")
    main(raw, out)
