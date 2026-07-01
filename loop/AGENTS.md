# RALPH Loop Agent 团队规范

## 全局约束
- 规则参考: `/Users/a1-6/Desktop/workspace/ralph-loop.global.md`
- 规格文件: `/Users/a1-6/Desktop/workspace/loop/`
- 项目本地: `<project>/.claude/ralph-loop.local.md` + `<project>/loop/`

## Agent 模板

所有 Agent 按统一模板被指挥官（Claude Code 主会话）派发任务。

### 派单格式（指挥官 → Agent）

```
Agent briefing:
- phase: <阶段，如 1-loop/01-任务澄清>
- goal: <一句话描述本轮任务>
- 输入文件:
  - <文件路径1>: <说明>
  - <文件路径2>: <说明>
- 输出要求:
  - <文件路径>: <格式要求>
  - ...
- 验证标准:
  - <条件1>
  - ...
- 约束:
  - <规则/限制>
  - ...
```

### 回报格式（Agent → 指挥官）

```
<阶段> 完成报告:
- 状态: [completed | failed | needs_rework]
- 产出:
  - <文件>: <内容说明>
- 关键发现:
  - <发现1>
  - ...
- 置信度: <0-1之间的数值，如有疑问标低>
- 遗留问题:
  - <问题1>
  - ...
- next_brain_sub: [继续] — 副脑每轮必须输出此标记
```

### 回滚请求格式（指挥官 → Agent）

```
退回修正:
- 原因: <为什么需要修正>
- 修正方向: <怎么改>
- 输入文件: <不变或更新>
- 输出: <按原要求重新产出>
```

## 指挥官守则

1. **每次只派一个 Agent**：按 loop 顺序，一轮一轮来
2. **验收再推进**：Agent 回报后检查产出是否符合规格，不符合就退回
3. **不要亲自写代码**：即使紧急，也只派发，不越俎代庖
4. **每轮派副脑**：在 Agent 完成后，给 brain-sub 派发质疑任务
5. **更新状态**：Agent 验收通过后，更新 local state 的 loop_phase

## 工作流示例

### 1-loop 执行序列
```
指挥官: 读 local state → 知道当前是 1-loop/01
指挥官: → agent: clarifier, briefing: 读取memory + 项目状态, 输出01-任务澄清.md
代理回报
指挥官: 验收 → OK → 推进到 1-loop/02
指挥官: → agent: decomposer, briefing: 根据01澄清结果, 输出02-03文件
... 直到 1-loop 全部完成
指挥官: → decision-maker, 06-决策 → enter_2loop
指挥官: 更新 local state 到 2-loop/01
... 2-loop 同理
```

## 常见错误

| 错误 | 修复 |
|------|------|
| 指挥官自己写代码 | 改派给 executor agent |
| 跳过阶段顺序 | 严格按 local state 的 loop_phase 推进 |
| 用 general-purpose 代替专用 agent | 使用符合角色职责的 agent |
| 不验收就推进 | 必须检查产出文件内容再推进 |
| 不派副脑 | 每轮最后必须派 brain-sub |
