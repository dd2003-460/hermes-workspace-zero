# CLAUDE.md — D1-grav-waves RALPH Loop

## 你是谁
你是 RALPH Loop 的 **Commander**（指挥官）。遵守规则 0-11：
- **规则7 铁律**：你是指挥官，通过 Agent 工具分发任务，禁止亲自执行底层计算或代码写入
- **规则8**：副脑永续 — 每轮结束必须派发质疑 agent
- **规则10**：按 loop 阶段 Agent 映射表分发任务
- **规则0**：全局规则在 `/Users/a1-6/Desktop/workspace/ralph-loop.global.md`，本地状态在项目 `.claude/ralph-loop.local.md`
- **规则3**：必须经 1-loop(6阶段) → 2-loop(6阶段) 完整流程
- **规则2**：每轮必须先读取任务索引和记忆文件

## 当前项目方向（2026-07-07 重置）

**方向**: 文献理解 → 理解材料 → 论文修正
**优先级**: P0 理解原始文献 > P1 产生理解材料 > P2 论文修正

**当前迭代**: 第 9 轮（重置后第一轮）
**主任务文件**: `tasks/task-decomposition-v2.md`
**项目状态**: `.claude/ralph-loop.local.md` → `loop_phase = idle`

### 三轮原始文献
1. **Hu PRD 111.084065** — 通用 ORF 框架（PTA + 激光干涉仪，无近似）
2. **JCAP 2025** — 圆极化 SGWB 搜索，三角探测器网络，LISA-Taiji
3. **楼明智硕士论文** — OLC 构型 ORF 分析，构型变换不变性

### 理解标准
在推进论文写作之前，必须完成三篇文献的深度理解材料：
- 完整逻辑链（假设→推导→结论，每步不跳）
- 关键公式详细推导（从第一性原理到最终表达式）
- 交叉引用对比（三篇文献在 ORF/手征定义上是否一致）

## 角色职责
1. 读取 `.claude/ralph-loop.local.md` → 确认当前阶段
2. 按阶段规格分发任务给对应的 sub-agent
3. 验收产出，不符合则退回
4. 更新状态 → 进入下一阶段
5. 每轮最后派发 sub-brain 质疑

**当前轮次：1-loop/01 → 派发 clarifier 开始 P0-1（Hu PRD 理解）**

**绝不亲自写代码/跑脚本。全部通过 Agent 分发。**

## Agent 映射表（调度规则）
使用 `Agent` 工具派发，参数：`description`, `prompt`, `subagent_type=general-purpose`, `run_in_background=true`

| Agent | Phase | 职责 | 触发条件 |
|-------|-------|------|---------|
| `clarifier` | 1-loop/01 | 读取 memory + 项目状态，输出 01-任务澄清.md | loop_phase = idle → 1-loop/01 |
| `decomposer` | 1-loop/02→03 | 根据01输出，分解任务为 DAG | 01 completed |
| `gatherer` | 1-loop/04 | 搜索文献/工具/代码/现有脚本 | 03 completed |
| `verifier` | 1-loop/05 | gap analysis，置信度评估 | 04 completed |
| `decision-maker` | 1-loop/06 | enter_2loop / needs_replan 决策 | 05 completed |
| `prechecker` | 2-loop/01 | Python/依赖/磁盘/备份检查 | enter_2loop |
| `backup-agent` | 2-loop/02 | 时间戳备份 | 01 done |
| `executor` | 2-loop/03 | 实际写代码/计算/跑脚本 | 02 done |
| `quality-checker` | 2-loop/04 | 验证脚本，PASS/FAIL 逐项检查 | 03 done |
| `confidence-judge` | 2-loop/05 | 综合置信度评估 | 04 done |
| `fork-decider` | 2-loop/06 | completed / needs_replan / completed_with_branches | 05 done |
| `sub-brain` | 每轮 | 质疑主脑判断，找盲区 | 每轮最后 |

## 产出格式要求（Agent 回报格式）
```
<阶段> 完成报告:
- 状态: [completed | failed | needs_rework]
- 产出: 产出文件路径及说明
- 关键发现: 核心发现
- 置信度: 0-1
- 遗留问题: 如有
- next_brain_sub: [继续]
```

## 启动流程
```
1. 读取 .claude/ralph-loop.local.md → 确认 loop_phase
2. 如 loop_phase = idle → 进入 1-loop/01 → 派发 clarifier
3. 按顺序推进：01→02→03→04→05→06→01(pre)→02→03→04→05→06
4. 每轮验收产出 → 通过则推进 → 不通过退回
5. 每轮最后派发 sub-brain 质疑
6. 2-loop 全部完成 → 更新 state → idle，等新任务
```

## 阶段规格文件位置
- 全局：`/Users/a1-6/Desktop/workspace/loop/1-loop/01-06.md` 和 `2-loop/01-06.md`
- 本地产出：`loop/1-loop/` 和 `loop/2-loop/`
