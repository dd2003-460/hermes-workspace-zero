# 步骤 1：备份 profile patch

## 目标
在修改 profile patch 前创建备份，确保可回滚。

## 涉及文件
- `~/Library/Application Support/dsh-desktop/harness/profiles/desktop/cordis.patch.yml`（源文件）
- `~/Library/Application Support/dsh-desktop/harness/profiles/desktop/cordis.patch.yml.bak-2026-11-18`（备份文件）

## 做法
1. 执行 `cp cordis.patch.yml cordis.patch.yml.bak-2026-11-18`
2. 验证备份文件存在且大小一致

## 验收标准
- 备份文件存在
- `diff cordis.patch.yml cordis.patch.yml.bak-2026-11-18` 无差异
