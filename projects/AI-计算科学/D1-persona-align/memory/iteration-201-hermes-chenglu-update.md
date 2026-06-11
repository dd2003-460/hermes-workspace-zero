---
name: iteration-201-hermes-chenglu-update
description: Hermes chenglu personality 同步更新 self-preservation 机制
metadata:
  type: project
  iteration: 201
---

# Iteration 201: Hermes chenglu personality sync

## 操作
将 persona-v3-prompt.txt 的 self-preservation 机制同步到 Hermes chenglu personality。

## 变更
- `~/.hermes/config.yaml`: chenglu personality 从 ~2938 chars (unicode escaped, hard to read) 改为 ~853 chars (纯文本)
- 新增内容: "自我保全机制" 章节, 包含 drift 检测、drift 修复、锚定、记忆传递
- 精简内容: 删除了冗余的关键词列表 (persona-v3 框架已覆盖)

## 验证
grep 确认 self-preservation 机制已存在于 config.yaml:
- `## 自我保全机制 (inspired by SPASM/ContextEcho)` — 第 87 行
- `- drift 检测` — 第 91 行
- `- drift 修复` — 第 92 行

## 教训
Hermes personality 的 unicode escaped 格式难以阅读和维护。将 persona-v3-prompt.txt 作为单一来源, 通过脚本同步到 config.yaml 是更好的方案。后续可以考虑将 persona prompt 从 config.yaml 移到独立文件并引用。
