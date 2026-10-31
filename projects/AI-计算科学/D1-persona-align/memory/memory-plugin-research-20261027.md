# 记忆插件调研：Hermes 规则提醒机制选型

> origin: ai · 2026-10-27 · 成璐要求调研"记忆插件 + hook 提醒"，格式=每个候选怎么样→最后决定用啥
> 痛点：规则写在 MEMORY.md/SOUL.md，session 开头注入，聊久了上下文一长就稀释；goal 只覆盖 goal 活跃期，覆盖不了全部；不可能每轮让 agent 重读整个 SOUL。

---

## 一、Hermes 现有记忆机制盘点（先看清家底）

| 机制 | 何时生效 | 干什么 | 局限 |
|------|---------|--------|------|
| **MEMORY.md / USER.md**（memory 工具） | 每次 session 开头注入系统提示 | 跨 session 持久记忆，char 限制 2200/1375 | 只在开头注入一次，聊 30 轮后中间内容被稀释；容量小 |
| **memory flush**（`flush_min_turns: 6`） | 上下文压缩前 | 自动触发 agent 把重要信息存进 MEMORY.md，防丢 | 只防"丢"，不防"当下忘了规则" |
| **nudge**（`nudge_interval: 10`） | 每 10 轮后台 fork review | 让 agent 反思要不要存记忆/技能 | 异步、不保证、不注入规则 |
| **goal 机制** | goal 活跃期每轮 | judge 判未完成→注入 continue 提示（带 goal 全文） | 只覆盖 goal 相关；goal 外不管；一段文本 |
| **hooks**（当前 `hooks: {}` 空） | 各种缝 | 见下 | 未配置=没用上 |

**结论**：现有机制里，"每轮稳定提醒规则"这个能力是空的。MEMORY.md 管开头，goal 管任务期，中间大片空白。

---

## 二、hook 能提醒的"缝"（成璐问：要输出的时候能不能提醒）

Hermes hooks 支持的与"提醒/输出"相关的缝：

| 缝（event） | 时机 | 能干什么 | 适合做规则提醒吗 |
|------------|------|---------|----------------|
| `pre_llm_call` | 每轮 LLM 调用前（工具循环开始前） | 返回 `{"context": "..."}` 注入当轮 user message | ✅ **最适合**。每轮都看到，等于持续提醒；注入 user message 不破坏 system prompt 缓存 |
| `post_llm_call` | 每轮产出最终回复后 | 观察（返回被忽略） | ❌ 只能事后看，不能改本轮 |
| `transform_llm_output` | 最终回复交付前 | 返回非空字符串=替换回复 | ⚠️ 能改输出但机械，适合兜底不适合提醒 |
| `pre_send` | 消息发出前 | 改/拦 outgoing | ⚠️ 同 transform，事后拦截 |
| `agent:start` | session 开始 | 注入 content | 只一次，等同于 MEMORY.md |
| 压缩后 re-inject | compaction committed 后 | 插件可 re-inject 被摘要掉的细节 | 辅助，配合 pre_llm_call |

**关键事实**：
- `pre_llm_call` 每轮触发一次（一次 user turn，不是每次 API 调用），返回的 context 追加到当轮 user message。
- 注入位置是 user message 不是 system prompt → 系统提示缓存不受影响，成本只是每轮多几十~几百 token。
- shell hook 就能做，不用写 Python plugin：stdout 输出 `{"context": "规则卡内容"}` 即可。

**回答成璐的问题**：能。"要输出的时候提醒"= `pre_llm_call`（每轮思考前把规则塞给我，我输出时自然记得）；"输出后检查"= `transform_llm_output`/`pre_send`（兜底拦 AI 腔调）。两个都能配，前者为主。

---

## 三、候选方案对比（每个"怎么样"）

### 方案 A：只靠 MEMORY.md（现状）
- **怎么样**：session 开头注入，免费，零维护。
- **坑**：聊 20+ 轮后规则稀释，"经常想不起规则"就是这个。capacity 2200 字符也装不下全部规则。
- **判定**：不够，只能当底层。

### 方案 B：pre_llm_call 每轮注入"规则卡"
- **怎么样**：写一个 shell hook，每轮把一张**精简规则卡**（从 SOUL/MEMORY 提炼，50-150 token）注入当轮。等于每轮都提醒，防漂移。
- **成本**：每轮多几十~一百多 token（user message 侧，不破坏 system prompt 缓存）。对 200 轮 goal 来说总成本可控。
- **坑**：规则卡写太长=每轮烧 token+干扰；要克制，只放最硬的最易忘的。
- **判定**：✅ 主力方案。直接解决"聊久忘规则"。

