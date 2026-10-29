# 结构化输出派发（structured-dispatch）

> origin: ai · 2026-10-25 · goal-8a4c1d33 · 从 goal-template.md §2.4.1 外移（2026-10-26 瘦身）
> 用途：把「决策/分类/选择/抽取」型子任务焊死成结构化返回，主 agent 拿 `JSON.parse` 即得结果。

## 核心原理

KV-bound 环境下少产 token = 少占 decode 步数、低延迟、省显存。

| 做法 | subagent 实际产出 token | 形态 |
|------|------------------------|------|
| 主 agent 自由生成「推理+结论」 | ~300–800 token 散文 | 自由文本，要正则扒 |
| 派发 `router`（choice） | ~20–40 token | `{"action":"calculator"}` |
| 派发 `brief`（极简开放选项) | ~60–140 token | 干净 JSON |

## skill 位置

`workspace-zero/projects/dsh-structured-output/adapters/dsh/skills/structured-dispatch/SKILL.md`
（同仓库含代理补丁 `lib/structured.mjs` + 输出形状注册表 `agents.json` + 安装脚本 `install.mjs`）

## 四种输出形状（注册表 `agents.json`）

- `router` — 固定枚举 choice，如 `{"action":"calculator"}`（二/多分类路由)
- `brief` — 极简开放选项 + 置信度，≤3 条、理由一句话、summary 一句
- `advisor` — 开放选项 + 置信度，不限条数、理由可长（需更充分论证)
- `ticket` — 固定字段（enum 约束），如 `{"priority":"HIGH","assignee":"alice"}`

## 派发规则（硬约束识别方式，二选一）

1. **方式 A — model 后缀（推荐，硬约束）**：`model: <基座模型>__schema=<key>`，如 `qwen3.8-27b-w8a16__schema=brief`。代理自动剥掉 `__schema=brief` 再发给 vLLM 并按 `brief` 强制工具调用。
2. **方式 B — HTTP 头 `X-Agent-Name: <key>`**：自研 harness / 能自定义请求头时用。
3. **方式 C — 软约束（没装代理补丁）**：subagent system prompt 写「必须只返回如下 JSON：{...}」。

## 主 agent 派发指令模板

「这是个决策型子任务，不需要长文。目标：<一句话>。候选/期望：<router 给枚举；brief 说『最多 3 个方案带置信度』>。派发方式：model 配 `qwen3.8-27b-w8a16__schema=<key>`。拿到返回直接 JSON.parse 使用。」

## 推荐场景

- ✅ 强推：路由/分类、给几个带置信度的方案、抽取固定字段/表单填充
- ❌ 禁用：生成型任务（写文章/代码/长分析）

## 维护

- 加新形状 = 在 `agents.json` 加条目，注册表按 mtime 热加载，改完即生效无需重启代理。
