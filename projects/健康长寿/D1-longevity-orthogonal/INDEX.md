# D1-longevity-orthogonal — 寿命正交贡献排序（控制面）

研究主体在 GitHub 仓 `dd2003-460/longevity-orthogonal-contribution`（本地克隆 = `repo/`，独立 git 仓，commit+push 都在那里做）。
本文件夹只放 loop 状态与规划，不放研究内容。

| 路径 | 内容 |
|------|------|
| `loop-state.json` | loop 状态 + 当前 goal（goal 唯一事实源，五字段格式见 sop/goal-template.md §1） |
| `tasks/decomposition.md` | 当前规划：分解树 + 正交性核对 + 空缺清单 + 任务表（派发只执行表内条目） |
| `memory/` | 探索记录（只增不删） |
| `repo/` | 工作仓克隆。⚠️ 仓内 `data/`、`scripts/`、`factors/` 路径被 `verify_integrity.py` 与 `audit_instruments.py` 硬编码引用，不可移动 |

**仓库现状速览**（2026-10-28 一手核实）：
- 阶段 1（工具变量可得性实测，2026-10-21 并入 main）已完成：24 因子分级实测表 + 东亚轨双表并存
- 阶段 2（实际跑 MR）从未运行：缺 R≥4.2 环境 + OpenGWAS token；仓库目前不含任何本项目自算的因果估计
- 预注册稿 = `repo/docs/20_方法/阶段2分析计划.md`（停止规则/主结局/负对照阈值已锁死，改动必须记修订记录）
- 可执行版脚本 = `repo/scripts/stage2_mr.R`（门禁是 `gate_fail()` 硬门禁；写于无 R 环境，首用先 `--dry-run`）
- 阶段 2 A 级暴露 = 5 个（F01 戒烟 / F03 降压 / F04 他汀 / F08 减重 / F15 抑郁 blocked：nsnp 仅 10,000 截断版）