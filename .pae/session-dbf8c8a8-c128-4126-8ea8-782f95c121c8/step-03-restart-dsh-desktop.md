# 步骤 3：重启 DSH Desktop

## 目标
重启 DSH Desktop 使新的 profile patch 生效。

## 涉及文件
- DSH Desktop 应用（运行中进程）
- `~/Library/Logs/DSH Desktop/harness.log`（日志验证）

## 做法
1. 关闭 DSH Desktop 应用
2. 重新启动 DSH Desktop
3. 等待应用完全启动（约 10-30 秒）

## 验收标准
- DSH Desktop 进程运行中（`pgrep -f "DSH Desktop"` 返回 pid）
- harness.log 无新的 `session-error` 或 `unknown prompt variable` 错误
- harness.log 无 `preset-loop` 相关的 mount 错误
