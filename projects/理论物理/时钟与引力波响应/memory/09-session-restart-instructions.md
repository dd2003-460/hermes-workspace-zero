# 会话重启指南 — D1-grav-waves RALPH Loop

## 核心机制

每个新的 Claude Code 会话启动时，**CLAUDE.md 自动加载**，注入完整 RALPH Loop 上下文。不需要手动导入规则。

## 启动流程（每次新 session）

```
1. Claude Code 自动加载 CLAUDE.md（项目根目录下）
2. CLAUDE.md 包含：
   - RALPH 规则（规则 0-11）
   - Agent 映射表
   - 当前项目状态（迭代号、已完成阶段、任务清单）
   - 已知问题（06-olc-lisa-mixed-network.py 的 4 个 bug）
   - 启动流程指引
3. Claude Code 自动读取 .claude/ralph-loop.local.md → 获知当前阶段
4. 按 loop_phase 开始执行：
   - idle → 进入 1-loop/01
   - 2-loop/01-pre-check → 直接开始环境检查
5. 使用 Agent 工具派发子任务给对应的 sub-agent
6. 每轮结束派发 sub-brain 质疑
7. 完成后更新 .claude/ralph-loop.local.md 进入下一阶段
```

## 验证启动完整性

```bash
# 在 session 中运行：
bash start-ralph-loop.sh status
```

这会输出：
- 全局规则是否存在
- 阶段规格文件是否完整
- 本地状态文件的当前阶段
- CLAUDE.md 是否加载
- 所有 Agent 定义是否就位
- 已有脚本完整性
- Python 环境可用性

## 重置状态

```bash
bash start-ralph-loop.sh reset
# 将 loop_phase 设为 idle，从头开始新一轮 1-loop
```

## 本地文件清单

| 文件 | 用途 | 加载方式 |
|------|------|---------|
| `CLAUDE.md` | RALPH 规则 + 项目状态 + Agent 映射 | 每次自动加载 |
| `.claude/ralph-loop.local.md` | 迭代状态 + 阶段进度 | 指挥官主动读取 |
| `.claude/agents/*.md` | 12 个 Agent 定义 | Claude Code 自动识别 |
| `loop/1-loop/*.md` | 1-loop 中间结果 | 按阶段读取 |
| `loop/2-loop/*.md` | 2-loop 中间结果 | 按阶段读取 |
| `memory/*.md` | 理论推导和科学结论 | 按需读取 |
| `scripts/*.py` | 已有代码和验证脚本 | 按需执行 |

## 当前状态摘要（从 local.md）

- **迭代**: 3
- **阶段**: 2-loop/01-pre-check（等待环境检查启动）
- **1-loop 3**: 全部完成，决策 enter_2loop
- **P0 任务**: 混合网络 (OLC+LISA/PTA) 交叉相关灵敏度分析
- **M 任务**: M1(修复06bug) → M2(空间OLC) → M3(对比分析) → M4(阈值扫描) → M5(验证) → M6(总结)
- **4 个已识别的 bug**: C1(维度不一致), C2(SNR公式), C3(gamma混淆), C4(概念错误)

## 快速参考：Agent 调度规则

1-loop（指挥官不执行，只派发）:
- `clarifier` → 01-任务澄清
- `decomposer` → 02-目标澄清 + 03-任务分解
- `gatherer` → 04-信息搜集
- `verifier` → 05-完备核验
- `decision-maker` → 06-决策

2-loop:
- `prechecker` → 01-pre-check（环境检查）
- `backup-agent` → 02-backup（备份）
- `executor` → 03-execute（实际执行，唯一写代码的 Agent）
- `quality-checker` → 04-verify（验证脚本）
- `confidence-judge` → 05-confidence（置信度）
- `fork-decider` → 06-decision（分叉决策）
- `sub-brain` → 每轮最后（质疑主脑）
