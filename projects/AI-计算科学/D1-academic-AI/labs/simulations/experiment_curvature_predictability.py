#!/usr/bin/env python3
"""
S17 语言信息几何实验 2：曲率-可预测性相关性

假设：文本的"曲率"（D1-S17 理论）与可预测性负相关
曲率代理量 = surprisal variance（surprisal 的方差）
可预测性代理量 = entropy rate（熵率，越低越可预测）

数据：Project Gutenberg 公开文本
- Poetry sample: Shakespeare Sonnets
- Prose sample: Pride and Prejudice
"""

import sys
import json
import urllib.request
import numpy as np
from pathlib import Path
from collections import Counter
import re


def download_gutenberg(epub_id, cache_dir="labs/data/gutenberg"):
    """从 Project Gutenberg 下载文本"""
    cache_path = Path(cache_dir) / f"pg{epub_id}.txt"
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if cache_path.exists():
        return cache_path.read_text(errors="ignore")

    url = f"https://www.gutenberg.org/cache/epub/{epub_id}/pg{epub_id}.txt"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            text = response.read().decode("utf-8", errors="ignore")
        cache_path.write_text(text)
        return text
    except Exception as e:
        print(f"下载失败 {epub_id}: {e}")
        return None


def clean_text(text):
    """清理 Gutenberg 文本（去除项目头和尾，只保留正文）"""
    # 提取主要正文部分
    start = text.find("START OF THIS PROJECT GUTENBERG")
    end = text.find("END OF THIS PROJECT GUTENBERG")
    if start != -1 and end != -1:
        text = text[start:end]
    else:
        # 如果没有找到标记，尝试基于标题搜索
        title_match = re.search(r'CHAPTER I', text, re.IGNORECASE)
        if title_match:
            text = text[title_match.start():]

    return text


def tokenize(text):
    """简单分词：转小写，保留字母和标点"""
    text = text.lower()
    tokens = re.findall(r'[a-z0-9]+|[^a-z0-9\s]', text)
    return [t for t in tokens if t.strip()]


def compute_surprisal_distribution(tokens):
    """
    计算 surprisal 分布 H(i) = -log p(token_i | context)

    近似方法：用 trigram 概率估计
    """
    if len(tokens) < 3:
        return np.array([])

    trigram_counts = Counter()
    bigram_context = Counter()
    surpisals = []

    # 第一遍：统计所有 trigram 和 bigram 上下文
    for i in range(2, len(tokens)):
        w1, w2, w3 = tokens[i-2], tokens[i-1], tokens[i]
        trigram_counts[(w1, w2, w3)] += 1
        bigram_context[(w1, w2)] += 1

    # 第二遍：计算 surprisal
    for i in range(2, len(tokens)):
        w1, w2, w3 = tokens[i-2], tokens[i-1], tokens[i]
        context_count = bigram_context[(w1, w2)]
        if context_count > 0:
            prob = trigram_counts[(w1, w2, w3)] / context_count + 1e-10
            surprisal = -np.log2(prob)
            surpisals.append(surprisal)

    return np.array(surpisals) if surpisals else np.array([])


def compute_metrics(text, max_tokens=10000):
    """
    计算曲率和可预测性指标

    取前 max_tokens 个 token 避免过长时间处理
    """
    tokens = tokenize(text)[:max_tokens]

    if len(tokens) < 10:
        return None

    surprisal_arr = compute_surprisal_distribution(tokens)

    if len(surprisal_arr) == 0:
        return None

    # Vocabulary
    vocab = set(tokens)

    # Token probability distribution
    token_counts = Counter(tokens)
    probs = np.array([token_counts[t] / len(tokens) for t in vocab])
    probs = probs[probs > 0]

    # Shannon entropy rate (per token)
    entropy_rate = -np.sum(probs * np.log2(probs))

    return {
        "surprisal_mean": float(np.mean(surprisal_arr)),
        "surprisal_var": float(np.var(surprisal_arr)),  # Curvature proxy
        "entropy_rate": float(entropy_rate),
        "n_tokens": len(tokens),
        "n_vocab": len(vocab),
        "entropy_per_token": float(len(surprisal_arr) / len(tokens)),
        "vocab_ratio": float(len(vocab) / len(tokens)),
    }


def main():
    print("=== S17 语言信息几何实验 2：曲率-可预测性相关性 ===")
    print()

    # 下载文本（POETRY - 莎士比亚十四行诗，PROSE - 傲慢与偏见）
    print("正在下载 Project Gutenberg 文本...")

    poetry_id = "1041"  # Shakespeare's Sonnets
    prose_id = "1342"   # Pride and Prejudice

    poetry_text = download_gutenberg(poetry_id)
    prose_text = download_gutenberg(prose_id)

    texts = {}
    if poetry_text:
        texts["shakespeare_sonnets"] = clean_text(poetry_text)
    if prose_text:
        texts["pride_and_prejudice"] = clean_text(prose_text)

    print(f"已加载 {len(texts)} 个文本")
    print()

    print(f"{'Text Type':>25} | {'Tokens':>7} | {'Vocab':>5} | {'Surprisal Var':>14} | {'Entropy Rate':>13}")
    print("-" * 85)

    metrics = {}
    for name, text in texts.items():
        m = compute_metrics(text)
        if m:
            metrics[name] = m
            print(f"{name:>25} | {m['n_tokens']:>7d} | {m['n_vocab']:>5d} | {m['surprisal_var']:>14.4f} | {m['entropy_rate']:>13.2f}")

    # Correlation analysis
    print()
    print("=== 相关性分析 ===")

    if len(metrics) >= 2:
        keys = list(metrics.keys())
        curvature_vals = np.array([metrics[k]["surprisal_var"] for k in keys])
        entropy_vals = np.array([metrics[k]["entropy_rate"] for k in keys])

        # Pearson correlation
        correlation = np.corrcoef(curvature_vals, entropy_vals)[0, 1] if len(keys) >= 2 else 0
        print(f"曲率( surprisal 方差) vs 熵率: r = {correlation:.3f}")

        # Interpret S17 hypothesis
        # Higher curvature = lower predictability
        # We expect: surprisal_var correlates with entropy_rate
        # The sign depends on what the data shows
        if len(keys) >= 2:
            higher = keys[0] if metrics[keys[0]]["surprisal_var"] > metrics[keys[1]]["surprisal_var"] else keys[1]
            lower = keys[1] if higher == keys[0] else keys[0]
            print(f"\n曲率较高：{higher}（surprisal_var = {metrics[higher]['surprisal_var']:.4f}）")
            print(f"曲率较低：{lower}（surprisal_var = {metrics[lower]['surprisal_var']:.4f}）")
            print(f"\n假设：曲率反映文本的'不确定性'分布特征")
            print(f"      （注意：需要更多数据点验证与熵率的关系）")

    # Save results
    output = {k: metrics[k] for k in sorted(metrics.keys())}
    output_path = "labs/simulations/curvature_predictability_results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n数据已保存：{output_path}")


if __name__ == "__main__":
    main()
