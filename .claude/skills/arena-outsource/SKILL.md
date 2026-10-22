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

## 拆分优先（大调研题 · 2026-10-22 成璐 m00656 指令）

大题目 ≠ 一个 subagent 全包。标准流程：
1. **Lead 拆正交子领域**（3–7 个；每个子领域能独立成一句话问题）
2. **每个子领域 1 个 subagent**（任务卡自包含、背景 ≤10 行），并行 ≤3（subagent 上限）
3. subagent 按本 SOP 走 arena agent mode 调研 → 交付物先落盘
   3a. **arena 通道调研时，每个子领域拆成 2 个 subagent**（主调研 + 交叉验证），而非 1 个 subagent 做两件事——arena 失败率高，拆开后即使挂了一个，另一个还能落盘
   3b. **任务时长阈值**：≤15min 短任务（无需 checkpoint）/ 15–30min 中任务（需 checkpoint）/ >30min 长任务（应拆分）
4. Lead 汇总 → 交叉验证门禁 → 回写项目

为什么拆：短任务失败模式少、可断点恢复、可并行。本会话实证：3 个 20–90min 长任务挂 2 次 + 1 次 arena 回复未落页；子领域级短任务全部落盘。

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
[正交性自检]（可选）本子领域与其他子领域的输入/输出/时间轴重叠度（<30% / 30-50% / >50%）
[落盘约束] 文件不存在=任务未完成，Lead 不验收
```

## 失败处理与降级（2026-10-22 实测补丁 · 本轮 4 次错误归纳）

1. **回复落页校验**：提交后先 waitForFunction 等新输出出现；**三档超时**：30s 无新 DOM 节点 → 判定"没跑"，re-snapshot 重新定位输入框+发送按钮，重试 1 次；1min 有输出但无新输出 → 判定"跑慢"，继续等到 3min；3min 无新输出 → 判定"超时"，**直接进降级阶梯第 2 级**（不再 re-snapshot 第二次）。"提交成功"≠"回复已落"（实测：decomp 提交成功但回复未落页，页面疑似 outage，subagent 空等 20min+）。
2. **降级阶梯**（逐级降，每级记录原因）：arena agent mode → arena 普通 Battle → ego-browser 直抓目标页 → 自答。自答时 conf −0.2，文件头标「arena 不可用 <日期> <原因>（降级自整理）」。
3. **恢复协议（幂等）**：subagent 开工先检查交付文件是否已存在且完整 → 完整则跳验证；中断后从最近完成步骤续跑，任务卡必须可重入（不依赖内存态）。
4. **交叉验证降级**：第二站点不可用（页面漂移/未登录）→ 用 arXiv 摘要/官方文档直核替代，回执记「交叉验证降级：<站点>不可用，改 <来源>」（实测先例：persona 调研 ChatGPT 漂移 → arXiv 2509.14543/2509.24930 直核）。
5. **长任务 checkpoint**：预计 >15min 的任务，先写交付文件「开始」行 + 更新 loop-state，再开工；中途挂掉 Lead 也能从磁盘看出进度（实测：persona RESEARCH.md 87min 后才落盘，期间无任何中间痕迹，只靠 .bak-v0 推断）。
6. **格式校验**（理论推演，待实测）：任务卡加"[格式校验] 交付物必须是 <markdown 表格/JSON>，否则重写"；Lead 收到后先 grep 关键字段确认格式合规。
7. **登录态检查**（理论推演，待实测）：提交前 snapshot 确认"退出"按钮存在（=已登录）；若会话被重置 → 从第 1 步重新开始。
8. **串行提交**（理论推演，待实测）：同一 taskSpace 内多任务串行提交，不并发；等回复落页再提交下一个。
9. **落盘硬约束**（高优，本会话实证 #4）：任务卡加"文件不存在=任务未完成，Lead 不验收"；Lead 收到完成通知后先 `ls` 确认文件存在+行数>0（实测：memory-hooks researcher 结束未写文件）。

## 边界
- arena 是**执行层**外包，决策仍在本会话（conf 低/矛盾 → 自己用 ego-browser 补查）
- subagent 无网络（AGENTS.md 硬规则）：需要在线信息时由 Lead（本会话）走本 skill 代查并写文件，subagent 读文件
- 匿名 Battle 评测（非 agent mode）有专门工具：`projects/decomp/arena_capture/`（Edge+CDP 驱动，先读其 SKILL.md）——与本 skill 正交：那里是「评测模型」，这里是「外包任务」
- web_search 仍禁用（付费）；纯 JS 聊天页 WebFetch 仍禁用
