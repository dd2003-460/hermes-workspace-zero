# Iteration 207: 修复 INDEX.md 和 TASKS.md 滞后信息

## 目标
修正项目入口索引文件 (INDEX.md, TASKS.md) 中的过时信息.

## 发现的问题

入口索引文件是项目的"第一层信息", 如果滞后会导致整个项目状态感知错误:

| 文件 | 旧信息 | 实际状态 | 差距 |
|------|--------|----------|------|
| INDEX.md 状态行 | "54 篇外部研究" | 60+ 篇 | 滞后 ~6 篇 |
| INDEX.md 任务 | "T1-T31" | T1-T40 | 滞后 9 个任务 |
| INDEX.md memory | "58+ iteration logs" | 77 个 | 滞后 ~19 个 |
| INDEX.md scripts | "6 个" | 25 个 | 缺失 19 个 |
| INDEX.md 脚本列表 | 仅 6 个 | 20+ 个 | 大量缺失 |
| TASKS.md persona-align | "T1-T26, 50 篇研究" | T1-T40, 60+ 篇 | 滞后 14 个任务 + 10 篇 |

## 执行过程

1. 更新 INDEX.md:
   - 状态行: persona-v3 完整描述 (8 原则 + 6 维度 + 3 行为约束) + T1-T40
   - 子目录计数: 77 个 iteration logs, 60+ 篇研究, 20+ 个脚本
   - 脚本列表重构: 按功能分组 (评估/监控/评估验证/生成验证)
   - 新增 sync_personality.py 和 persona_v3_batch_enhance.py
   - persona-v3-prompt.txt 更新描述: 加入 self-preservation
2. 更新 TASKS.md: persona-align 状态从 T1-T26 更新到 T1-T40

## 教训

- INDEX.md 和 TASKS.md 是入口级索引, 比迭代日志更需要及时更新
- 大型迭代周期中, 入口文件容易被忽略 — 因为它们不像迭代日志那样每次都要写
- 教训: 完成一个迭代周期的"大块工作"后, 必须回头更新入口索引
- 建议: 将入口索引更新加入迭代完成的"收尾检查清单"
