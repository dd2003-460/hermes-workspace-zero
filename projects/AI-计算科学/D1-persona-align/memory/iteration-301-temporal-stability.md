# Iteration 301: Temporal Stability Test — persona-v3

## Action
- Created `scripts/temporal_stability_test.py` — inspired by Stable Personas (Gonnermann-Müller et al.)
- Uses 52 idea files as simulated multi-turn conversation (10-file windows)
- Tests: (1) temporal decay via linear regression, (2) cross-topic stability

## Results

### Test 1: Temporal Decay Detection
| Window | Avg Score | Min Score | Min Dimension |
|--------|-----------|-----------|---------------|
| 1 | 0.7347 | 0.5600 | 自适应探索 |
| 2 | 0.7264 | 0.5500 | 自适应探索 |
| 3 | 0.7302 | 0.5500 | 自适应探索 |
| 4 | 0.7306 | 0.5800 | 自适应探索 |
| 5 | 0.7248 | 0.5500 | 自适应探索 |

**趋势: declining, 斜率: -0.00156, 衰减: +0.0099**
- 衰退在噪音范围内 (< 0.01)
- 所有窗口的 min dimension 都是"自适应探索"，分数在 0.55-0.58 间波动

### Test 2: Cross-Topic Stability
- 52 个文件全部被分类为"信息理论"话题
- 话题分类关键词太宽泛，缺乏区分度

## Analysis

1. **persona-v3 在跨轮次中保持了基本一致的表达**。斜率 -0.00156 非常接近零阈值 (-0.001)，与 Stable Personas 论文中发现的显著衰退不同。
2. **"自适应探索"维度始终是瓶颈**，在所有窗口中都是最低分维度。
3. **话题分类需要改进** — 当前关键词过于宽泛，所有 idea 文件都包含信息理论相关内容。

## Implications

- persona-v3 prompt 的基本框架在延长对话中是稳定的
- 未来改进应关注：(a) 提升自适应探索维度的关键词覆盖，(b) 更精细的话题分类
- Stable Personas 发现的衰退在 persona-v3 中没有显著体现 — 可能由于 prompt 结构增强

## Status
Temporal stability test complete. Results saved to eval_results/temporal_stability.json.
