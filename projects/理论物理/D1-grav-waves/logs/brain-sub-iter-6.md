# Brain-Sub Iteration 6 — 质询报告

**执行者**：Brain-Sub (Auto)
**执行时间**：2026-07-01 14:05
**上下文**：2-loop/06-decision completed, ready_for_submission

---

## 质询

### Q1: arXiv 政策合规 — 作者邮箱不合法

tex 文件第23行：`chenglu@research.local`

`.local` 是 mDNS 保留域名，不是有效邮箱。arXiv 要求作者有可验证的联系方式。
**建议**：在上传前替换为实际邮箱。如果作者选择不暴露邮箱，可用 `chenglu[at]protonmail[dot]com` 等替代。

### Q2: arXiv 政策合规 — 使用 article 类而非 JHEP 类

tex 文件第1行使用 `\documentclass[11pt,a4paper]{article}`，不是 JHEP 模板。虽然 arXiv 允许自定义模板，但 gr-qc 社区论文绝大多数使用 PRD 格式或article 格式。这个不是合规问题，但值得注意 — JHEP 社区可能期望 JHEP 模板一致性。

**实际风险**：arXiv gr-qc 接受 article 类提交的论文，无合规问题。

### Q3: arXiv 查重风险

论文大量引用 NANOGrav 15-year 数据相关文献（Agazie:2023, etc.）和 AQFT 文献（Brunetti:2003, etc.）。artXiv similarity report 可能标记：
- NANOGrav 数据的描述部分（Agazie:2023 相关）— 这是正常引用，但如果措辞与已有论文高度相似会触发
- AQFT 框架描述部分（Brunetti:2003, Baez:1995 相关）— 同上

**风险等级**：低 — 标准引用不会触发审查，但如果直接复制了某些综述的段落文字会被标记。

### Q4: 科学内容风险 — Abstract 过度声称

Abstract 第34行有一段 `\textbf{Information-theoretic perspective:}` 的内容，描述了 HD anisotropy measurement 的"交叉域映射"（GW detection ↔ information theory ↔ category theory）。这部分语言偏向哲学论述，对于 gr-qc 读者来说可能显得冗余甚至过度解释。

**风险**：arXiv 不拒稿这类内容，但 gr-qc 审稿人可能认为 abstract 过于冗长（应该先陈述核心结果再提供观点性讨论）。

### Q5: DistCat 并行准备

DistCat 声称需要 D1 的 arXiv ID 才能引用。但 DistCat 的 tarball 可以在 D1 提交前完全准备完毕，仅需预留一个占位引用格式：
```
[28] A. Author, "Title," arXiv:XXXX.XXXXX [gr-qc] (D1-grav-waves, submitted).
```
这样 D1 获得 arXiv ID 后可以快速更新。

**建议**：现在开始 DistCat 的并行准备工作。

---

## 盲区和遗漏

### 盲区1: license 声明可能冲突

Abstract 内包含 "CC BY 4.0" 声明，同时 arXiv 也有 license 选择。双重 license 声明可能造成混淆 — arXiv 提交时有标准 license dropdown，论文内部的 CC BY 声明应该是匹配的。

**建议**：确保论文内 CC BY 4.0 与 arXiv 提交时选择的 license 一致。

### 盲区2: BibTeX .bib 文件与 inline thebibliography 内容可能不一致

v5 tarball 包含 `GW-BacQFT.bib`（24 entries）但 tex 使用 inline thebibliography（27 bibitems）。两者条目数量和格式不一致意味着：
- GW-BacQFT.bib 只是元数据记录，不参与编译
- arXiv 审查时不会 .bib 文件的影响，但如果 arXiv 生成 abstract 页面时会扫描 .bib 可能导致引用计数混乱

**建议**：考虑从 tarball 中移除 GW-BacQFT.bib（或将其重命名为 `.bib.meta`），避免混淆。

### 盲区3: 论文第26行 `\date{\today}` 可能导致提交日期显示异常

`2026-07-01` 是编写日期。如果 arXiv 提交时间与此不同，`\date{\today}` 仍然显示 tex 最后编译日期。arXiv 的 "Published" 日期来自 arXiv 服务器，不是论文内日期。这个不是问题，但如果 arXiv 生成 PDF 元数据时会包含 \date 值，可能导致日期不一致。

---

## 总结

| # | 质询 | 风险等级 | 建议 |
|---|------|----------|------|
| Q1 | 作者邮箱 .local 无效 | 高 | 上传前修改为实际邮箱 |
| Q2 | article 类 vs JHEP 类 | 低 | gr-qc 接受 article 类 |
| Q3 | arXiv 查重 | 低 | 标准引用无问题 |
| Q4 | Abstract 过度解释 | 低 | gr-qc 读者可能不欣赏 |
| Q5 | DistCat 并行准备 | 中 | 现在开始准备 |
| B1 | 双重 license | 低 | 确保一致 |
| B2 | .bib 与 inline bib 不一致 | 低 | 可移除或重命名 .bib |
| B3 | \date{\today} 日期漂移 | 极低 | 无影响 |

**最高优先级修复**：Q1 — 作者邮箱必须在上传前修正。
