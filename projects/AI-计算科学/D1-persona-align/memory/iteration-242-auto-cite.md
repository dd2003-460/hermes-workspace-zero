# Iteration 242: gap_filler --auto-cite 自动文献搜索

## 目标
实现 gap_filler 调用 arXiv API 自动搜索相关文献并填充引用占位符，解决 iteration 241 识别的关键限制：gap_filler 建议的引用是填充式占位符 (citation_1)，需要用户手动填入。

## 执行动作

### persona_v3_gap_filler.py 扩展

1. **新增 `search_arxiv(topic, max_results)` 函数**:
   - 通过 arXiv API (export.arxiv.org/api) 搜索相关文献
   - 解析 Atom XML 返回 (标题, 作者, 摘要)
   - 对中文 topic 使用英文关键词映射表 (arXiv 是英文数据库)
   - 当前映射: "自适应 Token 与信息密度" → "adaptive token information density"

2. **新增 `fill_citation_placeholders(template, topic, arxiv_results)` 函数**:
   - 将 `{citation_1}`, `{citation_2}`, `{citation_3}` 替换为真实文献引用
   - 将 `{data_source_1}`, `{field_1}`, `{field_2}` 替换为话题相关内容
   - 空作者名回退为 "Anonymous"

3. **`generate_fill_suggestions()` 扩展**:
   - 新增 `auto_cite` 参数
   - 当 auto_cite=True 时，对 ReportBench 维度自动搜索并填充引用

4. **`process_file()` 和 CLI 扩展**:
   - 新增 `--auto-cite` 命令行标志
   - 传递 auto_cite 到 process_file → generate_fill_suggestions

## 验证

对 idea-20 运行 `--file idea-20.md --json --auto-cite`:
- 引用相关性建议中的 `{citation_1}` 被替换为真实 arXiv 文献
- 作者名: Shivam Duggal, Sanghyun Byun, William T. Freeman 等
- 标题: Single-pass Adaptive Image Tokenization for Minimum Program Search
- 摘要: According to Algorithmic Information Theory (AIT)...

## 限制与未来改进

1. **中文 topic 映射**: 当前只映射了 2 个 topic → English。未来应实现自动翻译或使用英文关键词集合
2. **arXiv API 速率限制**: 通过 urllib 调用 (WebFetch 之前被 429)，需添加请求间隔
3. **泛化**: 对未映射的 topic，搜索应回退到中文 topic (即使 arXiv 结果可能为空)

## 影响

- gap_filler 从"建议引用占位符"升级为"自动搜索并填充文献"
- 这是 iteration 234 提到的"主动搜集外部学术资源"的具体实现
- 闭环: 评估 → 发现缺口 → 搜索文献 → 生成引用 → --apply 补全 → re-evaluate
