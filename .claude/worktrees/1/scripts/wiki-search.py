#!/usr/bin/env python3
"""wiki-search: 轻量级 wiki 搜索工具（无需外部依赖）

支持：
    - 关键词搜索（grep-like，但结构化输出）
    - TF-IDF 近似排序
    - 导出为可迁移格式

用法：
    python3 wiki-search.py search "范畴论"
    python3 wiki-search.py export
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter

WIKI_ROOT = Path(__file__).parent.parent / "wiki"

def scan_files():
    """扫描所有 .md 文件"""
    files = []
    for md_file in WIKI_ROOT.rglob("*.md"):
        if md_file.name in ("index.md", "log.md", "SCHEMA.md"):
            continue
        files.append(str(md_file.relative_to(WIKI_ROOT)))
    return sorted(files)

def read_file(path):
    """读取文件内容"""
    full_path = WIKI_ROOT / path
    if not full_path.exists():
        return ""
    return full_path.read_text(encoding="utf-8")

def tokenize(text):
    """简单分词（中文按字符，英文按单词）"""
    # 保留中文字符和英文单词
    words = re.findall(r'[\u4e00-\u9fff]|[a-zA-Z]+', text.lower())
    return words

def compute_tfidf(files):
    """计算简单 TF-IDF"""
    # 文档频率
    doc_freq = Counter()
    for path in files:
        content = read_file(path)
        tokens = set(tokenize(content))
        doc_freq.update(tokens)
    
    # IDF
    n_docs = len(files)
    idf = {term: (n_docs / freq) for term, freq in doc_freq.items()}
    
    # TF-IDF 向量（简化：只保留最高分）
    tfidf = {}
    for path in files:
        content = read_file(path)
        tokens = tokenize(content)
        tf = Counter(tokens)
        
        # 计算每个词的 TF-IDF 分数
        scores = {}
        for term, count in tf.items():
            if term in idf:
                scores[term] = (count / len(tokens)) * idf.get(term, 1)
        
        tfidf[path] = scores
    
    return tfidf

def search(query, top_k=5):
    """搜索 wiki 文件"""
    files = scan_files()
    if not files:
        print("没有 wiki 文件。")
        return
    
    query_terms = set(tokenize(query))
    if not query_terms:
        print("查询为空。")
        return
    
    tfidf = compute_tfidf(files)
    
    # 计算每个文档的查询匹配分数
    results = []
    for path, scores in tfidf.items():
        score = sum(scores.get(term, 0) for term in query_terms)
        if score > 0:
            results.append((path, score))
    
    # 按分数排序
    results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n搜索结果（查询：'{query}'）:")
    print("-" * 60)
    
    for path, score in results[:top_k]:
        content = read_file(path)
        # 提取第一行作为标题
        title = content.split('\n')[0].replace('# ', '').strip() or path
        
        # 提取匹配上下文
        lines = content.split('\n')
        context_lines = []
        for line in lines:
            if any(term in line.lower() for term in query_terms):
                context_lines.append(line.strip())
        
        print(f"\n  [{score:.2f}] {title}")
        print(f"      路径：{path}")
        if context_lines:
            for ctx in context_lines[:3]:
                print(f"      → {ctx}")

def export():
    """导出为可迁移格式"""
    files = scan_files()
    
    export_data = {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "files": []
    }
    
    for path in files:
        content = read_file(path)
        export_data["files"].append({
            "path": path,
            "content": content[:5000],  # 限制大小
            "title": content.split('\n')[0].replace('# ', '').strip() if content else path
        })
    
    export_path = WIKI_ROOT.parent / "wiki_export.json"
    export_path.write_text(json.dumps(export_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已导出到: {export_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python3 wiki-search.py [search <query>|export]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "search":
        if len(sys.argv) < 3:
            print("用法：python3 wiki-search.py search <query>")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        search(query)
    elif cmd == "export":
        export()
    else:
        print(f"未知命令：{cmd}")
        sys.exit(1)
