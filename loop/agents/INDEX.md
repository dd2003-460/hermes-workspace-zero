# Loop Agents 索引

## 映射规则

每个 agent 对应一个 loop 阶段。agent 的 prompt 中必须包含：
1. **全局阶段规格** — 按哪个 md 文件执行
2. **输入文件** — 项目中对应阶段的本地产出（上一阶段的输出）
3. **输出文件** — 本项目中应写入的本地产出

## Agent 映射表

| Agent 编号 | Loop 阶段 | 全局规格文件 | 输入 | 本地输出 | 外部信息权限 |
|------------|-----------|-------------|------|----------|-------------|
| 01 | 1-loop 01-任务澄清 | `loop/1-loop/01-任务澄清.md` | project 下的 task-spec.md | 本项目 `loop/1-loop/01-任务澄清.md` | 无 |
| 02 | 1-loop 02-目标澄清 | `loop/1-loop/02-目标澄清.md` | 1-loop/01 产出 | 本项目 `loop/1-loop/02-目标澄清.md` | 无 |
| 03 | 1-loop 03-任务分解 | `loop/1-loop/03-任务分解.md` | 1-loop/02 产出 | 本项目 `loop/1-loop/03-任务分解.md` | 无 |
| 04 | 1-loop 04-信息搜集 | `loop/1-loop/04-信息搜集.md` | 1-loop/03 产出 | 本项目 `loop/1-loop/04-信息搜集.md` | arXiv WebSearch WebFetch |
| 05 | 1-loop 05-完备核验 | `loop/1-loop/05-完备核验.md` | 1-loop/03 + 1-loop/04 | 本项目 `loop/1-loop/05-完备核验.md` | arXiv 论文查询 |
| 06 | 1-loop 06-决策 | `loop/1-loop/06-决策.md` | 1-loop/05 产出 | 本项目 `loop/1-loop/06-决策.md` | 无 |
| 07 | 2-loop 01-pre-check | `loop/2-loop/01-pre-check.md` | 1-loop/06 产出 | 本项目 `loop/2-loop/01-pre-check.md` | 无 |
| 08 | 2-loop 02-backup | `loop/2-loop/02-backup.md` | 2-loop/01 产出 | 本项目 `loop/2-loop/02-backup.md` | Bash (cp/diff) |
| 09 | 2-loop 03-execute | `loop/2-loop/03-execute.md` | 2-loop/02 产出 | 修改后的文件 | Bash (运行脚本/测试) |
| 10 | 2-loop 04-verify | `loop/2-loop/04-verify.md` | 2-loop/03 产出 | 本项目 `loop/2-loop/04-verify.md` | Bash (运行测试) |
| 11 | 2-loop 05-confidence | `loop/2-loop/05-confidence.md` | 2-loop/04 产出 | 本项目 `loop/2-loop/05-confidence.md` | 无 |
| 12 | 2-loop 06-decision | `loop/2-loop/06-decision.md` | 2-loop/05 产出 | 本项目 `loop/2-loop/06-decision.md` | 无 |

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
