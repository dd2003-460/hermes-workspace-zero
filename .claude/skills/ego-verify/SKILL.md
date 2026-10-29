# ego-verify — 网页 LLM 交叉验证 SOP

> 来源：原 AGENTS.md「网页 LLM 交叉验证流程」节，2026-10-21 移入（m00172 批准）。AGENTS.md 留核心原则 + 指针。

## 核心原则

1. **关键结论必须通过 ≥2 个不同 LLM 服务验证**（站点清单见下，任选 ≥2）
2. **不同 LLM 给出矛盾答案时，记录矛盾点并进一步搜索核实**
3. **禁止对纯 JS 聊天页做 WebFetch**（返回空，会无限空转）

## 唯一通道：ego-browser（ego-lite，复用已登录会话）

网页 LLM 交叉验证**只走 ego-browser**：用 `ego-browser` skill 驱动用户已登录的 ego-lite 浏览器（可见 profile，如 Profile 1），在页内向目标 LLM 提交 claim、等待回复、snapshot 读取。**不使用任何无头/非持久浏览器**（Playwright、`browser_navigate` 等一律不用）。

```bash
ego-browser nodejs <<'EOF'
const task = await taskSpace('web-llm-<stage>-<date>')   // 同一任务复用同名 space
const p1 = task.page('p1')
await p1.goto('https://chatgpt.com')
const s = await p1.snapshot()          // 定位: @N ref / loc=css: / loc=role: / text= / xpath=
// fill 输入框 → click 发送 → waitForFunction 等回复完成 → snapshot 读回复
await task.finish({ keep: [] })        // 结束前必须 finish，否则留僵尸进程
EOF
```

API 细节以 `ego-browser` skill 加载后的说明为准（当前 0.5.1.13：`taskSpace / page.goto / snapshot / fill / click / evaluate / waitFor* / task.finish`）。

## 站点清单（可复制网址，任选 ≥2；需用户已在 ego-lite 中登录）

| 站点 | URL | 备注 |
|------|-----|------|
| ChatGPT | `https://chatgpt.com` | |
| DeepSeek | `https://chat.deepseek.com` | |
| GLM（智谱清言） | `https://chatglm.cn` | |
| Google AI Studio | `https://aistudio.google.com` | |
| Gemini | `https://gemini.google.com` | |
| Perplexity | `https://perplexity.ai` | |
| LMArena | `https://arena.ai/agent` | **agent mode 可直接代干活**，可选项最多 |

## 回执与门禁（02.5 / 04.5）

每个验证问题写一份回执 JSON 到阶段目录 `web-llm/*.json`，最低满足：
- `kind: "ralph_web_llm_cross_check"`
- `responses[]`：每站点一条（`provider_id` / `endpoint_host` / `status` / 回复要点）
- `successful_provider_ids[]`：≥2
- `observed_at`：ISO 8601 带时区（如 `2026-10-17T00:25:00+08:00`；勿裸写本地日期）

字段 `evidence_refs` 引用成功回执路径；回执过门禁后，按项目收口路径更新阶段状态文件（无 CLI 依赖，旧的字段提交流程已废弃）。
**既证先例**：`projects/AI-计算科学/D1-gpu-inference-hardware/loop-artifacts/stages/04.5/r1/web-llm/`（手写回执过门禁；完整结构含 `adopted` / `rejected` / `rejected_reasons` / `two_leg_disagreements`）。

## 流程索引

- 1-loop 02.5: `loop/archived-20261016/1-loop/loop-legacy/02.5-交叉验证.md`（prompt-first 现行版: `loop/prompt-first/02.5-cross-check.md`）
- 1-loop 04.5: `loop/archived-20261016/1-loop/loop-legacy/04.5-交叉验证.md`（prompt-first 现行版: `loop/prompt-first/04.5-final-review.md`）
- Agent 准则: `sop/archived-20261016/gatherer.md` §LLM 网页版交流通用准则
