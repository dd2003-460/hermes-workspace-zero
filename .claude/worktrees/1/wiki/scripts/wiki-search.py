#!/usr/bin/env python3
"""Wiki 轻量搜索（无需外部依赖）

用法:
    python wiki-search.py search "范畴论"
    python wiki-search.py export      # 导出为 JSON（迁移用）
"""

import os
import json
import glob
import re
from pathlib import Path

WIKI_DIR = Path(__file__).parent.parent

def read_file(path):
    """读取 Markdown 文件内容"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def get_all_md_files():
    """获取 wiki 目录下所有 Markdown 文件"""
    md_files = []
    for root, dirs, files in os.walk(WIKI_DIR):
        if 'embeddings' in root or 'scripts' in root:
            continue
        for f in files:
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))
    return sorted(md_files)

def search_content(query):
    """关键词搜索"""
    md_files = get_all_md_files()
    results = []
    
    query_lower = query.lower()
    for path in md_files:
        content = read_file(path)
        rel_path = os.path.relpath(path, WIKI_DIR)
        
        # 简单关键词匹配（不区分大小写）
        if query_lower in content.lower():
            # 提取标题和匹配行
            lines = content.split('\n')
            title = lines[0].replace('# ', '').strip() if lines else rel_path
            
            # 找到匹配的行
            match_lines = []
            for i, line in enumerate(lines):
                if query_lower in line.lower():
                    match_lines.append(f"  L{i+1}: {line.strip()}")
            
            results.append({
                "path": rel_path,
                "title": title,
                "match_count": len(match_lines),
                "matches": match_lines[:5],  # 最多显示 5 行匹配
            })
    
    # 按匹配数排序
    results.sort(key=lambda x: x["match_count"], reverse=True)
    
    print(f"\n搜索结果（查询: '{query}'）:")
    print("-" * 60)
    for r in results:
        print(f"\n[{r['match_count']} 处匹配] {r['path']}")
        print(f"  标题: {r['title']}")
        for m in r["matches"]:
            print(m)
    
    return results

def export_wiki():
    """导出为 JSON（迁移用）"""
    md_files = get_all_md_files()
    export_data = []
    
    for path in md_files:
        content = read_file(path)
        rel_path = os.path.relpath(path, WIKI_DIR)
        
        # 提取标题
        lines = content.split('\n')
        title = lines[0].replace('# ', '').strip() if lines else rel_path
        
        # 提取标签（从 ## 相关概念 或 ## 状态 部分）
        tags = []
        in_tags_section = False
        for line in lines:
            if '## 相关概念' in line or '## 状态' in line:
                in_tags_section = True
            if in_tags_section and '[[[' not in line:
                # 简单提取标签
                pass
        
        export_data.append({
            "id": rel_path.replace('/', '-').replace('.md', ''),
            "path": rel_path,
            "title": title,
            "content": content,
        })
    
    export_path = WIKI_DIR / "wiki_export.json"
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"导出完成！保存在 {export_path}")
    return export_data

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print('  python wiki-search.py search "查询词"')
        print("  python wiki-search.py export")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "search":
        if len(sys.argv) < 3:
            print("用法: python wiki-search.py search \"查询词\"")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        search_content(query)
    elif command == "export":
        export_wiki()
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
