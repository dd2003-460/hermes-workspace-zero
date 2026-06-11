"""
Cognitive Topology Module (D1-r02)

将耦合振荡器的拓扑方法映射到对话流分析。

使用方式：
    # 字符哈希模式（零依赖）
    from modules.cognitive_topology import char_hash

    # BERT 嵌入模式（需 pip install sentence-transformers）
    from modules.cognitive_topology import bert_embed

    estimator = char_hash.CognitiveTopologyEstimator()
    result = estimator.full_analysis(text)
"""

from modules.cognitive_topology import char_hash

__all__ = ['char_hash', 'bert_embed']
