# origin: ai
# R3 taskset: 10 curated AIME 2025 problems (AIME I+II 2025, source: HF dataset
# math-ai/aime25 fetched via hf-mirror.com, Apache-2.0; data file:
# tasks/aime25_test.jsonl, 30 problems, keys {problem, answer, id}).
# Ground truth = official AIME 2025 answers, spot-verified by brute force:
#   id 3  -> 117 (direct count)           id 16 -> 49 (n in {1,11,37})
#   id 0  -> 70  (17_b = b+7 | 9b+7 => b+7 | 56 => b in {21,49})
# Same interface as taskset.py: TASKS = list of dicts with
#   id / cat / diff / prompt / expected / check(text)->bool
# plus has_final re-exported for the scorer.

import json
import os

from taskset import has_final, _num  # reuse normalization helpers

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "aime25_test.jsonl"), encoding="utf-8") as fh:
    DATA = [json.loads(line) for line in fh if line.strip()]
_BYID = {int(d["id"]): d for d in DATA}  # jsonl ids are strings; normalize to int

# curated subset: (task_id, dataset_id, cat, diff)
# difficulty = my judgment (stratified: 1 easy / 5 medium / 4 hard)
CURATED = [
    ("A00", 0,  "number_theory", "medium"),   # base-b divisibility, parse trap
    ("A03", 3,  "number_theory", "easy"),     # integer pair count (brute-forceable)
    ("A04", 4,  "combinatorics", "medium"),   # 8-digit permutation count
    ("A09", 9,  "combinatorics", "hard"),     # 3x9 grid counting
    ("A11", 11, "geometry",      "hard"),     # 3D lattice, chained inequalities
    ("A16", 16, "number_theory", "medium"),   # divisibility sum
    ("A19", 19, "geometry",      "hard"),     # triangle, midpoints, circle area
    ("A23", 23, "trigonometry",  "medium"),   # sin(7*pi*sin(5x)) zero count
    ("A25", 25, "geometry",      "hard"),     # regular 24-gon segment count
    ("A27", 27, "sequences",     "medium"),   # rational sequence limit
]

def _mk(tid, did, cat, diff):
    d = _BYID[did]
    exp = int(d["answer"])
    prompt = d["problem"].strip() + "\nAnswer as a plain integer."
    return dict(id=tid, cat=cat, diff=diff, prompt=prompt, expected=str(exp),
                check=lambda s, e=exp: _num(s) == e)

TASKS = [_mk(*c) for c in CURATED]

if __name__ == "__main__":
    print("id    dataset_id  cat              diff     expected")
    print("-" * 60)
    for t in TASKS:
        did = CURATED[TASKS.index(t)][1]
        print(f"{t['id']}  {did:>4}         {t['cat']:<16} {t['diff']:<8} {t['expected']}")
    print("\nprompt sample (A00):")
    print(next(t for t in TASKS if t["id"] == "A00")["prompt"][:300])
    print("\nself-test (each expected passes its own check):")
    ok = True
    for t in TASKS:
        p = t["check"]("FINAL: " + t["expected"])
        ok = ok and p
        print(f"  {t['id']}: {'OK' if p else 'FAIL'}  expected={t['expected']}")
    # fallback: correct answer as last number, no FINAL line
    fb = {t["id"]: "computation gives " + t["expected"] for t in TASKS}
    print("fallback self-test (no FINAL, answer last):")
    for t in TASKS:
        p = t["check"](fb[t["id"]])
        ok = ok and p
        print(f"  {t['id']}: {'OK' if p else 'FAIL'}")
    print("\nALL SELF-TESTS PASS" if ok else "\nSOME SELF-TESTS FAILED")
