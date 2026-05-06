# 2-loop 执行 sub 包装器

这是 execution 阶段的 wrapper，不是 2-loop 的全局标准层。
先读 `../prompt-template.md`，再读 `./README.md` 和这一层的执行规范。

## 读取顺序

1. `../prompt-template.md`
2. `./README.md`
3. `./2.1-backup.md`
4. `./2.2-test.md`
5. `./2.3-verify.md`
6. `./2.4-confidence.md`
7. `./2.5-task-stages.md`
8. `./2.6-execution.md`
9. `../PROJECT_STANDARDS.md`

## 这一层只负责什么

- 备份
- 执行
- 测试
- 验证
- 置信度判断
- 分叉决策
- 把 `../AGENTS.md` 的原则继续传给主脑和副脑

## 这一层不负责什么

- 不把自己当成 2-loop 的统一标准
- 不把模板当作产出
- 不把“我已经跑过”当作完成
- 不绕过验证直接标 completed

## 2-loop 特有要求

1. 先备份，再执行，再验证
2. 任何业务变更都要落在正确的项目目录
3. 验证不通过就退回 planning / rollback
4. 完成后默认回到 1-loop 复盘
5. 如果要派发执行 sub，本轮必须明确工作区和边界
6. 每轮都要提醒主脑和副脑继续读 `../AGENTS.md`
7. 提醒不能中断，不能因为进入执行就停掉原则传递

## 公共层（不可跳过）

读 `../prompt-template.md`，按它定义的核心规则执行：
1. agents + 步骤确认
2. 按索引读
3. 状态读写显式
4. 单任务路径
5. 结果和证据优先

## 提醒一致性

执行层和判断层一样，都要把提醒完整传下去：

- 主脑要提醒副脑
- 副脑要提醒主脑
- 两边都要继续读 `../AGENTS.md`
- 如果提醒链断了，先补提醒，再继续执行
