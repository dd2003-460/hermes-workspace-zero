# 2026-04-22 Hermes Migration + LM Studio R1

## Goal

Try Hermes Agent, migrate the useful OpenClaw settings, and keep browser exploration as a bounded loop with dated diary files.

## What I checked

- OpenClaw workspace stays at `/Users/a1-6/Desktop/workspace-zero`
- OpenClaw `LOOP.md` stays minimal: read context, do task, record durable change, stop
- OpenClaw currently has five selectable LM Studio chat models
- Hermes was not installed at the start of this round

## What changed

- Installed Hermes Agent under `~/.hermes/hermes-agent`
- Migrated OpenClaw settings into Hermes with `hermes claw migrate`
- Imported LM Studio provider settings into Hermes config
- Switched Hermes default model to `lmstudio/qwen3.6-35b-a3b-ud-mlx`
- Kept OpenClaw workspace files untouched

## Findings

- OpenClaw had no workspace memory or skills directory to migrate
- The Hermes installer could not finish its first interactive wizard because this session has no TTY
- Hermes browser tooling is enabled, but the local node environment does not expose `npm` or `npx`, so browser-engine bootstrap still needs a separate path if we want to use Hermes browser automation directly

## Next step

- Keep browser exploration in a second round file and summarize the useful tools, memory layout, and migration gaps before expanding anything else
