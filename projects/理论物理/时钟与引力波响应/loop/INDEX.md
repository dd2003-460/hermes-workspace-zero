# 本地 Loop 目录 — 时钟与引力波响应项目

> 本目录按 `/Users/a1-6/Desktop/workspace/ralph-loop.global.md` 第 11 条规范维护。
> 全局 loop 规格文件：`/Users/a1-6/Desktop/workspace/loop/1loop.md` + `2loop.md`
> Agent prompts：`/Users/a1-6/Desktop/workspace/loop/1-loop-prompts/` + `2-loop-prompts/`

## 当前状态

**ralph-loop.local.md** 见 `.claude/ralph-loop.local.md`
最后产出：iter9 P24-p25-p3 完成（精确单天区匹配验证 + 结果表格图表 + 论文更新），51 页 PDF 编译通过

## 1-loop 产出

| 阶段 | 文件 | 状态 | 最后更新 |
|------|------|------|---------|
| 01-任务澄清 | `1-loop/01-任务澄清.md` + `01-任务澄清-p1-dedup.md` | completed | 2026-07-14 |
| 02-目标澄清 | `1-loop/02-目标澄清.md` | completed | 2026-07-14 |
| 03-任务分解 | `1-loop/03-任务分解.md` | completed (P1-P5, P23-P24-P3) | 2026-07-14 |
| 04-信息搜集 | `1-loop/04-信息搜集.md` | completed | 2026-07-14 |
| 05-完备核验 | `1-loop/05-完备核验.md` | completed | 2026-07-14 |
| 06-决策 | `1-loop/06-决策.md` | completed | 2026-07-14 |

## 2-loop 产出

| 阶段 | 文件 | 状态 | 最后更新 |
|------|------|------|---------|
| 01-pre-check | `2-loop/01-pre-check.md` | completed | 2026-07-14 |
| 02-backup | `2-loop/02-backup.md` | completed | 2026-07-14 |
| 03-execute | `2-loop/03-execute.md` | completed | 2026-07-14 |
| 04-verify | `2-loop/04-verify.md` | completed | 2026-07-14 |
| 05-confidence | `2-loop/05-confidence.md` | completed | 2026-07-14 |
| 06-decision | `2-loop/06-decision.md` | completed | 2026-07-14 |

## 归档

| 目录 | 内容 |
|------|------|
| `archive-iter1-103/` | 原始迭代 1-103 产出 |
| `archive-iter1-restart/` | RALPH Restart 后的中间迭代 |

## plan.md

| 文件 | 状态 |
|------|------|
| `plan-p23-p24-p3.md` | completed — P23-P24-P3 执行计划 |

## 回滚机制

- 回滚到特定迭代：从对应 `archive-*/` 恢复
- 备份文件：`2-loop/*.bak`（代码执行前备份）
- 论文源文件：`paper-archive/` 保留历史稳定版本
