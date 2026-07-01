# 2-loop/02: 备份与变更清单

**所属规格**：/Users/a1-6/Desktop/workspace/loop/2-loop/02-backup.md
**状态**：ready_for_backup
**输入**：01-pre-check (FAILED — C1/Fig2 missing, C2/no-bib)
**输出**：本文件 + 备份文件

---
## 需要修复的缺陷

| 编号 | 缺陷 | 修改文件 |
|------|------|----------|
| C1 | Fig2 缺失于 tarball | 新文件加入 v4 tarball |
| C2 | PDF 无参考文献列表 | `GW-BacQFT-paper.tex` |
| C3 | tarball 内容不完整 | 新 v4+1 tarball |
| C4 | metadata 页面数/大小错误 | `arxiv-submission-metadata.md` |
| C5 | INDEX.md 不一致 | `INDEX.md` |

---
## 前置备份清单

| 文件 | 当前状态 | 备份方式 |
|------|----------|----------|
| `papers/2026-GW-BacQFT/GW-BacQFT-paper.tex` (510行) | 待修改 | cp + 记录校验和 |
| `papers/2026-GW-BacQFT/arxiv-submission-D1-grav-waves-v4.tar.gz` | 待替换 | cp → v5.tar.gz |
| `papers/2026-GW-BacQFT/GW-BacQFT-paper.pdf` (12页) | 可重新生成 | 无操作 |
| `papers/2026-GW-BacQFT/arxiv-submission-metadata.md` | 待修改 | cp + 记录校验和 |

---
## 完成时间
待完成

---
## 回滚
可直接覆盖此文件进行重做
