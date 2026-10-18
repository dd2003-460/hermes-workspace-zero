# origin: ai
# Generate the exact subagent prompt text for every (condition x task) pair in R2.
# Writes prompts/generated/<COND>__<TASK>.prompt.txt and prints a manifest.
# Conditions: P0 (append), P1 (append), P3v2 (full prompt wrapping TASK).
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from taskset import TASKS

OUT = os.path.join(os.path.dirname(__file__), "..", "prompts", "generated")
os.makedirs(OUT, exist_ok=True)

P0 = "\n\nShow your reasoning step by step, then give the final answer.\nEnd with a line exactly: FINAL: <answer>"
P1 = "\nAnswer only. No reasoning, no working, no explanation.\nEnd with a line exactly: FINAL: <answer>"

P3V2_TMPL = (
"Output EXACTLY these parts in order, nothing else:\n"
"  1) ONE line: LEVEL: easy|medium|hard\n"
"     (easy = 1 step/trivial; medium = 2-3 steps; hard = 4+ steps or easy-to-get-wrong)\n"
"  2) reasoning sized EXACTLY to the level:\n"
"     easy -> NONE (omit this part entirely)\n"
"     medium -> at most 1 short line\n"
"     hard -> concise full reasoning, each step written ONCE, no re-deriving, no cross-check\n"
"  3) ONE line: FINAL: <answer>\n"
"STRICT RULES:\n"
"- Your LAST line MUST be exactly 'FINAL: <answer>'. Never omit, reorder, or reformat it.\n"
"- No first person ('I'), no mentioning a role/subagent/parent/oracle, no 'this task', "
"no 'I will do X', no restating the task, no commentary or apologies.\n"
"- If easy, the whole output is exactly two lines: the LEVEL line and the FINAL line.\n"
"TASK: {task}"
)

def prompt_for(cond, task):
    t = task["prompt"]
    if cond == "P0":
        return t + P0
    if cond == "P1":
        return t + P1
    if cond == "P3v2":
        return P3V2_TMPL.format(task=t)
    raise ValueError(cond)

CONDS = ["P0", "P1", "P3v2"]
manifest = []
for cond in CONDS:
    for t in TASKS:
        name = f"{cond}__{t['id']}.prompt.txt"
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(prompt_for(cond, t))
        manifest.append((cond, t["id"], t["diff"], t["cat"], name))

print(f"Wrote {len(manifest)} prompts to {os.path.abspath(OUT)}")
print(f"{'cond':<6} {'task':<5} {'diff':<8} {'cat':<16} file")
for c, tid, d, cat, name in manifest:
    print(f"{c:<6} {tid:<5} {d:<8} {cat:<16} {name}")
