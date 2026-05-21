#!/usr/bin/env python3
"""
Web search tool - uses DuckDuckGo HTML search (no API key required)
Usage: python search_web.py "search query" [max_results]
"""
import sys
import subprocess
import re
from urllib.parse import unquote, quote

def duckduckgo_search(query, max_results=10):
    """Search using DuckDuckGo HTML endpoint"""
    encoded_query = quote(query)
    cmd = [
        'curl', '-s',
        f'https://html.duckduckgo.com/html/?q={encoded_query}',
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    html = result.stdout
    
    results = []
    pattern = r'result__a[^>]*>([^<]+)</a>.*?result__url[^"]*" href="([^"]+)"'
    for match in re.finditer(pattern, html, re.DOTALL):
        title = match.group(1).strip()
        url = unquote(match.group(2).split('uddg=')[-1].split('&')[0])
        results.append({'title': title, 'url': url})
        if len(results) >= max_results:
            break
    
    return results

def arxiv_search(query, max_results=10):
    """Search arXiv using their API"""
    import xml.etree.ElementTree as ET
    encoded_query = quote(query)
    url = f'https://export.arxiv.org/api/query?search_query=all:{encoded_query}&max_results={max_results}'
    
    result = subprocess.run(['curl', '-s', '-L', url], capture_output=True, text=True, timeout=15)
    root = ET.fromstring(result.stdout)
    
    results = []
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    for entry in root.findall('atom:entry', namespace):
        title = entry.find('atom:title', namespace).text.strip()
        summary = entry.find('atom:summary', namespace).text.strip()[:500]
        id_url = entry.find('atom:id', namespace).text
        results.append({
            'title': title,
            'summary': summary,
            'url': id_url
        })
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python search_web.py <query> [max_results] [--arxiv]")
        print("       python search_web.py <query> --arxiv [max_results]")
        sys.exit(1)
    
    query = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 10
    use_arxiv = '--arxiv' in sys.argv or '-a' in sys.argv
    
    if use_arxiv:
        results = arxiv_search(query, max_results)
        print(f"arXiv search for: {query}")
        print(f"Found {len(results)} results\n")
    else:
        results = duckduckgo_search(query, max_results)
        print(f"Web search for: {query}")
        print(f"Found {len(results)} results\n")
    
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   {r['url']}")
        if 'summary' in r:
            print(f"   {r['summary']}")
        print()

if __name__ == '__main__':
    main()
