#!/usr/bin/env python3
# 04-r14: single-command gate for the whole stage-04 verification thread.
# Runs each self-test as a SUBPROCESS (so their __main__ exit codes are honored), collects results,
# exits 1 if ANY suite fails. This is the regression net behind every H* claim in this project.
# Run: python3 tasks/run_all.py   (exit 0 = whole thread green)
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
SUITES = ["roofline_verify.py", "test_hstar_rule.py", "resolve_hstar.py"]   # each independently runnable + exit-code-correct
# argv override: `python3 tasks/run_all.py <suite.py> ...` runs ONLY those (used to inject a failing canary
# and prove the gate actually goes RED -> exit 1; default (no args) = the two real suites).
if len(sys.argv) > 1:
    SUITES = sys.argv[1:]

def run(script):
    path = os.path.join(HERE, script)
    p = subprocess.run([sys.executable, path], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

print("== STAGE-04 VERIFICATION GATE (一手✓; one command, all suites) ==")
failed = []
for s in SUITES:
    rc, out, err = run(s)
    ok = rc == 0
    print(f"  [{'PASS' if ok else 'FAIL'}] {s}  (exit={rc})")
    if not ok:
        failed.append(s)
        tail = (out.splitlines() + err.splitlines())[-6:]
        print("    ---- last lines ----")
        for ln in tail: print("    " + ln)

print("  RESULT:", "ALL SUITES GREEN ✓" if not failed else ("RED -> failing: " + ", ".join(failed)))
sys.exit(1 if failed else 0)