# D1-grav-waves 项目 Loop 目录概览

> 本目录按 `/Users/a1-6/Desktop/workspace/ralph-loop.global.md` 第 11 条规范维护。
> 全局 loop 规格文件：`/Users/a1-6/Desktop/workspace/loop/1loop.md` + `2loop.md`
> Agent prompts：`/Users/a1-6/Desktop/workspace/loop/1-loop-prompts/` + `2-loop-prompts/`

## 当前状态

**loop-state.json** 见 `loop-state.json` — iteration 21, loop_phase: IDLE
最后产出：桥梁论文 v17 终稿（iter19 BP-10 + iter20 BP-A + iter21 TASKS.md 清理），19页 0 errors，已归档

## 1-loop 产出（iter14 RALPH 重启）

| 阶段 | 文件 | 状态 | 最后更新 |
|------|------|------|---------|
| 01-任务澄清 | `1-loop/01-任务澄清.md` | completed (旧版, v13 提交任务) | 2026-07-01 |
| 02-桥梁论文信息搜集 | `1-loop/02-桥梁论文-信息搜集.md` | completed | 2026-07-14 |
| 03-桥梁论文任务分解 | `1-loop/03-桥梁论文-任务分解.md` | completed | 2026-07-14 |
| 06-决策 | `1-loop/06-决策.md` | completed (ENTER 2-LOOP, 旧版) | 2026-07-01 |

## 2-loop 产出

| 阶段 | 文件 | 状态 | 最后更新 |
|------|------|------|---------|
| 01-pre-check | `2-loop/01-pre-check.md` | completed (pre-check 通过) | 2026-07-01 |
| 02-backup | `2-loop/02-backup.md` | completed (备份就绪) | 2026-07-01 |
| 03-execute | `2-loop/03-execute.md` | completed (缺陷修复) | 2026-07-01 |
| 04-verify | `2-loop/04-verify.md` | completed (v18 编译 14 页 0 errors) | 2026-07-01 |
| 06-decision | `2-loop/06-decision.md` | completed (论文 ready for submission) | 2026-07-01 |

## 归档

| 目录 | 内容 |
|------|------|
| `archive-iter1-103/` | 迭代 1-103 的全部 loop 产出（旧版 6 阶段结构） |

## 回滚机制

- 回滚到特定迭代：从 `archive-iter1-103/` 恢复对应迭代的产出文件
- 回滚到 Restart 前：从 `archive-iter1-restart/` 恢复
- 论文源文件：`paper-archive/main-paper-v17.tex` 保留最终稳定版本
