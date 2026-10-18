# origin: ai
# Benchmark task set for the thinking-token-budget experiment.
# Every task has an EXACT expected answer computed by Python (ground truth),
# so subagent answers can be scored automatically.
# Task family: AIME-style hard math + logic traps (the math/reasoning benchmark
# family Qwen-27B-class models are officially tested on; MMLU/GPQA/AIME).
# Emphasis: hard + error-prone (where a thinking budget actually matters).

import math
from fractions import Fraction
from itertools import combinations

def _divisors(n):
    return sum(1 for i in range(1, n+1) if n % i == 0)

def _gcd(a, b): return math.gcd(a, b)

# Each task: id, cat, diff, prompt, expected (string), check(subagent_final_str)
# check() normalizes and returns True/False.

TASKS = [
    # ---------------- EASY (should be solvable with ~0 thinking) -------------
    dict(id="T01", cat="arith", diff="easy",
         prompt="What is 15% of 240? Answer as a plain number.",
         expected="36",
         check=lambda s: _num(s) == 36),
    dict(id="T02", cat="number_theory", diff="easy",
         prompt="How many positive integer divisors does 360 have? Answer as a plain number.",
         expected=str(_divisors(360)),
         check=lambda s: _num(s) == _divisors(360)),
    dict(id="T03", cat="ratios", diff="easy",
         prompt="A train travels 300 km at a constant 75 km/h. How many hours does the trip take? Answer as a plain number.",
         expected="4",
         check=lambda s: _num(s) == 4),

    # ---------------- MEDIUM (needs a little reasoning) ---------------------
    dict(id="T04", cat="number_theory", diff="medium",
         prompt="How many integers from 1 to 1000 inclusive are divisible by 3 but NOT by 5? Answer as a plain number.",
         expected=str(sum(1 for i in range(1,1001) if i%3==0 and i%5!=0)),
         check=lambda s: _num(s) == sum(1 for i in range(1,1001) if i%3==0 and i%5!=0)),
    dict(id="T05", cat="combinatorics", diff="medium",
         prompt="A box has 5 red and 7 blue balls. How many ways are there to choose 3 balls such that at least one is red? Answer as a plain number.",
         expected=str(math.comb(12,3) - math.comb(7,3)),
         check=lambda s: _num(s) == math.comb(12,3) - math.comb(7,3)),
    dict(id="T06", cat="sequences", diff="medium",
         prompt="An arithmetic sequence starts 3, 7, 11, 15, ... . What is its 50th term? Answer as a plain number.",
         expected=str(3 + 49*4),
         check=lambda s: _num(s) == 3 + 49*4),
    dict(id="T07", cat="probability", diff="medium",
         prompt="A bag holds 3 red and 5 blue marbles. Two marbles are drawn without replacement. What is the probability both are red? Answer as a reduced fraction.",
         expected="3/28",
         check=lambda s: _frac(s) == Fraction(3,28)),

    # ---------------- HARD / ERROR-PRONE (thinking budget matters) ----------
    dict(id="T08", cat="number_theory", diff="hard",
         prompt="How many 4-digit positive integers are divisible by 11? Answer as a plain number.",
         expected=str(sum(1 for i in range(1000,10000) if i%11==0)),
         check=lambda s: _num(s) == sum(1 for i in range(1000,10000) if i%11==0)),
    dict(id="T09", cat="combinatorics", diff="hard",
         prompt="In how many ways can you place 3 non-attacking rooks on a 4x4 chessboard (no two share a row or a column)? Answer as a plain number.",
         expected=str(math.comb(4,3)*math.comb(4,3)*math.factorial(3)),
         check=lambda s: _num(s) == math.comb(4,3)*math.comb(4,3)*math.factorial(3)),
    dict(id="T10", cat="number_theory", diff="hard",
         prompt="What is the units digit (last digit) of 7 to the power 2026? Answer as a single digit.",
         expected=str(pow(7, 2026, 10)),
         check=lambda s: _digit(s) == pow(7,2026,10)),
    dict(id="T11", cat="combinatorics", diff="hard",
         prompt="In how many ways can 10 identical candies be distributed among 3 distinct children (a child may get zero)? Answer as a plain number.",
         expected=str(math.comb(10+3-1, 3-1)),
         check=lambda s: _num(s) == math.comb(10+3-1, 3-1)),
    dict(id="T12", cat="logic_trap", diff="hard",
         prompt="The sum of three consecutive odd integers is 111. What is the largest of the three? Answer as a plain number.",
         expected="39",
         check=lambda s: _num(s) == 39),
]

