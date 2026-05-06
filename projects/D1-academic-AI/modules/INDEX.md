# modules/ — 可复用模块索引

## [M.1] cognitive_topology
D1-r02 认知拓扑映射模块

```python
from modules.cognitive_topology import char_hash
est = char_hash.CognitiveTopologyEstimator(n_dim=64, window=3)
result = est.full_analysis(text)
# → {"I_C": 3.33, "dIC_dt": 0.73, "T_cog": ...}
```

**文件**：`char_hash.py` — 字符哈希实现（零依赖）

**待扩展**：
- `bert_embed.py` — BERT 嵌入模式（需 pip install sentence-transformers）
