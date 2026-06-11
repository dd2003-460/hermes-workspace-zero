# Iteration 350: 语义评估集成 unified_eval.py — 相关性分析

## 背景

迭代 349 开发了语义匹配评估器。迭代 350 将其集成到 unified_eval.py pipeline。

## 变更

### unified_eval.py 新增功能

1. **`--semantic` 标志**: 同时运行语义评估
2. **`pearson_correlation()` 函数**: 计算 Pearson 相关系数
3. **文件级输出**: 每个文件新增 `semantic_scores` 字段
4. **对比输出**: 打印 Pearson 相关系数 + 均值对比 + 一致性警告

### 使用方式

```bash
# 仅关键词评估 (原有行为)
python3 scripts/unified_eval.py --scan

# 关键词 + 语义对比评估
python3 scripts/unified_eval.py --scan --semantic
python3 scripts/unified_eval.py --prompt --semantic
```

## 实验结果

### 真实会话响应对比 (n=3)

| 版本 | 关键词 avg | 语义 score |
|------|-----------|-----------|
| v1 | 0.2849 | 0.5011 |
| v2 | 0.1864 | 0.2763 |
| minimal | 0.0686 | 0.2281 |

**Pearson r = 0.9175** — 高度相关

### 解读

1. **高相关性验证**: 关键词评估是语义对齐的合理代理 (proxy)。当关键词得分高时，语义对齐度也高。

2. **绝对值差异有意义**: 语义评估给出更有意义的绝对值 — v1 响应即使只使用 prompt 的 15% 内容，仍达到 0.50 对齐度。

3. **假阴性场景**: 当关键词和语义评估显著不一致时 (低相关), 检测到的文件很可能是假阴性 — 关键词得分低但语义对齐度高。

4. **n=3 局限性**: 这个相关性仅在 3 个真实会话响应上计算。需要在 52 个 idea 文件上运行以验证整体趋势。

## 下一步

1. 在 52 个 idea 文件上运行 `--scan --semantic` — 验证大规模下的相关性
2. 识别假阴性文件 — 关键词低但语义高的文件
3. 更新 DIMENSION_KEYWORDS 以减少假阴性
