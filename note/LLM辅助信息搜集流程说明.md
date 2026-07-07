# LLM 辅助信息搜集流程说明

## 概述

本流程集成到 Ralph Loop 信息搜集环节，实现 arXiv/ADS 自动搜索 + LLM 筛选的自动化管线。

## 工具清单

| 工具 | 路径 | 功能 |
|------|------|------|
| arXiv 搜索 | `tools/arxiv-search.py` | arXiv API 搜索 + 相关性分类 |
| ADS 引用图 | `tools/adscite-graph.py` | NASA ADS 引用网络查询 |
| 浏览器控制 | `note/浏览器控制可行性调研.md` | Playwright 备用抓取 |

## 使用方法

### 1. arXiv 自动搜索

```bash
# 基本搜索
python3 tools/arxiv-search.py search "gravitational wave optical clock" --top 20

# 多关键词搜索
python3 tools/arxiv-search.py search "optical lattice clock" "space gravitational wave" --top 10

# 指定输出目录
python3 tools/arxiv-search.py search "GW detection" --top 20 --output-dir note/
```

输出: `note/arxiv-results-YYYYMMDD.json`

包含分类结果：
- must-read (>=0.85): 直接相关
- recommended (>=0.65): 间接相关
- reference (>=0.40): 方法/引用参考
- skip (<0.40): 不相关

### 2. LLM 辅助筛选 (可选)

```bash
# 安装 anthropic SDK
pip install anthropic

# 设置 API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 搜索并自动 LLM 分类
python3 tools/arxiv-search.py search "OLC gravitational waves" --top 30
```

LLM 会阅读每篇论文的摘要，给出更准确的相关性评分。

### 3. ADS 引用图

```bash
# 设置 ADS API key
export ADS_QTOKEN="your_token"

# 搜索 ADS
python3 tools/adscite-graph.py search "optical clock gravitational waves" --top 20

# 构建引用图
python3 tools/adscite-graph.py graph seed-papers.json --depth 2 --max-per-node 5
```

### 4. 浏览器备用抓取

当 arXiv API 不可用时，使用 Playwright 抓取网页：

```bash
# 测试用 Playwright 搜索 arXiv
node tools/arxiv-web-search.js  # 待实现
```

## Ralph Loop 集成点

### 集成到 1-loop Step 2 (工具调用+信息搜集)

```
Step 2: 工具调用 + 信息搜集
  |
  +-- 调用 arxiv-search.py 自动搜索
  |    关键词来自 Step 1 的目标分解
  |
  +-- LLM 自动筛选结果
  |    根据研究问题判断相关性
  |
  +-- 产出: note/前沿信息-YYYYMMDD.md
       包含最相关的论文列表和摘要
```

### 持续监控 (可选)

```bash
# 设置 RSS 监控
python3 tools/arxiv-search.py rss "gravitational wave clock" --interval 24

# 监控文件位于 note/rss-monitors/
# 每次运行会检查新论文并通知
```

## 输出规范

### arxiv-results-YYYYMMDD.json

```json
{
  "search_date": "2026-07-02T...",
  "query": "gravitational wave optical clock",
  "keywords": ["gravitational wave", "optical clock"],
  "total_found": 45,
  "classified": 45,
  "must_read": [...],
  "recommended": [...],
  "reference": [...],
  "all_results": [...]
}
```

### citation-graph-YYYYMMDD.json

```json
{
  "nodes": [
    {
      "bibcode": "...",
      "title": "...",
      "authors": ["..."],
      "year": "2026",
      "depth": 0
    }
  ],
  "edges": [
    {"from": "...", "to": "...", "type": "citation"}
  ]
}
```

## 故障处理

| 问题 | 解决方案 |
|------|----------|
| arXiv API 502 | 自动重试 3 次，或改用 Playwright 抓取 |
| ADS 无 API key | 暂时无法使用 ADS 功能 |
| LLM API 失败 | 自动降级为启发式分类 |
| 网络超时 | 增加 --timeout 参数 |

## 更新前沿信息

搜索结果应更新到 `note/前沿信息-2026.md`:

```bash
# 手动添加重要论文到前沿信息文件
# 格式:
## YYYY-MM-DD
### [分类] 论文标题
- arXiv: arXiv:XXXX.XXXXX
- 相关性: must-read/recommended/reference
- 摘要: ...
- 笔记: ...
```
