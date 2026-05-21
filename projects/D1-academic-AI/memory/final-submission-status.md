---
name: 最终提交状态汇总 (iteration 82)
description: 所有已完成论文的提交状态、tarball、编译验证
type: reference
---

## 最终提交状态 (2026-05-11 23:00)

### 论文清单

| 论文 | 状态 | 页数 | PDF大小 | arXiv分类 | tarball | 目标期刊 |
|------|------|------|---------|-----------|---------|---------|
| D1-grav-waves (GW-BacQFT) | arXiv-ready (v4) | 10 | 303KB | gr-qc | 127K (v4) | JCAP |
| DistCat (统一框架) | arXiv-ready (v3) | 13+3supp | 303+336+241KB | math.CT+gr-qc | 867K (v3) | JMP |
| D40 (AI market) | arXiv-ready | 15 | 800KB | cs.LG | 12K | 待定 |

### 提交文件位置

**D1-grav-waves:**
- `projects/D1-grav-waves/papers/2026-GW-BacQFT/GW-BacQFT-paper.tex`
- `projects/D1-grav-waves/papers/2026-GW-BacQFT/arxiv-submission-D1-grav-waves-v3.tar.gz`
- `projects/D1-grav-waves/scripts/arxiv_submit.sh` (自动化脚本)

**DistCat:**
- `projects/D1-academic-AI/papers/arxiv-ready/` (main.tex + 3 supplement PDFs + tarball)
- `projects/D1-academic-AI/papers/latex-pandoc-convert/` (中间转换产物)

**D40:**
- `projects/D1-academic-AI/papers/D40-paper-converted.tex`
- `projects/D1-academic-AI/papers/D40-paper-converted.pdf`
- `projects/D1-academic-AI/papers/arxiv-submission-D40.tar.gz`

### BibTeX 参考文献文件
- `projects/D1-grav-waves/papers/2026-GW-BacQFT/GW-BacQFT.bib` — 24 references, D1-grav-waves paper
- `projects/D1-academic-AI/papers/DISTCAT-references.bib` — 12 references, DistCat unified framework

### 工具链
- `scripts/arxiv_submit.sh` — arXiv 端到端自动化提交
- `scripts/arxiv_submission_checklist.sh` — 清单验证
- `scripts/arxiv_cat.py` — arXiv 文献搜索
- `scripts/arxiv_prepare.py` — 提交包准备
- `scripts/project_health_check.sh` — 项目状态检查

### arXiv 提交步骤
1. 打开 https://arxiv.org/submission
2. 选择分类 (gr-qc / math.CT / cs.LG)
3. 上传对应 tarball
4. 填写 metadata (标题、作者、摘要见 arxiv-submission-metadata.md)
5. 提交

### 下一步
1. 等待作者确认提交
2. arXiv 上线后准备 JCAP/JMP 投稿版本
3. 探索 DistCat 桥梁论文 (2-Cat Classification of GW Observables)
4. EMRI Paper I (2511.03657v1) 补充 ρ_s→0 极限推导 → JCAP
