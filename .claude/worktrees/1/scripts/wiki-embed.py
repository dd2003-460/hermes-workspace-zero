#!/usr/bin/env python3
"""wiki-embed: 从 wiki Markdown 文件生成向量嵌入，支持本地和迁移模式。

用法：
    python3 wiki-embed.py build          # 扫描所有 .md 文件并生成嵌入
    python3 wiki-embed.py search "范畴论" # 语义搜索
    python3 wiki-embed.py export         # 导出为可迁移格式

依赖：pip install sentence-transformers numpy
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

WIKI_ROOT = Path(__file__).parent.parent / "wiki"
EMBEDDINGS_DIR = WIKI_ROOT / "embeddings"

def scan_files():
    """扫描所有 .md 文件（排除 index.md, log.md, SCHEMA.md）"""
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

def generate_embeddings(files):
    """生成向量嵌入（需要 sentence-transformers）"""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
    except ImportError:
        print("需要安装 sentence-transformers: pip install sentence-transformers")
        sys.exit(1)

    embeddings = {}
    for i, rel_path in enumerate(files):
        content = read_file(rel_path)
        if not content.strip():
            continue
        
        # 简单分块（按段落）
        chunks = [c.strip() for c in content.split('\n\n') if c.strip()]
        chunk_embeddings = model.encode(chunks)
        
        embeddings[rel_path] = {
            "chunks": [c[:200] for c in chunks],  # 存储文本摘要
            "embedding_refs": [f"{i}_{j}" for j in range(len(chunks))],
            "model": "all-MiniLM-L6-v2"
        }
        
        if (i + 1) % 10 == 0:
            print(f"  处理 {i+1}/{len(files)}: {rel_path}")
    
    return embeddings

def save_embeddings(embeddings):
    """保存嵌入索引"""
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
    
    index = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "files": list(embeddings.keys()),
        "data": embeddings
    }
    
    index_path = EMBEDDINGS_DIR / "index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"嵌入索引已保存: {index_path}")

def build():
    """构建完整嵌入"""
    print("扫描 wiki 文件...")
    files = scan_files()
    print(f"找到 {len(files)} 个文件")
    
    if not files:
        print("没有可嵌入的文件。先创建一些 wiki 内容。")
        return
    
    print("\n生成向量嵌入...")
    embeddings = generate_embeddings(files)
    
    if not embeddings:
        print("没有有效内容可嵌入。")
        return
    
    save_embeddings(embeddings)
    print(f"\n完成！嵌入 {len(embeddings)} 个文件。")

def search(query, top_k=5):
    """语义搜索（需要已构建的嵌入）"""
    index_path = EMBEDDINGS_DIR / "index.json"
    if not index_path.exists():
        print("没有嵌入索引。先运行: python3 wiki-embed.py build")
        sys.exit(1)
    
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("需要安装 sentence-transformers")
        sys.exit(1)
    
    index_data = json.loads(index_path.read_text(encoding="utf-8"))
    model = SentenceTransformer(index_data["data"][list(index_data["data"].keys())[0]]["model"])
    
    query_vec = model.encode([query])[0]
    
    # 简单余弦相似度搜索
    results = []
    for rel_path, data in index_data["data"].items():
        chunks = data["chunks"]
        chunk_vecs = model.encode(chunks)
        
        similarities = [float(query_vec @ v / (numpy.linalg.norm(query_vec) * numpy.linalg.norm(v))) 
                       for v in chunk_vecs]
        max_sim = max(similarities) if similarities else 0
        
        results.append((rel_path, max_sim))
    
    results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n搜索结果（查询：'{query}'）:")
    print("-" * 60)
    for path, score in results[:top_k]:
        print(f"  [{score:.3f}] {path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python3 wiki-embed.py [build|search <query>]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "build":
        build()
    elif cmd == "search":
        import numpy
        if len(sys.argv) < 3:
            print("用法：python3 wiki-embed.py search <query>")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        search(query)
    else:
        print(f"未知命令：{cmd}")
        sys.exit(1)
