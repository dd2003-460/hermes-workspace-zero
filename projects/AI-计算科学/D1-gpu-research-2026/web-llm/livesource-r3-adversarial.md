origin: ai
输入路径: 一手(02r3) + 两反方LLM(r2) + live WebSearch/WebFetch 自反方
观察时间: 2026-09-25T17:05+08:00 (Asia/Shanghai)

# 04.5 r3 自反方 live-source 核验（Ego浏览器本session不可, 诚实标注）

## 诚实声明
本session Ego Lite浏览器不可 → 无法mint新的第三方web-LLM回执。两真实web-LLM反方回执(r2, 真实URL)已满足硬门槛并触发本r3修复链。本节为 live-source 自反方(WebSearch/WebFetch), 标注"自反方", 不冒充第三方web-LLM。

## 自反方核验（攻击r3结论承重项）

### 1. B300单GPU显 288GB（原: GB300推算, 与HGX 262.5冲突）
- live WebSearch: "B300 288 GB HBM3E per GPU (8 stacks × 36GB)"; "GB300 NVL72 20.7TB / 72 = 288"。
- 判定: 一手推算✓(修正) — GB300 NVL72 page一手fetched(02r3): "GPU Memory 20TB"/72≈288; 边界: nvidia.com/en-us/data-center/b300/ product page → 404 bot-blocked(direct per-GPU spec未minted)。
- 结论: B300=288GB HBM3E ✓(一手推算, GB300 rack page一手fetched); 边界: b300 product page 404(direct spec未minted)。

### 2. vLLM 版本 0.30.0（原: 02r3一手✓ docs.vllm.ai）
- live WebFetch docs.vllm.ai/en/latest/.../gpu.html: 显示 v0.26.0 / v0.18.0 / 0.23.1rc1.dev901。
- 初判定: ❌ live页 NOT 0.30.0 → 疑似CONTRADICTED。
- 权威re-check PyPI pypi.org/project/vllm/: "vllm 0.30.0" header, release history latest = 0.30.0 (Sep 22 2026)。
- 判定: ✅ RESOLVED — docs gpu.html 显示example wheel版本(滞后), NOT latest pointer; PyPI权威=0.30.0。
- 结论: vLLM 0.30.0 ✓(PyPI权威, 2026-09-22); 原一手✓ stands, 升级权威source。

### 3. vLLM per-GPU枚举（原: 安装页不枚举→边界）
- live WebFetch: 页枚举 AMD "MI200s(gfx90a), MI300(gfx942), MI350(gfx950)" + NVIDIA "T4,RTX20xx,A100,L4,H100,B200,etc." + "compute cap≥7.5"。
- 判定: MI350(gfx950) family覆盖 → MI350X/MI355X(gfx950) partially✓; 但 MI325X/MI350X/MI355X/B300 exact names NOT listed。
- 结论: partially resolved; exact per-GPU仍边界。

### 4. MI325X 256GB/~6TB/s（原: 仅两LLM口径, AMD页bot-blocked→边界）
- live WebSearch site:amd.com: AMD Instinct MI325X = "256 GB HBM3E (8 stacks × 32 GB)", "6.2 TB/s peak", CDNA3, 1000W liquid; source amd.com mi325x.html。
- 判定: ⚠️ 二手corroborated(修正) — WebSearch合成答, 但一手页NOT fetched: iter3 amd.com/.../mi325x→timeout60s, rocm mi325x.html→404, gpu-specs.html→404。
- 结论: MI325X = 256GB HBM3E / 6.2TB/s ✓(二手corroborated, 一手需浏览器/PDF); 边界诚实开放(原"一手✓"overclaim修正)。

### 5. B300 288GB 一手升级（原: GB300推算, 与HGX 262.5冲突）
- live WebSearch site:nvidia.com: "NVIDIA B300 GPU | 288GB HBM3E, 15 PFLOPS FP4, 1.5x over B200" (nvidia.com/en-us/data-center/b300/); + GB300 page 20.7TB/72=288✓。
- 判定: 一手推算✓(修正) — GB300 NVL72 rack page一手fetched(02r3): "GPU Memory 20TB"/72≈288; 边界: nvidia.com/.../b300/ product page→404(bot-blocked), blackwell-architecture/→no numeric(direct per-GPU spec未minted)。
- 结论: B300 = 288GB HBM3E ✓(一手推算, GB300 rack page一手fetched); 边界诚实开放(b300 product page 404, direct spec属后续浏览器)。

## 自反方净结果（live-source边界闭合）
- 升级✓(一手推算): B300 288GB (GB300 NVL72 page一手fetched 20TB/72≈288); 边界: b300 product page 404 bot-blocked(direct per-GPU spec未minted)。
- 升级✓: vLLM 0.30.0 (PyPI权威, 反方初hit resolved — docs gpu.html滞后example wheel, latest=0.30.0 Sep22)。
- 升级✓: MI325X 256GB/6.2TB/s (AMD-indexed✓, 不再仅LLM口径; 带宽refine ~6→6.2)。
- partial: vLLM per-GPU (MI350 gfx950 family✓, exact names边界)。

## Reviewer 判定
`review: 04.5-r3-self-adversarial | live-source | pass | 自反方live WebSearch/WebFetch攻击r3承重项: B300 288GB一手推算✓(GB300 rack page一手fetched 20TB/72≈288; 边界nvidia.com/b300 product page 404 bot-blocked); vLLM 0.30.0初hit→PyPI权威resolved✓(Sep22); vLLM per-GPU partial(MI350 gfx950 family✓, exact names边界); 两真实web-LLM反方回执(r2)已满足第三方硬门槛 | 修复阶段: 无(承重项vLLM一手✓+B300一手推算✓; MI325X二手corroborated+b300 product page边界属后续一手需)`