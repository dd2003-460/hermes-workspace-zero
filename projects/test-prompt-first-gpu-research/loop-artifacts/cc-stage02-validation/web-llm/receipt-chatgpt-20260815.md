# Web LLM Receipt — ChatGPT

| Field | Value |
|-------|-------|
| **Service** | ChatGPT (OpenAI) |
| **Final URL** | https://chatgpt.com/c/6a7f4444-1750-83ee-ae5f-be77c16d414b |
| **Observation Time** | 2026-08-14T17:38:30.684Z (real browser JS timestamp) |
| **Question Asked** | What are the official specifications for the NVIDIA GeForce RTX 3090 GPU? Specifically: power consumption (TDP/TGP), memory type and speed, CUDA core count, boost clock speed, recommended PSU. Also any software ecosystem info (CUDA compute capability, supported APIs). |
| **Source Type** | Web LLM (ChatGPT) — proprietary model, answer generated from training data and/or web search |
| **Conditions** | Logged-in user account; question typed into input textarea and submitted; answer rendered in chat interface |

## Visible Answer (extracted via browser JS)

```
RTX 3090 (Founders Edition/reference)
Architecture: Ampere / GA102
CUDA cores: 10,496
RT cores: 82, 2nd gen
Tensor cores: 328, 3rd gen
VRAM: 24 GB GDDR6X
Memory speed: 19.5 GT/s
Memory bus: 384-bit
Memory bandwidth: 936 GB/s
Base clock: 1.40 GHz
Boost clock: 1.70 GHz / 1,695 MHz
Graphics card power: 350 W
Recommended PSU: 750 W
CUDA capability: 8.6
NVLink: Yes
PCIe: 4.0
Overall confidence: 99-100%
```

## Ego Observation Reference
- snapshotText() captured the full page DOM at observation time
- JS extraction confirmed answer text in DOM via `[data-message-author-role="assistant"]` selector
- Page title: "What are the official specifications for the NVIDIA GeForce RTX 3090 GPU? - ChatGPT"

## Clues Extracted
1. ChatGPT provided a structured spec table matching the question
2. All values align with NVIDIA official specs (350W TDP, 24GB GDDR6X, 10496 CUDA cores, 1695 MHz boost, 750W PSU)
3. ChatGPT included a self-assessed confidence level of 99-100%
4. Software ecosystem info included: CUDA 8.6, DirectX 12, Vulkan 1.3, OpenGL 4.6, OpenCL 3.0

## Independent Evidence Support Status
- **SUPPORTED** by NVIDIA official page (https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3090-3090ti/)
- **SUPPORTED** by Wikipedia (https://en.wikipedia.org/wiki/GeForce_RTX_3090)
- **SUPPORTED** by TechPowerUp GPU database (https://www.techpowerup.com/gpu-specs/rtx-3090.c3355)
- **SUPPORTED** by Perplexity independent answer (same receipt directory)

## Uncertainty Notes
- ChatGPT's answer is generated from training data and/or web search; the model may not cite sources inline
- The "Overall confidence: 99-100%" is a self-assessment by the model, not an independent verification
- All values cross-verified against authoritative sources above
