# Web LLM Receipt — Perplexity

| Field | Value |
|-------|-------|
| **Service** | Perplexity AI |
| **Final URL** | https://www.perplexity.ai/search/f70863ce-d4f9-4d63-9b8c-634a7abf06b6 |
| **Observation Time** | 2026-08-14T17:47:35.302Z (real browser JS timestamp) |
| **Question Asked** | What are the official specifications for the NVIDIA GeForce RTX 3090 GPU? Specifically: power consumption (TDP/TGP), memory type and speed, CUDA core count, boost clock speed, recommended PSU. Also any software ecosystem info (CUDA compute capability, supported APIs). |
| **Source Type** | Web LLM (Perplexity) — proprietary model with web search, answer includes inline citations |
| **Conditions** | Logged-in user account; question typed into search input and submitted; answer rendered with citation links (asus+, techpowerup+, nvidia+, nanoreview+, techradar+) |

## Visible Answer (extracted via browser JS)

```
Here are the official specifications for the NVIDIA GeForce RTX 3090 (Founders Edition/reference design):

Core Specifications
Specification | Value
1. Power Consumption (TDP/TGP) | 350 W notebookcheck+4
2. Memory Type & Speed | 24 GB GDDR6X @ 19.5 Gbps (effective) asus+5
3. CUDA Core Count | 10,496 asus+5
4. Boost Clock Speed | 1,695 MHz techpowerup+4
5. Recommended PSU | 750 W (NVIDIA official); 850 W commonly recommended by board partners asus+2

Architecture Details
Feature | Specification
GPU Architecture | Ampere (2nd-gen RTX) nvidia+2
GPU Codename | GA102 techpowerup+2
CUDA Compute Capability | 8.6 nanoreview
Tensor Cores | 328 (3rd-gen) nvidia+2
RT Cores | 82 (2nd-gen) nvidia+3
SMs (Streaming Multiprocessors) | 82 techradar+1
Fabrication Process | Samsung 8 nm nanoreview
Transistor Count | 28 billion nanoreview

Software & API Support
API / Technology | Version / Support
DirectX | DirectX 12 (Feature Level 12_2) nanoreview
Vulkan | Vulkan 1.3 nanoreview
OpenGL | OpenGL 4.6 asus+1
OpenCL | OpenCL 3.0 nanoreview
CUDA | CUDA 8.6 (Compute Capability) nanoreview
Ray Tracing | Hardware-accelerated (2nd-gen RT Cores) nvidia+2
DLSS | DLSS 2 (Tensor Core AI acceleration) nanoreview

PCIe Interface: PCIe 4.0 x16 asus+3

Additional Notes
Memory Bus: 384-bit asus+4
Memory Bandwidth: 936 GB/s techradar+2
Display Outputs: 1x HDMI 2.1, 3x DisplayPort 1.4a asus+2
Max Resolution: 7680x4320 (8K) asus
Power Connector (Founders Edition): 1x 12-pin (adapter to 2x 8-pin included) techradar

The 750 W PSU recommendation comes directly from NVIDIA for the Founders Edition, though many board partners (ASUS, MSI, etc.) recommend 850 W to account for system headroom and transient power spikes. asus+2
```

## Ego Observation Reference
- snapshotText() captured the full page DOM at observation time
- JS extraction confirmed answer text in DOM via `.prose` selector (10,000 char limit)
- Page title: "What are the official specifications for the NVIDIA GeForce RTX 3090 GPU?... - Perplexity"
- Page shows answer tab (答案), link tab (链接), and image tab (图片)

## Clues Extracted
1. Perplexity provided structured spec tables with inline citations (asus+, techpowerup+, nvidia+, nanoreview+, techradar+, notebookcheck+)
2. All values match NVIDIA official specs and ChatGPT answer
3. Perplexity cited multiple independent sources for each claim
4. Notable: Perplexity noted the distinction between NVIDIA's 750W recommendation and board partners' 850W recommendation
5. Software ecosystem info: CUDA 8.6, DirectX 12, Vulkan 1.3, OpenGL 4.6, OpenCL 3.0, DLSS 2

## Independent Evidence Support Status
- **SUPPORTED** by NVIDIA official page (https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3090-3090ti/)
- **SUPPORTED** by Wikipedia (https://en.wikipedia.org/wiki/GeForce_RTX_3090)
- **SUPPORTED** by TechPowerUp GPU database (https://www.techpowerup.com/gpu-specs/rtx-3090.c3355)
- **SUPPORTED** by ChatGPT independent answer (same receipt directory)
- Perplexity's own citations reference: asus.com, techpowerup.com, nanoreview.info, techradar.com, notebookcheck.net, nvidia.com

## Uncertainty Notes
- Perplexity provides inline citations which increase trustworthiness
- The citation markers (e.g., "asus+5") indicate the number of supporting sources cited
- All values cross-verified against authoritative sources and ChatGPT answer