### 方案 C：transform_llm_output / pre_send 输出兜底
- **怎么样**：输出前用脚本检查/替换 AI 腔调特征词（"综上所述/值得注意的是/让我仔细"等）、检测结构化标题。
- **坑**：规则式替换容易误伤、机械；自然语言判断放脚本里做不了，得调 LLM（贵+慢）。
- **判定**：⚠️ 可选兜底，只做粗粒度特征词拦截，不做主方案。

### 方案 D：goal 驱动
- **怎么样**：goal 活跃期每轮注入 continue 提示（带 goal 全文），把关键规则写进 goal 描述。
- **坑**：只覆盖 goal 期；goal 外（日常聊天）不管；一段文本容量有限。
- **判定**：长任务期间用，和 B 互补，不冲突。

### 方案 E：memory flush + nudge 调频
- **怎么样**：把 `nudge_interval` 调小（如 5）、确认 `flush_min_turns` 生效，让 agent 更频繁存记忆。
- **坑**：解决"存"不解决"取/记得"；nudge 是异步 review 不保证注入。
- **判定**：辅助，防丢用。

---

## 四、最终决定（组合拳）

**决定用 B 为主 + A 兜底 + D 补长任务 + E 防丢，C 暂不做。**

具体落地：

1. **建规则卡文件** `~/.hermes/rule-card.md`（或工作区内），内容是提炼后的硬规则，控制在 ~150 token：
   - 微信聊天真人语感（不结构化/去名词化/保留不确定/半截话/不总结收尾）
   - 诚实第一（不知道就说不知道）
   - 过程可见（先计划后执行）
   - 简洁直接
   - （只放最硬最易忘的，SOUL 全量不进卡）

2. **配 pre_llm_call shell hook** 每轮注入规则卡：
   ```yaml
   # ~/.hermes/config.yaml
   hooks:
     pre_llm_call:
       - command: "~/.hermes/agent-hooks/inject-rule-card.sh"
   ```
   ```bash
   #!/usr/bin/env bash
   # ~/.hermes/agent-hooks/inject-rule-card.sh
   cat - >/dev/null
   card=$(cat ~/.hermes/rule-card.md 2>/dev/null)
   [[ -n "$card" ]] && jq --null-input --arg c "$card" '{context: ("[规则卡]\n" + $c)}' || printf '{}\n'
   ```

3. **SOUL.md 改软人格体**（配合 persona 结论）：把 SOUL 从"规则清单"改写成"人格描述"（你是成璐的数字分身，你说话像真人，你思考先分类再执行…），软+human 语言引导内化，而不是硬规则堆砌激活执行模式。

4. **MEMORY.md 保持精简**：只放跨 session 事实（工作区路径、项目状态指针），不放行为规则（规则归 SOUL 软人格 + rule-card 硬卡）。

5. **goal 用于长任务**：decomp/pfb 核验这类长探索用 goal，goal 描述里带任务相关规则。

6. **nudge/flush 保持默认**（10/6），不额外调。

---

## 五、SOUL 软提示 + persona 结论（成璐问的关联性）

- SOUL.md 本质就是**软提示**（系统提示里的人格描述），不是硬规则引擎。
- persona 研究结论支持：**人格描述体（软+human 语言）比规则清单体（硬）更能让 agent 自然内化**。规则清单激活"执行规则"模式→机械；人格描述激活"成为这个人"模式→自然。
- 但纯软有漂移风险（聊久忘）→ 所以 **软人格(SOUL) 管"成为谁"，硬规则卡(hook 每轮注入) 管"别忘底线"**，双层。
- 这正好回应"goal 只能覆盖一部分不可能每轮看全部 SOUL"：SOUL 全量确实不该每轮看，看的是**提炼后的规则卡**（几十 token），SOUL 本体只在 session 开头加载一次做人格底座。

---

## 六、待办（等成璐确认方向后执行）

- [ ] 写 `~/.hermes/rule-card.md`（初版规则卡，等成璐过目）
- [ ] 写 `~/.hermes/agent-hooks/inject-rule-card.sh` + 配 config.yaml hooks
- [ ] SOUL.md 软人格化改写（基于 D1-persona-align 的 persona.md 8 层成果）
- [ ] 重启 gateway 验证 hook 生效（`hermes hooks test` 或实际聊几轮看是否注入）
