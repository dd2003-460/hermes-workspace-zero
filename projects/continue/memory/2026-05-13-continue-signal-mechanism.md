# 信号文件 IPC 机制

**日期**: 2026-05-13
**状态**: ✅ 已实现

## 实现细节

### Hook Handler (`~/.hermes/hooks/continue/handler.py`)

- 从 hook context 获取 response、transcript_path、session_key
- 检查完成关键词（COMPLETE/DONE/任务已完成）
- 检查 max_iterations
- 条件不满足时写入信号文件

### Gateway 补丁 (`gateway/run.py`)

**注入点**: line 10702（agent 完成后，pending message 检查前）

**关键修改**:
- 检查 `~/.hermes/continue-signals/` 目录
- 读取信号文件内容并注入 `pending`
- 修正 `pending = None` 覆盖 bug（line 10724）

### 信号文件规范

```
路径: ~/.hermes/continue-signals/signal-{md5(session_key)[:12]}.txt
内容: "{timestamp}:{prompt}"
```

## 验证

```bash
# 验证 hook handler 语法
python3 -c "import sys; sys.path.insert(0, '~/.hermes/hooks/continue'); import handler; print('OK')"

# 验证 run.py 编译
python3 -c "compile(open('/Users/a1-6/.hermes/hermes-agent/gateway/run.py').read(), 'run.py', 'exec'); print('OK')"
```

## 下一步

1. 配置 config.yaml 启用 continue
2. 实际测试 agent 自动循环
3. 监控 _MAX_INTERRUPT_DEPTH 递归限制
