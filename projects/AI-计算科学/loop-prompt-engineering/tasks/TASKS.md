# D1-loop-prompt-engineering 任务

## 目标

将现有的 1-loop（规划）和 2-loop（执行）各阶段规格文件，重新设计为 **步骤化 AI 执行 prompt**。

核心问题：当前的规格文件（如 `1-loop/01-perstep.md`、`2-loop/01-perstep.md`）是面向人类的规则文档，阅读者有完整的 loop 上下文。而实际通过 Agent 工具调用的 AI 只收到一个 prompt，缺少：
- 每一步的具体操作指令
- 输入输出的精确路径和格式
- 失败时的处理流程
- 与前后的衔接关系

## 输入

- 全局规则：`/Users/a1-6/Desktop/workspace/ralph-loop.global.md`
- 1-loop 完整规格：`/Users/a1-6/Desktop/workspace/loop/1-loop.md`
- 1-loop 精简规格：`/Users/a1-6/Desktop/workspace/loop/1-loop/01-perstep.md`
- 2-loop 完整规格：`/Users/a1-6/Desktop/workspace/loop/2-loop.md`
- 2-loop 精简规格：`/Users/a1-6/Desktop/workspace/loop/2-loop/01-perstep.md`
- 现有 agent spec：`/Users/a1-6/Desktop/workspace/loop/agents/`（12 agents）
- 现有 agent prompt：`/Users/a1-6/Desktop/workspace/loop/agents/prompts/`（6 个 prompt）
- Agent INDEX：`/Users/a1-6/Desktop/workspace/loop/agents/INDEX.md`
- 科研 SOP：`/Users/a1-6/Desktop/workspace/loop/00-research-sop.md`

## 已知问题（来自现有 prompt）

- 现有 prompt 是 agent 规格文档，不是步骤化操作指令
- 没有精确的文件路径（使用 `<项目>/` 占位符）
- 没有明确的完成/失败判定条件
- 没有衔接说明（完成后谁来接手）
- 缺少人类确认门处理（UNCERTAIN 时如何触发）
- 缺少失败修复流程
- 与 global 规则不一致（global 引用不存在的文件路径）

## 产出

### 产出物 1：1-loop 各阶段步骤化 Prompt（6 个）

针对以下每个阶段，输出一份可直接注入 Agent 的 prompt：

1. **任务澄清** (clarifier) — 将模糊需求转化为结构化任务定义
2. **目标澄清** (visionary) — 定义目标与边界，产出目标说明书
3. **任务分解** (decomposer) — 将目标拆解为可执行子任务（产出 plan.md）
4. **信息搜集** (researcher) — 搜索 arXiv/Web 搜集技术信息
5. **完备核验** (auditor) — 检查任务分解的完备性，找遗漏
6. **决策** (decision-maker) — 综合前后阶段信息，决定 1→2

### 产出物 2：2-loop 各阶段步骤化 Prompt（6 个）

1. **预检** (pre-checker) — 检查 2-loop 执行前提条件
2. **备份** (backup-ops) — 执行前备份，生成变更清单
3. **执行** (executor) — 执行修改、编写代码/脚本
4. **验证** (verifier) — 验证产出是否符合预期
5. **置信度** (confider) — 计算置信度，识别不确定项
6. **最终决策** (final-decider) — 综合验证结果，决定是否结束

### 产出物 3：Prompt 模板规范

定义统一的 prompt 模板结构，每个阶段 prompt 必须包含：
- 身份声明（agent 是谁，对什么负责）
- 输入清单（精确文件路径 + 格式说明）
- 分步操作（Step N: 做什么，怎么做，做到什么程度）
- 输出清单（精确文件路径 + 格式要求）
- 验证条件（什么算完成，什么算失败）
- 失败处理（遇到 XX 情况应该怎么做）
- 衔接说明（完成后谁来接手，下一步是什么）

## 约束
- 输出必须使用中文（代码标识符和技术术语可用英文）
- 每个 prompt 应在 **4000 tokens 以内**
- 不能改变现有 loop 的业务逻辑，只做表达方式的转换
- **关键：prompt 必须引用实际文件路径，不是 global 中描述的路径**
- 使用精简版 loop 规格（01-perstep.md 和 01-规划.md）作为主要参考
- 参考现有 agents/prompts/*.md 了解当前 prompt 的问题所在

## 文件结构

所有产出放在：
```
projects/AI-计算科学/loop-prompt-engineering/
├── TASKS.md（本文件）
├── PROMPT-TEMPLATE.md（产出物3：统一模板）
├── 1-loop-prompts/
│   ├── 01-clarifier.md
│   ├── 02-visionary.md
│   ├── 03-decomposer.md
│   ├── 04-researcher.md
│   ├── 05-auditor.md
│   └── 06-decision-maker.md
├── 2-loop-prompts/
│   ├── 01-pre-checker.md
│   ├── 02-backup-ops.md
│   ├── 03-executor.md
│   ├── 04-verifier.md
│   ├── 05-confider.md
│   └── 06-final-decider.md
└── INCONSISTENCY-NOTES.md（global vs 精简版不一致说明）
```
