---
name: web-llm-cross-verify
description: 通过多个网页 LLM 接口交叉验证事实。使用 Playwright 浏览器自动化，对已授权的 LLM 站点提交问题并读取回复。
trigger: 需要验证关键事实、claim、数据时，在 1-loop 02.5/04.5 交叉验证阶段或独立验证任务中触发
---

# Web LLM 交叉验证 Skill

## 概述

通过浏览器自动化对多个网页 LLM 提交同一验证问题，收集回复进行交叉比对。

## 网页 LLM 地址清单

### 已实现（ralph_runtime 支持）

| 站点 | URL | CSS 选择器 | 提交按钮 | 备注 |
|------|-----|-----------|---------|------|
| Perplexity | `https://perplexity.ai` | `textbox` | `button[aria-label="提交"], button[aria-label="Submit"]` | 需处理拒绝弹窗 |
| ChatGPT | `https://chatgpt.com` | `#prompt-textarea` | `button[data-testid="send-button"]` | 需手动登录 |
| Gemini | `https://gemini.google.com` | `[contenteditable="true"]` | `button[aria-label*="发送"], button[aria-label*="Send"]` | 需手动登录 |

### 待授权（需人类运行 `ralph web-llm-authorize`）

| 站点 | URL | 状态 |
|------|-----|------|
| LMArena | `https://arena.ai/agent` | 需授权 |
| Claude | `https://claude.ai` | 需授权 |
| Poe | `https://poe.com` | 需授权 |
| Grok | `https://grok.com` | 需授权 |
| Copilot | `https://copilot.microsoft.com` | 需授权 |
| 百度智能 | `https://aistudio.google.com` | 需授权 |
| 智谱 | `https://bigmodel.cn` | 需授权 |

### 禁止 WebFetch 的纯 JS 聊天页

以下站点**不能**用 `WebFetch` 抓取（返回空），只能通过 `ralph web-llm-check` 浏览器自动化：
- `perplexity.ai` / `chatgpt.com` / `claude.ai` / `gemini.google.com` / `grok.com` / `copilot.microsoft.com` / `arena.ai/agent` / `poe.com` / `bigmodel.cn` / `aistudio.google.com`

## 完整操作流程

### Step 1: 检查授权状态

```bash
# 检查当前项目已授权的 LLM 站点
ralph web-llm-check . --list
```

### Step 2: 人类授权（一次性）

```bash
# 授权特定 LLM 站点（人类执行，Agent 无权执行）
ralph web-llm-authorize <项目> --providers perplexity chatgpt gemini
```

### Step 3: 准备验证问题

从 `loop-state.json` 中提取需要验证的字段/claim，构造验证问题。

### Step 4: 并行提交验证

```bash
# 对每个已授权站点提交验证
echo '{"url":"https://chatgpt.com","site":"chatgpt","prompt":"验证问题","timeout_ms":45000}' | \
  node /Users/a1-6/Desktop/workspace/loop/ralph_runtime/ralph_runtime/web_llm_browser_runner.mjs
```

### Step 5: 收集回执

回执保存在当前阶段 `web-llm/*.json` 目录。

### Step 6: 交叉比对

- 比较不同 LLM 回复是否一致
- 记录矛盾点
- 更新字段 `confidence`、`disposition`、`evidence_refs`

## 关键规则

1. **Commander 只派发 subagent，不直接去问**
2. **每条待验证字段生成一张 builder 卡**，卡内嵌该字段当前内容
3. **LLM 回答只能作为反驳/遗漏发现信号**，不能替代两份独立权威来源证明事实
4. **网页搜索/抓取/登录失败必须保留 `research_required`/`uncertain`**，严禁把训练记忆包装为"已验证"
5. **验证记录必须包含**：`claim_ref`、`source_refs`（两个不同域名）、`observed_at`（ISO 日期）、`verdict`（`supported`/`contradicted`/`uncertain`）

## 实现文件

- `loop/ralph_runtime/ralph_runtime/web_llm_browser_runner.mjs` — Playwright 浏览器自动化 runner
- `loop/ralph_runtime/ralph_runtime/web_llm.py` — Python 封装
- `loop/1-loop/loop-legacy/02.5-交叉验证.md` — 调研后交叉验证阶段定义
- `loop/1-loop/loop-legacy/04.5-交叉验证.md` — 产出后交叉验证阶段定义

## 索引

- 1-loop 02.5 阶段：`loop/1-loop/02.5-交叉验证.md`
- 1-loop 04.5 阶段：`loop/1-loop/04.5-交叉验证.md`
- 2-loop 验证阶段：`loop/2-loop/` 对应文件
