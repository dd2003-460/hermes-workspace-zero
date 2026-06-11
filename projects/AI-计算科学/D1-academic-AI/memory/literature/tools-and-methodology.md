# 文献检索工具与方法论

**创建**: 2026-05-04
**版本**: v0.1（初始架构）

---

## 工具能力矩阵

| 工具 | 状态 | 能力 | 限制 |
|------|------|------|------|
| **arxiv.py v3.0.0** | ✅ 可用 | 搜索/下载 arXiv 论文，支持重试和速率限制 | 需要 Python ≥3.10，目前运行在 3.9（urllib3 警告） |
| WebFetch | ⚠️ 部分 | 抓取页面内容 | Google Scholar 有验证码，arXiv search page 不工作 |
| WebSearch | ❌ 不可用 | 结构化搜索 | arXiv/Google Scholar 返回 422 |
| GitHub 搜索 | ⚠️ 部分 | 代码仓库查找 | 结果取决于 GitHub API 可用性 |

### Python 版本兼容性
```
pip install arxiv  → 需要 Python 3.10+
当前: Python 3.9
工作区: Library/Python/3.9
```
需要升级 pip 或通过其他方式解决 urllib3 兼容性。

---

## 搜索方法论

### 分层搜索策略
```
L1 (快速预扫描) → arXiv API (arxiv.py)
L2 (深度检索)   → WebFetch (Google Scholar)
L3 (最终确认)   → 训练知识（架构框架文件）
```

### 关键词工程
```
优先级:
1. 精确匹配 + OR（概念并列）：`"self-fulfilling prophecy" OR "belief coordination"`
2. 作者 + 关键词（经典理论）：`Schelling "segregation" OR "threshold"`
3. 理论名称搜索：`"deGroot model" OR "Friedkin-Johnsen"`
4. 英文同义词扩展：`convergence ↔ consensus ↔ alignment`
```

---

## 工具优先原则

**核心原则：选择比努力重要。**

对于重复性任务（论文搜索、下载、分类），工具的效率提升是数十倍的。
不要手动复制粘贴 arXiv 摘要——用 arxiv.py 脚本批量处理。

**推荐工具栈**：
- arxiv.py — arXiv 搜索/下载
- 若有 MCP 工具可用 — 构建自动化工作流
- 本地缓存 — 避免重复下载（chimera_lab/papers_cache/）

---

## 1-loop 集成建议

在规划阶段添加 "工具辅助检索" 步骤：
1. 提取理论核心关键词
2. 运行 arxiv.py 批量搜索
3. 下载关键论文 PDF（供后续摘要）
4. 更新 related-work-framework.md

---

*此文件应随工具可用性更新而维护*
