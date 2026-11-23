# 步骤 5：清理

## 目标
清理临时文件和遗留目录，保持环境整洁。

## 涉及文件
- `~/Library/Application Support/dsh-desktop/harness/.agent-presets/loop/`（遗留目录，删除）
- `~/Library/Application Support/dsh-desktop/harness/.agent-presets/.loop-backup-2026-11-18/`（备份目录，保留）
- `/tmp/dsh-asar/`（临时解压目录，删除）

## 做法
1. 删除遗留的 `.agent-presets/loop/` 目录（0.14.0 不再读取此格式）
2. 保留 `.loop-backup-2026-11-18/` 备份目录（原始 legacy preset 备份）
3. 删除 `/tmp/dsh-asar/` 临时解压目录

## 验收标准
- `.agent-presets/loop/` 目录不存在
- `.loop-backup-2026-11-18/` 目录存在（备份保留）
- `/tmp/dsh-asar/` 目录不存在
