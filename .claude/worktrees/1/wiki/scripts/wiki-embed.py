#!/usr/bin/env python3
"""Wiki 向量检索基础设施

用法:
    python wiki-embed.py build      # 为所有 Markdown 文件生成 embedding
    python wiki-embed.py search "范畴论"  # 语义搜索

依赖: pip install sentence-transformers numpy
"""

import os
import json
import glob
import numpy as np
from pathlib import Path

EMBEDDINGS_DIR = Path(__file__).parent.parent / "embeddings"
WIKI_DIR = Path(__file__).parent.parent

def read_file(path):
    """读取 Markdown 文件内容"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def get_all_md_files():
    """获取 wiki 目录下所有 Markdown 文件"""
    md_files = []
    for root, dirs, files in os.walk(WIKI_DIR):
        # 跳过 embeddings 目录
        if 'embeddings' in root:
            continue
        for f in files:
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))
    return sorted(md_files)

def build_embeddings():
    """为所有 Markdown 文件生成 embedding"""
    from sentence_transformers import SentenceTransformer
    
    print("加载模型...")
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    os.makedirs(EMBEDDINGS_DIR / "vectors", exist_ok=True)
    
    index_data = []
    md_files = get_all_md_files()
    
    print(f"处理 {len(md_files)} 个文件...")
    for i, path in enumerate(md_files):
        content = read_file(path)
        rel_path = os.path.relpath(path, WIKI_DIR)
        
        # 生成 embedding（取前 512 字符避免过长）
        text = content[:512]
        embedding = model.encode(text, normalize_embeddings=True)
        
        # 保存向量
        vec_path = EMBEDDINGS_DIR / "vectors" / f"{i:04d}.npy"
        np.save(vec_path, embedding)
        
        index_data.append({
            "id": f"doc-{i:04d}",
            "path": rel_path,
            "embedding_ref": str(vec_path),
            "text_preview": content[:200].replace('\n', ' '),
        })
        
        if (i + 1) % 10 == 0:
            print(f"  已处理 {i + 1}/{len(md_files)}")
    
    # 保存索引
    index_path = EMBEDDINGS_DIR / "index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"完成！索引保存在 {index_path}")

def search_embeddings(query, top_k=5):
    """语义搜索"""
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    # 加载索引
    index_path = EMBEDDINGS_DIR / "index.json"
    if not index_path.exists():
        print("错误：索引不存在，请先运行 'build'")
        return
    
    with open(index_path, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    # 生成查询 embedding
    query_embedding = model.encode(query, normalize_embeddings=True)
    
    # 计算相似度
    scores = []
    for item in index_data:
        vec_path = EMBEDDINGS_DIR / item["embedding_ref"]
        if vec_path.exists():
            vec = np.load(vec_path)
            score = float(np.dot(query_embedding, vec))
            scores.append((score, item))
    
    # 排序取 top_k
    scores.sort(reverse=True)
    results = scores[:top_k]
    
    print(f"\n搜索结果（查询: '{query}'）:")
    print("-" * 60)
    for score, item in results:
        print(f"\n[得分 {score:.4f}] {item['path']}")
        print(f"  预览: {item['text_preview'][:100]}...")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python wiki-embed.py build      # 生成 embedding")
        print('  python wiki-embed.py search "查询词"')
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "build":
        build_embeddings()
    elif command == "search":
        if len(sys.argv) < 3:
            print("用法: python wiki-embed.py search \"查询词\"")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        search_embeddings(query)
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
