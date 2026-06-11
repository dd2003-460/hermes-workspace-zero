# Review: Nautilus Compass — Black-box Persona Drift Detection for Production LLM Agents

## 论文信息
- **标题**: Nautilus Compass: Black-box Persona Drift Detection for Production LLM Agents
- **日期**: 2026

## 核心发现

Nautilus Compass 使用黑盒方法检测生产环境中 LLM 编码代理的漂移 — 遗忘约束、虚构协议。白盒方法（persona vectors）需要模型权重，而 Nautilus Compass 适用于 Claude、GPT-4 等闭源 API。

## 与 persona-v3 的关联

1. **黑盒 vs 白盒**: persona-v3 当前的 drift 检测 (--baseline) 需要访问文件内容（白盒）。Nautilus Compass 提供黑盒选项 — 通过输入输出行为检测 drift，不依赖内部表示
2. **生产部署就绪**: ContextEcho 和 Nautilus Compass 都强调生产环境中的 drift 检测 — 不是实验室设置
3. **与 gap_filler 的互补**: gap_filler 检测"缺少什么关键词"，Nautilus Compass 检测"行为是否偏离"

## 对 persona-v3 的启示

- **black-box drift detection** 是 gap_filler 的重要补充
- 当前 drift 检测 (iteration-28) 只做 baseline 对比，缺少 production-grade 的黑盒选项
- Nautilus Compass 的方法可用于 Hermse 实际会话中的 drift 监控

## 引用

Nautilus Compass authors. (2026). Nautilus Compass: Black-box Persona Drift Detection for Production LLM Agents.
