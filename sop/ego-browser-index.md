# ego-browser Skill Index

## 基本信息
- **Skill 名称**: `ego-browser`
- **版本**: 1.2.3 (本地) / 1.2.6 (GitHub 最新)
- **安装路径**: `~/.hermes/skills/ego-browser/`
- **GitHub**: https://github.com/citrolabs/ego-lite
- **文档**: https://lite.ego.app/document/
- **Stars**: 8894+

## 核心概念
1. **Task Space** — 每个 agent 有独立的隔离浏览空间，继承用户的登录状态
2. **Heredoc 执行** — 通过 `ego-browser nodejs <<'EOF' ... EOF` 执行 Node.js 脚本
3. **三种工作流**:
   - 语义工作流: `snapshotText()` + refs/locators (默认)
   - 视觉工作流: `captureScreenshot()` + 坐标操作 (canvas/富编辑器)
   - 直接 DOM/CDP: `js()` / `cdp()` (浏览器状态/数据提取)

## 常用命令
```bash
# 检查 ego-browser 是否可用
command -v ego-browser

# 基本使用
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('task name')
await openOrReuseTab('https://example.com', { wait: true })
cliLog(await snapshotText())
EOF

# 完成 task space
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('task name')
await completeTaskSpace(task.id, { keep: false })
EOF
```

## 关键注意事项
- `@N` refs 只在最近的 `snapshotText()` 调用中有效
- `js()` 返回的是评估结果，不是 JSON 字符串
- `cliLog()` 是 heredoc 中唯一的输出机制
- 每次 heredoc 执行后 Node.js 运行时退出，状态不保留
- 必须调用 `completeTaskSpace()` 关闭 task space
- 用户接管控制权时，agent 必须等待用户确认才能继续

## 相关文件
- `~/.hermes/skills/ego-browser/SKILL.md` — 主文档
- `~/.hermes/skills/ego-browser/references/install.md` — 安装指南
- `~/.hermes/skills/ego-browser/learnings/` — 学习记录 (github/google/x-com)
- `/Applications/ego lite.app/.../ego-skills/ego-browser/` — 应用捆绑资源
