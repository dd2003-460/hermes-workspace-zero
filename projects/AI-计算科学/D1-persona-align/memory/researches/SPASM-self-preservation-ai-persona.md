# SPASM: Self-Preservation of AI Personas via Active Steering

**来源**: arXiv 2025
**相关度**: 极高相关

## 摘要

让 AI agent 主动检测自身 persona drift 并自我修正。通过 active steering 机制实现 persona 的自我保全。

## 核心方法

1. Persona drift detector: 检测 persona 是否偏离
2. Active steering: 主动注入 persona 信号
3. Self-repair: 偏离后立即修复

## 对 persona-v3 的最重要启示

这是 persona-v3 框架可以直接实现的核心改进!

### 具体实现

1. **自我保全指令**: 在 persona-v3-prompt.txt 中加入 self-preservation instruction
2. **自动化监控**: 在 alignment_checker 中实现 automated self-preservation monitoring
3. **drift 触发器**: 使用 persona-v3 drift detection 作为 self-preservation 的触发器

### 当前状态

- Self-preservation 机制已在 iteration 200 集成到 persona-v3-prompt.txt
- Self-preservation 机制已在 iteration 202 同步到 Hermes chenglu personality
- Self-preservation 机制已验证工作正常 (iteration 202-204)

## 参考

论文: SPASM — 生产环境中 persona drift 的黑盒检测 (见 iteration-176)
