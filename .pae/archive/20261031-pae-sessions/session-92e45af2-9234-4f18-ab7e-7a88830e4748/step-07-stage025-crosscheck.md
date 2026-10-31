# Step 07：阶段 02.5 交叉验证（≥2 独立 LLM 源 + 回执 JSON 门禁）

## 目标
对阶段 02 的关键结论（至少：LDL 样本量裁决、FinnGen/BBJ/GIANT 免凭据可得性、TwoSampleMR 免凭据行为）做 ≥2 个不同 LLM 服务交叉验证，产出符合回执门禁的 JSON 工件。

## 现状约束
- 唯一联网通道 = ego-browser（`/Users/a1-6/.local/bin/ego-browser`，需先 `skill ego-browser` 读指南）；禁 web_search（付费）；纯 JS 聊天页禁 web_fetch。
- 站点任选 ≥2：ChatGPT / DeepSeek / GLM / Google AI Studio / Gemini / Perplexity / LMArena-agent。
- 回执门禁（AGENTS.md 网页 LLM 交叉验证节 + ego-verify skill）：`web-llm/*.json` 含 `kind: "ralph_web_llm_cross_check"` + `responses[]` + `successful_provider_ids[]`（长度≥2）+ `observed_at` ISO 8601 带时区。
- 完整 SOP：`.claude/skills/ego-verify/SKILL.md`（先读再动手）；矛盾答案记录矛盾点并进一步核实。

## 涉及文件
- 读：`loop-artifacts/stages/02/r1/`（待验证结论清单）、`.claude/skills/ego-verify/SKILL.md`
- 写：`repo/web-llm/cross-check-stage2-20261028.json`（回执）、`loop-artifacts/stages/02/r1/cross-check-notes.md`（矛盾点与裁决记录）

## 做法
2-loop：
1. **备份**：cp stage02 产出到 /tmp。
2. **执行**：
   - 从 stage02 产出里挑出「会改变 MR 结果/门禁结论」的关键断言（最多 5 条，每条一句话 + 我的 conf）。
   - ego-browser 依次访问 ≥2 个站点，把同一条断言分别喂给 2 个不同 LLM，收集回答原文片段。
   - 组装回执 JSON（字段齐全），矛盾的条目记入 cross-check-notes.md 并注明裁决。
3. **review/verify**：`python3 -c` 校验回执 JSON：kind 正确、`len(successful_provider_ids)>=2`、observed_at 带时区。
4. **提交**：落盘 web-llm/*.json + notes，判定 stage 02 pass（含 02.5）才进 03。

## 验收标准
- 回执 JSON 三项门禁全过（kind/responses/successful_provider_ids≥2/observed_at 带时区）。
- 每条被验证断言有 ≥2 个不同 provider 的回答记录；矛盾项有裁决 + 理由。
- 若 ego-browser 故障：降级记录故障 + 结论 conf 降 0.2，写 knowledge/efficiency-bottlenecks.md，不静默跳过本阶段。