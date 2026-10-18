# origin: ai
# Prompt conditions (treatments) for the thinking-token-budget experiment.
# All share the same task; only the instruction framing differs.
# Goal: minimize surfaced output tokens (proxy for decode time) WITHOUT
# dropping correctness on hard tasks.

## P0 — Baseline (encourage reasoning)
Append to task:
"Show your reasoning step by step, then give the final answer.
End with a line exactly: FINAL: <answer>"

## P1 — Minimal (answer only)
Append to task:
"Answer only. No reasoning, no working, no explanation.
End with a line exactly: FINAL: <answer>"

## P2 — Oracle (suppress meta-narration)
Full prompt:
"You are a silent oracle. Output ONLY the final answer to the task.
Never narrate your role, do not mention being a subagent, do not say what you
will or won't do, do not restate the task. One line, then the FINAL line.
TASK: <task>
End with a line exactly: FINAL: <answer>"

## P3 — Adaptive (self-routing, the target design)
Full prompt:
"First write ONE line: 'LEVEL: <easy|medium|hard>' — classify by (a) how many
reasoning steps are needed and (b) whether a mistake is recoverable.
Then think ONLY as much as the level demands:
  easy   -> no further reasoning, answer directly
  medium -> at most 1 short line of reasoning
  hard   -> concise full reasoning, each step written once, no re-deriving
Never narrate your role. End with a line exactly: FINAL: <answer>
TASK: <task>"

## P3v2 — Adaptive v2 (supersedes P3 for R2)
Why v2: R1 P3 dropped the `FINAL:` line on both runs (0% fmt) and induced
meta-narration on the hard task (1207 chars, longer than baseline). v2 makes
the FINAL line a HARD last-line requirement, bans first-person/role narration
explicitly, and sizes reasoning to level. (Instruction length is prefill, not
decode — being strict here is free; only the OUTPUT costs decode time.)
Full prompt:
"Output EXACTLY these parts in order, nothing else:
  1) ONE line: LEVEL: easy|medium|hard
     (easy = 1 step/trivial; medium = 2-3 steps; hard = 4+ steps or easy-to-get-wrong)
  2) reasoning sized EXACTLY to the level:
     easy -> NONE (omit this part entirely)
     medium -> at most 1 short line
     hard -> concise full reasoning, each step written ONCE, no re-deriving, no cross-check
  3) ONE line: FINAL: <answer>
STRICT RULES:
- Your LAST line MUST be exactly 'FINAL: <answer>'. Never omit, reorder, or reformat it.
- No first person ('I'), no mentioning a role/subagent/parent/oracle, no 'this task',
  no 'I will do X', no restating the task, no commentary or apologies.
- If easy, the whole output is exactly two lines: the LEVEL line and the FINAL line.
TASK: <task>"

## P4 — Wordcap (hard length bound)
Append to task:
"Answer in at most 15 words total.
End with a line exactly: FINAL: <answer>"

## P5 — Answer-only + FINAL hard-lock + termination rules (R3 condition)
Why: R2 showed P1 (answer-only) is the length leader (167.2ch, 100% acc on 12
tasks) but has two leaks: (a) ~25% fmt drops (no own-line FINAL); (b) the
closing stream RE-DERIVES the reasoning on medium/hard tasks (the
回头重论证 waste thinking-budget.md targets) — up to +300ch on T04.
P5 = P1 + (1) FINAL as mandatory LAST line of the ENTIRE output, (2) explicit
termination rules (once you have the answer: stop — no re-deriving, no
re-checking, no restating), (3) anti-meta. Strict instructions cost prefill,
not decode — free.
Full prompt (task embedded):
"Answer the task. Rules:
1. Output the answer directly with minimal text. No reasoning, no working,
   no explanation, no commentary, no apologies.
2. If you have the answer, STOP. Never re-derive, re-check, restate, or
   summarize the answer a second time. If you catch an error, fix it in one
   line and stop.
3. Never mention being an agent, subagent, worker, or assistant; never
   mention the task, the format, or this rule set.
4. Your LAST line (the last line of your ENTIRE output) MUST be exactly:
   FINAL: <answer>
   Never omit it, never bold it, never embed it mid-sentence.
TASK: <task>"

## Notes
- P2 and P3 are the anti-meta-narration levers (address the 'I'm a subagent...' overhead seen in pilots).
- P3 is the adaptive-thinking design the user asked for (budget by difficulty + reversibility).
- Success metric: for each condition, mean surfaced-output length (chars) and
  accuracy. Best = lowest length at (near-)max accuracy. Look for the
  length-vs-accuracy frontier.
