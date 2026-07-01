# Loop Agents 索引

## 映射规则

每个 agent 对应一个 loop 阶段。agent 的 prompt 中必须包含：
1. **全局阶段规格** — 按哪个 md 文件执行
2. **输入文件** — 项目中对应阶段的本地产出（上一阶段的输出）
3. **输出文件** — 本项目中应写入的本地产出

## Agent 映射表

| Agent | 编号 | 代号 | Loop 阶段 | 角色 |
|------|------|------|-----------|------|
| Leader | - | - | 团队指挥官 | 调度、分配任务、验证门禁 |
| Brain-Sub | - | brain-sub | 副脑（永续） | 质疑主脑决策、找盲区 |
| Agent | 01 | clarifier | 1-loop/01-任务澄清 | 将模糊需求转化为结构化任务定义 |
| Agent | 02 | visionary | 1-loop/02-目标澄清 | 定义目标与边界，产出目标说明书 |
| Agent | 03 | decomposer | 1-loop/03-任务分解 | 将目标拆解为可执行子任务 |
| Agent | 04 | researcher | 1-loop/04-信息搜集 | 搜索 arXiv/Web 搜集技术信息 |
| Agent | 05 | auditor | 1-loop/05-完备核验 | 检查任务分解的完备性，找遗漏 |
| Agent | 06 | decision-maker | 1-loop/06-决策 | 综合前后阶段信息，决定 1→2 |
| Agent | 07 | pre-checker | 2-loop/01-pre-check | 检查 2-loop 执行前提条件 |
| Agent | 08 | backup-ops | 2-loop/02-backup | 执行前备份，生成变更清单 |
| Agent | 09 | executor | 2-loop/03-execute | 执行修改、编写代码/脚本 |
| Agent | 10 | verifier | 2-loop/04-verify | 验证产出是否符合预期 |
| Agent | 11 | confider | 2-loop/05-confidence | 计算置信度，识别不确定项 |
| Agent | 12 | final-decider | 2-loop/06-decision | 综合验证结果，决定是否结束 |

## 启动规则

- **串行**：agent 01→02→03→04→05→06 必须串行（1-loop 的依赖链）
- **并行**：04和05可以并行（各自依赖不同输入：04依赖03，05依赖03+04）
- **启动**：leader 按 INDEX 映射创建 sub-agent，附上全局路径和本项目路径

## 每个本地阶段文件的模板格式

每个项目中的 `loop/1-loop/XX-xxx.md` 或 `loop/2-loop/XX-xxx.md` 必须包含：

```markdown
# [阶段编号]: [阶段名称]

**所属规格**：[指向全局loop/xx.md的路径]
**状态**：pending | in_progress | completed
**输入**：[上一步的本地文件路径]
**输出**：[本阶段的产出]

---
## 产出内容
[具体产出 — 按全局规格文件的输出格式]

---
## 完成时间
[last_completed_at]

---
## 回滚
[如果失败如何回到上一步]
```
