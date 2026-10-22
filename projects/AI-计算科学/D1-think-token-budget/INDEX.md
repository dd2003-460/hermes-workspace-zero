# D1-think-token-budget

思考 token 预算实验（qwen3-32b 基准 + 3 轮发现）。

## 结构

- memory/ — 基准数据与轮次发现（round1-3-findings, qwen3-32b-benchmarks, thinking-reduction-survey）
- tasks/ — 当前任务
- prompts/ — 实验 prompt
- results/ — 实验结果
- loop-state.json — 项目状态

## 状态

- complete: T1-T4 全完成, R3 前沿映射交付（P1=prompt 级前沿, 414.5ch/104tok 2.63x 短于 P0）
- 下一步候选: serving 层优化
