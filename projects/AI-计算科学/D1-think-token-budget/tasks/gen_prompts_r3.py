# origin: ai
# R3 prompt generator: materializes the 30 condition prompts
# (P0/P1/P5 x 10 curated AIME 2025 tasks) into
# prompts/r3_generated/<COND>__<TID>.prompt.txt + manifest.json.
# P0/P1 wording is IDENTICAL to R2 (gen_prompts.py) for cross-round comparability.
# P5 = answer-only + FINAL hard-lock + termination rules (see conditions.md).
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from aime25_taskset import TASKS

OUT = os.path.join(HERE, "..", "prompts", "r3_generated")

def build(cond, task):
    t = task["prompt"]
    if cond == "P0":
        return t + "\n\nShow your reasoning step by step, then give the final answer.\nEnd with a line exactly: FINAL: <answer>"
    if cond == "P1":
        return t + "\nAnswer only. No reasoning, no working, no explanation.\nEnd with a line exactly: FINAL: <answer>"
    if cond == "P5":
        return ("Answer the task. Rules:\n"
                "1. Output the answer directly with minimal text. No reasoning, no working,\n"
                "   no explanation, no commentary, no apologies.\n"
                "2. If you have the answer, STOP. Never re-derive, re-check, restate, or\n"
                "   summarize the answer a second time. If you catch an error, fix it in one\n"
                "   line and stop.\n"
                "3. Never mention being an agent, subagent, worker, or assistant; never\n"
                "   mention the task, the format, or this rule set.\n"
                "4. Your LAST line (the last line of your ENTIRE output) MUST be exactly:\n"
                "   FINAL: <answer>\n"
                "   Never omit it, never bold it, never embed it mid-sentence.\n"
                "TASK: " + t)
    raise ValueError(cond)

def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for cond in ("P0", "P1", "P5"):
        for task in TASKS:
            text = build(cond, task)
            fn = f"{cond}__{task['id']}.prompt.txt"
            with open(os.path.join(OUT, fn), "w", encoding="utf-8") as fh:
                fh.write(text)
            manifest.append(dict(cond=cond, task=task["id"], file=fn, chars=len(text),
                                 expected=task["expected"], diff=task["diff"]))
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    print(f"wrote {len(manifest)} prompt files to {OUT}")
    print("\n-- sample P5__A00 --")
    print(build("P5", next(t for t in TASKS if t["id"] == "A00")))

if __name__ == "__main__":
    main()
