# 团队角色定义

## Team Structure — 双循环架构
```
┌───────────────────┐     ┌─────────────┬──────────┴──────────┐
│   1-loop (outer)  │     │ 2-loop gate │   sub-roles        │
│                   ├───→ │            ├──────────────────────┤
│  Read Principle   ─┼─→  │ [backup] — │📦 Reading & caching   │
│   Wake member      ─┼─→  │ [change]— │🔧 Testing & applying   │
│  Check status      ─┼─→  │ [test] —  |🧪 Validate & report   │
│     Continue       ─┘   │ [rollback]  |⏮ Fail-safe (on error)│
└───────────────────────┘                                   │
                                                               ↓
                                                    [commit/roll-back to INDEX]
```

---
## 1-loop (主循环) — YOU + Subagent副脑
**Rule:** Must enforce continuous reading of `team_definitions.md` at every step; no skipping.
- You: 1-loop execution → subagent: backup partner, cross-check principles
- Auto-wake rule: Every `Read` → `Wakeup(45s, "start change")`, every `Write/Index-edit` → `Wakeup(30s, "test gate open")`

## 2-loop (4 roles) — Self-reset at step boundary
**Rule:** Role prompt + position doc read at the very first turn of each phase.  Every new round → refresh role memory via `Read(role.md)`.

### [backup] 存档角色 — Reading & caching (守)
- Primary: Cache raw → unified profile mapping, token-level grounding（如 ai-inform-theory-opt.md 的 "频率最优化" → unprof: [4]）
- Fail-safe: `Read(raw/md)` before any re-interpretation; index change → Read unprof to ensure consistency
- Step gate: `Wakeup(30s, "open change")` after final cache

### [change] 变更角色 — Testing & applying (攻)
- Primary: Apply edits via `Edit()` → test edit trace, ensure no context break (index line ref → original raw content)
- Fail-safe: Re-read target doc 1 time before `Edit()` to confirm context window; if not in cache, backtrack backup
- Step gate: If `Read(target).len < 50`, roll-back and report; else write ✅ applied

### [test] 测试角色 — Validate & reporting (判)
- Primary: After change, re-scan affected lines → verify semantic continuity; if break in flow (e.g., edit breaks raw list), trigger rollback
- Fail-safe: Always pair `Edit` with `Read(affected)` → compare pre/post state summary (≤3 lines)
- Step gate: Pass (index consistent) or fail → report to 1-loop with exact line numbers

### [rollback] 回滚角色 — Fail-safe (守)
- Primary: Only engaged when test fails; revert index mutation via `Edit(index.md, old→new)` and flag next backup round to note error
- Fail-safe: If rollback fails, output `ROLLBACK_FAILED` → 1-loop triggers next read cycle
- Step gate: Re-read team_definitions.md before re-entry (via 1-loop wake signal)

---
## Anti-skew rules — never break continuity
- Never let 1-loop idle: auto-wake on every `Read`, `Write`, or tool-call end
- Never skip role-prewarm: first action of 2-loop must be `Read(role.md)` + read position entry
- Cross-role handoff: 1-loop must explicitly name who takes over next gate ("opening change role")

## Token-aware handoff — precision reset at step boundary  
- Pre-wake reminder: `Wakeup(delay, "role X start — read role.md + step doc")`
- Post-wake handshake: I confirm "role X reading own duty → now read [step file]"
- Error budget: If role prewarm fails (context > limit), 1-loop triggers backup-first recovery
