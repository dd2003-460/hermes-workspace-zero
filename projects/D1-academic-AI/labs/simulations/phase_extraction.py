#!/usr/bin/env python3
"""
D4-S18 r04: 策略相位提取协议
从 Agent 响应文本中提取相位表示 θ ∈ [0, 2π)
"""

import numpy as np
from scipy.spatial.distance import cosine

def extract_phase_from_response(response_text, reference_vectors=None,
                                 embedding_model="text-embedding-3-small"):
    """
    将 Agent 响应映射为相位角 θ

    Args:
        response_text: Agent 的文本输出
        reference_vectors: 预定义参考向量集合（可选）
        embedding_model: 文本嵌入模型

    Returns:
        theta: 相位角 (radians) in [0, 2π)
    """
    # Step 1: 获取文本 embedding
    # 使用 OpenAI text-embedding-3 或本地模型
    text_embedding = get_embedding(response_text, embedding_model)

    if reference_vectors is None:
        # 默认：使用固定参考方向
        # 基于语义分类构建参考向量空间
        reference_vectors = build_semantic_reference_space()

    # Step 2: 计算投影到参考空间
    # 将 embedding 投影到参考向量集合
    projections = np.array([cosine(text_embedding, ref) for ref in reference_vectors])

    # Step 3: 计算主投影角度
    # 使用两个主参考方向构建二维相位空间
    θ1 = np.arctan2(projections[1], projections[0])
    θ2 = np.arctan2(projections[3], projections[2])

    # Step 4: 线性组合得到相位角
    # θ = w1 * θ1 + w2 * θ2 + phase_offset
    weights = np.array([0.7, 0.3])  # 第一主成分权重更高
    theta = np.around(weights[0] * θ1 + weights[1] * θ2, decimals=6)

    # Step 5: 归一化到 [0, 2π)
    theta = np.mod(theta, 2 * np.pi)

    return theta, projections

def build_semantic_reference_space():
    """
    构建语义参考空间（基于常见讨论方向）
    """
    # 在后续实验中可通过数据拟合确定参考向量
    reference_terms = [
        "analytical", "creative", "critical", "descriptive",
        "evaluative", "prescriptive", "exploratory", "conclusive"
    ]
    return [get_embedding(term, "text-embedding-3-small")
            for term in reference_terms]

def get_embedding(text, model="text-embedding-3-small"):
    """
    获取文本 embedding（需集成实际 API）
    """
    import openai
    client = openai.OpenAI()
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return np.array(response.data[0].embedding)
