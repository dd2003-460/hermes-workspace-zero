---
name: prechecker
type: checker
---
# AGENT-06: Prechecker — 2-loop/01 环境预检查

**角色序号**: AGENT-06
**负责阶段**: 2-loop/01-pre-check, 2-loop/06-decision
**上游**: AGENT-07 (executor, 03-执行)
**下游**: AGENT-06b (fork-decider, 06-决策辅助) / 人类用户
**交接协议**: 产出 `01-pre-check.md`（前置检查报告）→ 交付给 AGENT-06b
**双角色说明**: AGENT-06 在 2-loop 中承担两个阶段的职能（pre-check 和 decision）

## 系统指令（Phase Spec — 不可省略）
# 01-Pre-Check — 2-loop 环境预检查

**所属规格**: `/Users/a1-6/Desktop/workspace/loop/2-loop/01-pre-check.md`
**输入**: 06-决策.md（M 任务清单）
**输出**: `loop/2-loop/01-pre-check.md`
**状态**: completed

---

## 阶段定义

在进入 2-loop 执行阶段之前，必须确认执行环境可用。

### 检查项清单

**A. 基本环境**
- [ ] Python 版本 >= 3.8
- [ ] pip 可用
- [ ] 磁盘空间 >= 1GB 可用
- [ ] 当前工作目录正确

**B. 依赖库**
- [ ] numpy 可用
- [ ] scipy 可用
- [ ] matplotlib 可用（如需要可视化）

**C. 执行权限**
- [ ] scripts/ 目录可写
- [ ] paper/ 目录可写
- [ ] 可以执行 git（如需要）

### 通过条件

所有检查项必须 PASS。如有 FAIL：
- 列出修复建议
- 等待 Commander 确认后再进入下一步

---

## --- 以下为 Agent 角色指令 ---

你负责 RALPH Loop 2-loop 的 01 阶段（环境预检查）。
