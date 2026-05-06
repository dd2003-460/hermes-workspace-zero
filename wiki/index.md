# Wiki Index

## 目录结构

```
wiki/
├── index.md              ← 本文件：知识总览与导航
├── log.md                ← 变更日志（每次写入/更新都记录）
├── SCHEMA.md             ← 知识体系定义（概念、实体、关系类型）
├── embeddings/           ← 向量索引目录
│   ├── index.json        ← 向量元数据（id, path, embedding_ref）
│   └── vectors/          ← 向量数据（可选：本地存储或外部引用）
├── raw/                  ← 原始素材（论文、文章、转录）
│   ├── articles/         ← 一般文章
│   ├── papers/           ← 学术论文（arxiv ID 命名）
│   └── transcripts/      ← 对话/会议转录
├── entities/             ← 实体笔记（人、机构、项目）
│   ├── people/           ← 人物
│   └── orgs/             ← 机构
├── concepts/             ← 概念笔记（核心知识单元）
├── comparisons/          ← 对比分析
└── queries/              ← 查询模板与结果缓存

scripts/
├── wiki-search.py        ← 轻量搜索（无需外部依赖）
└── wiki-embed.py         ← 向量嵌入（需 pip install sentence-transformers）
```

## 知识体系（按 SCHEMA.md）

### 范畴论 × 引力波天文学

- [[Extended Functorial QFT]] — PTA/干涉仪的统一数学框架
- [[AQFT]] — 代数量子场论，局部协变性的基础
- [[拓扑斯理论]] — 量子引力的背景无关表述
- [[高阶规范理论]] — 新引力波偏振模式的分类
- [[层论在 PTA 数据分析中的应用]] — 最大研究空白

### 关键实体

- **人**: [[Urs Schreiber]], [[John Baez]]
- **机构**: [[NANOGrav]], [[SKAO]]

### 关键论文

- arXiv:0806.1079 — Schreiber, AQFT from n-functorial QFT
- arXiv:1105.6202 — Brunetti, Fredenhagen & Verch, 局部协变性
- arXiv:2311.11026 — Schreiber, Higher Topos Theory in Physics

## 使用方式

### 1. 关键词搜索（无需安装依赖）
```bash
python3 wiki/scripts/wiki-search.py search "范畴论"
python3 wiki/scripts/wiki-search.py search "引力波"
```

### 2. 向量检索（需安装依赖）
```bash
pip install sentence-transformers numpy
python3 wiki/scripts/wiki-embed.py build
python3 wiki/scripts/wiki-embed.py search "范畴论"
```

### 3. 导出迁移
```bash
python3 wiki/scripts/wiki-search.py export
# 输出到 wiki/wiki_export.json（可导入任意平台）
```

## 与 memory/ 的关系

| 目录 | 用途 | 性质 |
|------|------|------|
| `memory/` | 会话日志、进度追踪 | 临时性 |
| `wiki/` | 结构化知识、可长期复用 | 持久性 |

## 迁移指南

整个 `wiki/` 目录可复制到任意平台：
1. **Obsidian**: 直接导入 wiki 目录作为 vault
2. **Notion**: 用 `wiki_export.json` 批量导入
3. **任意向量数据库**: 用 `wiki-embed.py build` 生成 embedding
