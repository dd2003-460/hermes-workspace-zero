# 2026-04-22 Hermes Browser Loop R2

## Goal

Run a browser-and-memory research loop in Hermes, reading the previous diary first and then writing a new compressed round note.

## What changed since R1

- Hermes model provider is now `custom` with the LM Studio endpoint
- Hermes main model context length is explicitly overridden to 262144
- Hermes auxiliary compression is also pointed at the same LM Studio endpoint with a 262144 context override
- The cron job was re-created after the provider/context fixes

## Result

- The cron job got further than the earlier provider/context failures
- Hermes then failed with `NameError: tree_reduce is not defined` during API call execution

## Interpretation

- This looks like a Hermes runtime or dependency bug, not a workspace/content problem
- The workspace diary format is correct
- The blocking issue is now inside Hermes execution, after model routing and context detection

## Next step

- Either patch or upgrade Hermes to resolve the `tree_reduce` error, or switch the browser loop to another agent framework if we want a reliable recurring run
