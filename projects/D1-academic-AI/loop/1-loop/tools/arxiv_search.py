#!/usr/bin/env python3
"""
arxiv_search.py — arXiv 文献检索工具（D1 专用版）

替代 WebFetch/WebSearch，直接使用 arxiv.py 库绕过反爬限制。
支持批量关键词搜索、按作者搜索、引用统计。

用法:
  python3 loop/1-loop/tools/arxiv_search.py "关键词" [max_results]
  python3 loop/1-loop/tools/arxiv_search.py "Schelling segregation" 10
  python3 loop/1-loop/tools/arxiv_search.py --list  # 显示常用搜索列表
"""

import arxiv
import sys
import json
from datetime import datetime
from pathlib import Path

# 配置
CACHE_DIR = Path(__file__).parents[2] / "loop" / "1-loop" / "cache"
DEFAULT_MAX_RESULTS = 10
DEFAULT_DELAY = 2.0  # 秒，避免触发速率限制

CACHE_DIR.mkdir(parents=True, exist_ok=True)


def create_client():
    """创建带重试和速率限制的客户端"""
    return arxiv.Client(
        page_size=100,
        delay_seconds=DEFAULT_DELAY,
        num_retries=5
    )


def search(query, max_results=DEFAULT_MAX_RESULTS, sort_by=None):
    """搜索 arXiv 论文"""
    try:
        client = create_client()
        if sort_by is None:
            sort_by = arxiv.SortCriterion.Relevance
        else:
            sort_by = arxiv.SortCriterion.SubmittedDate

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by
        )
        results = list(client.results(search))
        return format_results(results)
    except Exception as e:
        print(f"搜索错误: {e}", file=sys.stderr)
        return []


def format_results(results):
    """格式化搜索结果为可读文本和 JSON"""
    output = []
    json_output = []

    for r in results:
        title = r.title[:120]
        published = r.published.strftime('%Y-%m') if hasattr(r.published, 'strftime') else 'N/A'
        authors = ', '.join([a.name for a in r.authors[:3]])
        if len(r.authors) > 3:
            authors += f' +{len(r.authors)-3}'

        record = {
            'title': title,
            'published': published,
            'authors': authors,
            'arxiv_id': r.entry_id.split('/')[-1],
            'categories': ', '.join(r.categories[:3]),
            'summary': r.summary[:200] + '...' if len(r.summary) > 200 else r.summary
        }

        output.append(f"[{published}] {title}")
        output.append(f"  作者: {authors} | ID: {record['arxiv_id']}")
        output.append(f"  类别: {record['categories']}")
        if len(r.authors) >= 3:
            output.append(f"  摘要: {r.summary[:150]}...")
        output.append()

        json_output.append(record)

    return '\n'.join(output), json_output


def list_default_searches():
    """列出 D1 项目的常用搜索关键词"""
    searches = {
        "动力学与同步": [
            "Kuramoto model synchronization",
            "chimera state phase transition",
            "coupled oscillator dynamics"
        ],
        "社会动力学": [
            "Schelling segregation model",
            "opinion dynamics consensus",
            "evolutionary game coordination"
        ],
        "信息论与学习": [
            "information bottleneck theory",
            "VC dimension learning theory",
            "PAC learning bounds"
        ],
        "正反馈系统": [
            "path dependence increasing returns",
            "positive feedback instability",
            "self-referential dynamics"
        ],
        " belief formation": [
            "belief aggregation consensus",
            "bounded confidence model",
            "belief coordination game"
        ]
    }

    output = "D1 常用搜索关键词:\n"
    for category, queries in searches.items():
        output += f"\n{category}:\n"
        for q in queries:
            output += f"  - \"{q}\"\n"

    return output


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n用法: python3 arxiv_search.py '关键词' [max_results]")
        print("或:   python3 arxiv_search.py --list")
        return

    if sys.argv[1] == '--list':
        print(list_default_searches())
        return

    query = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MAX_RESULTS

    print(f"搜索: {query}\n")
    text_output, json_output = search(query, max_results)
    print(text_output)

    # 保存到缓存
    cache_file = CACHE_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_search.json"
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print(f"\n结果已缓存: {cache_file}")


if __name__ == '__main__':
    main()
