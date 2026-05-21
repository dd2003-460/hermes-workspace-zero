# D1-continuous-agent — Agent 持续循环机制研究

**状态**: 初始研究阶段
**创建**: 2026-05-13
**方向**: agent 系统如何实现不间断持续工作

---

## 项目目标

**核心机制**：
当 agent **完全停止**（没有工具运行、没有子 agent、没有命令在跑）时，stop hook 拦截退出事件，注入同一个 session 中预设的 prompt，保证 agent 工作不间断。

**关键约束**：
- 只在 agent 真正空闲时触发（不能打断正在执行的工具/命令）
- 注入的是同一个 session（不是新建会话）
- 工作流：agent 完成 → 空闲 → hook 拦截 → 注入 prompt → agent 继续

**具体目标**：
1. 完整理解 Claude Code stop hook 机制（含 stop-hook.sh 完整流程）
2. Hermes 上能否获得等效能力
3. 持续迭代，对标业界最佳实践

---

## 文件结构

```
D1-continuous-agent/
├── INDEX.md                  # 本文件
├── memory/                   # 探索记录（不可删除）
├── notes/                    # 分析笔记、对比研究
│   ├── 01-stop-hook-analysis.md  # Claude Code Stop Hook 机制分析（已有）
│   └── 02-hermes-gateway-hooks.md  # Hermes Gateway Hooks 系统发现（agent:end）（新增）
└── tasks/                    # 任务状态
```

---

## 递归索引

见各子目录 `INDEX.md`。
