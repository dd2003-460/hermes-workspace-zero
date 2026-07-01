# Agent 角色说明

| Agent 编号 | 代号 | Loop 阶段 | 角色职责 |
|------------|------|-----------|----------|
| 01 | clarifier | 1-loop/01-任务澄清 | 将模糊需求转化为结构化的任务定义 |
| 02 | visionary | 1-loop/02-目标澄清 | 定义目标与边界，产出目标说明书 |
| 03 | decomposer | 1-loop/03-任务分解 | 将目标拆解为可执行子任务 |
| 04 | researcher | 1-loop/04-信息搜集 | 搜索 arXiv / Web 搜集技术信息 |
| 05 | auditor | 1-loop/05-完备核验 | 核验任务分解的完备性，找遗漏 |
| 06 | decision-maker | 1-loop/06-决策 | 综合前后阶段信息，作出 1→2 决策 |
| 07 | pre-checker | 2-loop/01-pre-check | 检查 2-loop 执行前提条件 |
| 08 | backup-ops | 2-loop/02-backup | 创建执行前备份，生成变更清单 |
| 09 | executor | 2-loop/03-execute | 执行具体修改、编写脚本、编译等 |
| 10 | verifier | 2-loop/04-verify | 验证执行结果是否符合预期 |
| 11 | confider | 2-loop/05-confidence | 计算置信度，识别不确定项 |
| 12 | final-decider | 2-loop/06-decision | 综合验证结果，决定是否结束 2-loop |
| - | brain-sub | 副脑（永续） | 每轮派发，质疑主脑决策，找盲区 |

## 文件结构

每个 agent 对应一个 `.md` 文件，定义其角色、职责和输入输出格式。
`leader.md` 是指挥官（主脑）的指令文件。
`INDEX.md` 是 agent 与 loop 阶段的映射表。

## 命名规范

- 代号用小写短横线命名（如 `clarifier.md`）
- 副脑：`brain-sub.md`（每轮必须派发给不同 agent）