# ---------- normalization helpers ----------
def has_final(s):
    """True if the output contains a 'FINAL:' LINE (line-anchored, so a quoted
    mention like 'ended with "FINAL: 96"' in mid-line does NOT count)."""
    import re
    return bool(re.search(r"^\s*FINAL\s*[:：]", str(s or ""), re.M))

def _clean(s):
    if s is None: return ""
    s = str(s).strip()
    # pull the FINAL: <answer> if present (last occurrence, ANYWHERE in text —
    # matches a realistic deployment regex; the strict own-line requirement is
    # the separate fmt column via has_final, so a mid-line "…= 66. FINAL: 66"
    # still yields the right answer for accuracy while fmt flags the risk)
    import re
    m = list(re.finditer(r"FINAL\s*[:：]\s*(.+)$", s, re.M))
    if m:
        s = m[-1].group(1).strip()
    else:
        # no FINAL line: fall back to the LAST number in the text (answers are
        # usually stated last); avoids grabbing a leading number like "15%"
        nums = re.findall(r"-?\d+\.?\d*", s)   # no capture group (findall would return groups)
        if nums:
            s = nums[-1]
    # strip trailing punctuation / words like 'the answer is'
    s = s.rstrip(".").strip()
    return s.strip()

def _num(s):
    s = _clean(s).replace(",", "").replace(" ", "")
    import re
    m = re.search(r"-?\d+(\.\d+)?", s)
    if not m: return None
    v = float(m.group(0))
    return int(v) if v == int(v) else v

def _frac(s):
    # Fraction answer. If a FINAL: line exists, search it; otherwise search the
    # WHOLE text for the LAST fraction (avoids _clean's last-number fallback,
    # which would reduce "3/28" to "28").
    if s is None: return None
    import re
    s = str(s).replace(" ", "")
    m = list(re.finditer(r"FINAL\s*[:：]\s*(.+)$", s, re.M))
    seg = m[-1].group(1) if m else s
    fm = list(re.finditer(r"(\d+)/(\d+)", seg))
    if fm:
        last = fm[-1]
        return Fraction(int(last.group(1)), int(last.group(2)))
    n = _num(s)
    return Fraction(n) if isinstance(n, int) else None

def _digit(s):
    n = _num(s)
    return int(str(n)[-1]) if n is not None else None

# ---------- ground-truth table ----------
if __name__ == "__main__":
    print("id    cat              diff     expected")
    print("-"*52)
    for t in TASKS:
        print(f"{t['id']}  {t['cat']:<16} {t['diff']:<8} {t['expected']}")
    # self-test: make sure each task's own check accepts its expected string
    print("\nself-test (each expected should pass its own check):")
    ok = True
    for t in TASKS:
        passed = t["check"]("FINAL: " + t["expected"])
        if not passed:
            ok = False
        print(f"  {t['id']}: {'OK' if passed else 'FAIL'}  expected={t['expected']}")
    # fallback self-test: correct answer stated last WITHOUT a FINAL line
    print("\nfallback self-test (no FINAL line, answer as last number):")
    fb_cases = {"T01": "15% of 240 = 36", "T09": "Answer: 96. check -> 96",
                "T11": "stars-and-bars: C(12,2) = 66. FINAL: 66"}
    for tid, s in fb_cases.items():
        t = next(x for x in TASKS if x["id"] == tid)
        passed = t["check"](s)
        ok = ok and passed
        print(f"  {tid}: {'OK' if passed else 'FAIL'}  sample='{s}'")
    # has_final: strict own-line check (fmt column) — a mid-line FINAL is a
    # format risk and must NOT count as compliant, even though acc still parses it
    mid = "stars-and-bars: C(12,2) = 66. FINAL: 66"
    own = "blah\nFINAL: 42"
    ok = ok and (has_final(own) is True)
    ok = ok and (has_final(mid) is False)
    print(f"  has_final own-line/mid-line: {'OK' if has_final(own) and not has_final(mid) else 'FAIL'}")

    print("\nALL SELF-TESTS PASS" if ok else "\nSOME SELF-TESTS FAILED")
