# Iteration 243: --auto-cite 映射表扩展 — 30 个 topic

## 目标
扩大 search_arxiv 的中文→English topic 映射表，解决 iteration 242 中只支持 2 个 topic 的限制。

## 执行动作

### persona_v3_gap_filler.py 扩展
- en_keywords_map 从 2 个条目扩展到 30 个条目
- 覆盖 persona-v3 主题 (自适应精度, 贝叶斯推理, 跨域类比, 探索利用权衡等)
- 覆盖通用研究主题 (语言模型, 深度学习, 注意力机制, 强化学习, 思维链, 提示工程, 知识图谱等)

## 验证

对所有测试 topic 运行 search_arxiv:
```
自适应精度: 3 results (Quantum rate distortion...)
信息论: 3 results (Group Testing: An Information Theory Perspective...)
贝叶斯推理: 3 results (Navigating the State of Cognitive Flow...)
注意力机制: 3 results (Transformer-based Personalized Attention...)
思维链: 3 results (Understanding Reasoning in Chain-of-Thought...)
```

所有测试 topic 均返回结果。

## 影响

- search_arxiv 的 topic 覆盖从 2 扩展到 30
- persona-v3 的 gap_filler --auto-cite 可以覆盖绝大多数 idea 文件的主题
- 未来改进: 未映射 topic 的泛化回退 (提取英文关键词或提示用户手动指定)
