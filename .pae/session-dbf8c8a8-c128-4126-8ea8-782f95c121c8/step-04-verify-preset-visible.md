# 步骤 4：验证 preset 可见

## 目标
确认 "Loop 配方模式" preset 在 DSH Desktop 的 preset picker 中可见且可激活。

## 涉及文件
- DSH Desktop GUI（preset picker 界面）
- `~/Library/Logs/DSH Desktop/harness.log`（日志验证）

## 做法
1. 在 DSH Desktop 中打开 preset picker（新会话或设置界面）
2. 查找 "Loop 配方模式" 选项
3. 选择该 preset 创建新会话
4. 检查 harness.log 确认 preset 激活成功

## 验收标准
- preset picker 中显示 "Loop 配方模式"
- 选择该 preset 后无错误
- harness.log 无 `preset-loop` 相关的 activation 错误
- 新会话正常启动（无 session-error）
