# Memory

## Migrated subset

Keep only the durable pieces here:

- Stable preferences
- Long-lived decisions
- Important project context
- Things that should survive restarts

## Current scope

- Desktop is the active workspace location
- `workspace-zero` is curated instead of full-fidelity
- Only the memory, agents, and loop documents are kept
- `~/workspace-zero` is the fuller historical source workspace; this desktop copy stays as the curated OpenClaw subset
- The stable user profile has been mirrored into Hermes `~/.hermes/memories/USER.md`
- User profile baseline: 成璐, Asia/Shanghai, concise/direct, action/verification, default autonomous execution within safety
- Hermes has been installed and migrated from OpenClaw config settings only; no workspace memory or skills were present to import
- LM Studio is the active local model source for OpenClaw and Hermes
- Browser-heavy Hermes work should be kept as a narrow diary loop in `memory/` with dated round files
- Hermes cron currently hits a runtime `NameError: tree_reduce is not defined` after the context-length fix; this is a Hermes-side blocker, not a workspace file issue
- Community Hermes WebUI is installed at `http://127.0.0.1:8787` and reads Hermes state from `~/.hermes`
- Hermes WebUI default workspace is pointed at `/Users/a1-6/Desktop/workspace-zero`
- LM Studio stateful chats use `response_id` / `previous_response_id`; Hermes and OpenClaw still keep their own session stores, so source naming should stay explicit
- Use a prefix convention when naming sessions and notes, e.g. `HERMES:` vs `OCLAW:`

## 2026-04-26: User Profile System v2.0 Initialized

- Cron-driven profile extraction completed on first run
- Scanned 1,487 raw files from memory/raw/ (ai_chats + memory subdirectories)
- Extracted 3 categories: preferences, thinking_patterns, behavior_traits
- Built unified_profile.json (v2.0) with 6-dimension analysis from canonical sources
- Checkpoint tracks all 1,487 file hashes for idempotent re-runs
- Key sources: user_intent_and_method.md (6-dim distillation), methodology_approach.md, user_preferences_2026-03-26.md
- Weight framework updated: 自动化(0.6)/写作(0.2)/学术(0.1)/健康人脉(0.1) — superseded earlier 学术(0.4)/资本(0.2)/健康(0.2)/人脉(0.2)

## Update rule

When new information matters, write it here in a short, durable form.
