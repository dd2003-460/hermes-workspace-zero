# 2026-04-22 Hermes WebUI R3

## Goal

Install a nicer community web UI for Hermes so conversation/session management is easier than the terminal view.

## What I installed

- Cloned `nesquena/hermes-webui` into `~/.hermes/hermes-webui`
- Bootstrapped it successfully
- Confirmed the local UI responds on `http://127.0.0.1:8787`

## What it reads

- Hermes agent state from `~/.hermes`
- Sessions, config, cron, skills, and memory in read-only UI panels

## Session boundary

- LM Studio remains the model backend
- Hermes and OpenClaw keep separate session stores
- Use explicit prefixes like `HERMES:` and `OCLAW:` when naming sessions or notes

## Next step

- If needed, point the WebUI default workspace at the curated desktop workspace instead of the repo default `~/workspace`
