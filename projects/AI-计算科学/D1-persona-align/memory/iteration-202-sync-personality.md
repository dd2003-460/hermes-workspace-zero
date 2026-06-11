---
name: iteration-202-sync-personality
description: sync_personality.py 自动同步脚本 + sp_section 行索引 bug 修复
metadata:
  type: project
  iteration: 202
---

# Iteration 202: sync_personality.py + self-preservation sync

## 操作

1. 创建 `scripts/sync_personality.py` 用于将 persona-v3-prompt.txt 同步到 Hermes config.yaml
2. 修复 `build_personality()` 中 `sp_section` 行索引 bug
3. 运行 sync 验证 self-preservation 正确同步到 Hermes

## Bug: sp_section 行索引

原始代码: `sp_lines = prompt_text.split("\n")[sp_start:]`
- `sp_start` 是 CHARACTER offset (1059)
- `split("\n")` 返回 LINES 数组
- `[1059:]` 试图跳过 1059 行, 而不是 1059 字符 → sp_lines 为空 → sp_section 为空

修复: 先找到 CHARACTER offset 对应的 LINE index, 再从该行开始取

## 同步结果

- `~/.hermes/config.yaml`: chenglu personality 已包含 self-preservation 机制
- `## 自我保全机制 (inspired by SPASM/ContextEcho)` 在配置文件第 87 行
- drift 检测、drift 修复、锚定、记忆传递 全部正确同步

## sync_personality.py 功能

- `--dry-run`: 只预览变更
- `--config path`: 指定 config 路径
- 自动备份 `.backup` 文件
- 比较 personality 后仅在变更时写入

## 教训

字符串偏移 (character offset) 和数组索引 (line index) 是不同的坐标系。split 后再取 slice 需要正确的坐标系转换。
