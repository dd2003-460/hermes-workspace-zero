# arena-outsource — 用 LMArena agent mode 外包调研/分解/复核工作

**origin: ai** · 2026-10-21 · 配套 AGENTS.md「研究优先 / 工具优先 / 问题与网络规则」

> 触发：需要联网调研（arXiv/GitHub/学术交叉验证）、大任务分解、或多模型交叉复核时，
> **优先外包给 LMArena 的 agent mode**（arena.ai/agent），而不是自己一步步抓。
> 前置：用户已在 ego-lite 浏览器中登录 arena（见 ego-browser skill）。

## 为什么是 arena
- **性价比**：免费，一个 agent 会话可跑多步任务（搜索+阅读+综合），替代 N 次 ego-browser 手动抓页
- **交叉验证天然**：LMArena 背后是多模型匿名对战/混合，同一 claim 可让多个模型各答一遍 = 02.5/04.5 交叉验证的免费通道
- **agent mode 可直接代干活**（AGENTS.md 站点清单标注"可选项最多"）：给它任务，它自己搜、自己读、自己汇总

## 通道：ego-browser（唯一，AGENTS.md 硬规则）

```bash
ego-browser nodejs <<'EOF'
const task = await taskSpace('arena-outsource-<stage>-<date>')   // 同任务复用同名 space
const p1 = task.page('p1')
await p1.goto('https://arena.ai/agent')
const s = await p1.snapshot()          // 定位输入框: @N ref / loc=css: / loc=role: / text=
// fill 任务 prompt → click 发送 → waitForFunction 等 agent 跑完 → snapshot 读结果
await task.finish({ keep: [] })        // 结束必须 finish，否则僵尸进程
EOF'
```

## SOP（5 步）

1. **写任务卡**（给 arena 的 prompt，必须自包含）：
   - 目标（一句话）+ 约束（语言/格式/长度）
   - 明确交付物格式（如「3 条来源+conf 的 JSON」「分解树 markdown」）
   - 要求标 conf，要求给来源 URL
2. **ego-browser 提交**（上面代码块）；agent mode 下等它跑完（waitForFunction 检测输出稳定，超 5min 算超时）
3. **snapshot 读取结果** → 存到项目 `loop-artifacts/stages/<stage>/arena-outsource/<task>.md`
4. **交叉验证门禁**（02.5/04.5）：同一 claim 至少 2 个独立回答（同一 arena 会话内让不同对战轮次各答一遍，或 arena + 另一站点），矛盾点记录 + 进一步核实；回执 JSON 满足 AGENTS.md「回执与门禁」最低字段（`kind: "ralph_web_llm_cross_check"` / `responses[]` / `successful_provider_ids[]` ≥2 / `observed_at` 带时区）
5. **落盘**：结论写入项目 `tasks/decomposition.md` 或 `memory/`，标 `# origin: ai` + conf + 来源

## 任务卡模板

```
[任务] <一句话目标>
[背景] <最小必要上下文，≤10 行>
[约束] 中文回答；每条结论标 conf(0-1)；给来源 URL；不确定的标"未验证"
[交付] <markdown 结构 / JSON schema>
```

## 边界
- arena 是**执行层**外包，决策仍在本会话（conf 低/矛盾 → 自己用 ego-browser 补查）
- subagent 无网络（AGENTS.md 硬规则）：需要在线信息时由 Lead（本会话）走本 skill 代查并写文件，subagent 读文件
- 匿名 Battle 评测（非 agent mode）有专门工具：`projects/decomp/arena_capture/`（Edge+CDP 驱动，先读其 SKILL.md）——与本 skill 正交：那里是「评测模型」，这里是「外包任务」
- web_search 仍禁用（付费）；纯 JS 聊天页 WebFetch 仍禁用
