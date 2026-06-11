# Iteration 246-247: search_arxiv 全面改进 — 死代码修复 + 映射表扩大 + 多策略回退 + 速率限制

## 目标
修复 search_arxiv 严重 bug，建立健壮的泛化回退机制，覆盖所有 idea 文件 topic。

## 执行动作

### 1. Bug 修复: 死代码覆盖搜索结果 (iteration 246)
原代码中第 127 行 `entries = []` 清除了所有搜索结果的死代码块。
**修复**: 删除死代码，保留 try_search 的正确返回值。

### 2. 映射表扩展 (iteration 246)
- 新增 20 个 idea 文件常见主题映射
- 覆盖: CoT, 信道容量, 同调群, 反馈动力学, 选择偏差, 神经网络信息论等

### 3. 多策略泛化回退 (iteration 247)
实现 4 级策略链，避免所有未映射 topic 回退到同一 "large language model"：
- **Strategy 1**: 提取英文词 (如果 topic 含英文)
- **Strategy 2**: 取最后 2-3 个词 (中文分割)
- **Strategy 3**: 领域关键词映射 — 28 个中文领域 cue → 英文 arXiv 查询
  - 例如: "信息" → "information theory"; "学习" → "machine learning";
         "控制" → "control theory"; "反馈" → "feedback control";
         "同调" → "homology computational topology"
- **Strategy 4**: 多领域通用搜索 (large language model → transformer → ML → DNN)

### 4. 速率限制 (iteration 247)
- try_search 添加 `time.sleep(0.25)` 避免 arXiv API 429
- 超时从 15s 提高到 20s

## 验证

测试效果对比 (回退前 vs 回退后):
| Topic | 回退前 | 回退后 |
|-------|--------|--------|
| 控制类微扰 | LLM fallback | control theory → Control of a Rigid Wing... |
| 反馈动力学 | LLM fallback | feedback control → Feedback Optimization... |
| agent | LLM fallback | multi-agent RL → Survey of Multi-Agent... |
| 信息理论 | LLM fallback | information theory → Group Testing... |
| 已映射 topic | ✅ 精确匹配 | ✅ 精确匹配 |

## 影响

- search_arxiv 从"30 个映射 topic → LLM 通用回退"升级为"50 个精确映射 + 28 个领域回退 + 多策略泛化"
- 未映射 topic 的回退结果从千篇一律变为领域相关
- gap_filler --auto-cite 可用于任意 topic
