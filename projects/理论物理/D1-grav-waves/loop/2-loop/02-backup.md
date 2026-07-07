# 2-loop/02: 备份与变更清单

**所属规格**：/Users/a1-6/Desktop/workspace/loop/2-loop/02-backup.md
**状态**：completed
**输入**：01-pre-check (FAILED — C1/Fig2 missing, C2/no-bib, 后续迭代已修复)
**输出**：本文件 + git backup commit

---

## 备份记录

### Git Commit

| 字段 | 值 |
|------|-----|
| **Full Hash** | `cdf218be466155d789f810e0c72f82cacd10b57d` |
| **Short Hash** | `cdf218b` |
| **Message** | backup before iteration 23 arXiv gr-qc submission v13 |
| **Date** | 2026-07-01 20:23:47 +0800 |
| **Files Changed** | 56 files (+2858, -112) |

### 关键备份文件

| 文件 | 状态 | 备注 |
|------|------|------|
| `papers/2026-GW-BacQFT/GW-BacQFT-paper.tex` | 已备份 | v13 版本，25 refs，0 uncited |
| `papers/2026-GW-BacQFT/arxiv-submission-metadata.md` | 已备份 | v13 元数据，15 pages, ~1.2MB |
| `papers/2026-GW-BacQFT/arxiv-submission-D1-grav-waves-v5.tar.gz` | 已备份 | 846KB, Fig2 已加入 |
| `papers/2026-GW-BacQFT/arxiv-submission-D1-grav-waves-v6.tar.gz` | 已备份 | email 修复 |
| `papers/2026-GW-BacQFT/arxiv-submission-D1-grav-waves-v7.tar.gz` | 已备份 | abstract 格式清理 |
| `papers/2026-GW-BacQFT/arxiv-submission-D1-grav-waves-v8.tar.gz` | 已备份 | SKAO numbers, Theorem 1 修正 |
| `papers/2026-GW-BacQFT/arxiv-submission-D1-grav-waves-v9.tgz` | 已备份 | Fig3 scaling 图 |
| `papers/2026-GW-BacQFT/arxiv-submission-D1-grav-waves-v10.tgz` | 已备份 | Definition 1 修正 |
| `papers/2026-GW-BacQFT/arxiv-submission-D1-grav-waves-v11.tgz` | 已备份 | skewness 声明弱化 |
| `papers/2026-GW-BacQFT/arxiv-submission-D1-grav-waves-v12.tgz` | 已备份 | Raidal citation year 修正 |
| `papers/2026-GW-BacQFT/arxiv-submission-D1-grav-waves-v13.tgz` | 已备份 | 3 uncited bibitems 移除 |
| `papers/2026-GW-BacQFT/Fig3-scaling-SNR.png` | 已备份 | 87KB |

---

## 变更清单

**本次迭代（iteration 23）所需变更：无项目文件修改**

tarball v13 已就绪，变更清单用于记录提交前的状态快照。实际提交流程由 `arxiv_submit.sh` 或手动在 arXiv 完成。

**v13 历史变更摘要**（均已在备份 commit 之前完成）：

| 版本 | 变更内容 |
|------|----------|
| v5 | Fig2 加入 tarball（修复 C1） |
| v6 | 作者 email 修复 |
| v7 | abstract 去掉 \textbf 包装 |
| v8 | SKAO 数据加入结论，Theorem 1 常量 c 定义修正 |
| v9 | Fig3 scaling 图新增 |
| v10 | Definition 1 改为 cobordism-based extended AQFT |
| v11 | skewness 声明弱化，PBH 简并性加入 Limitations |
| v12 | Raidal citation year 2020→2017 |
| v13 | 移除 3 个 uncited bibitems (28→25 refs) |

---

## 回滚命令

```bash
# 回滚到本次备份状态
cd /Users/a1-6/Desktop/workspace/projects/理论物理/D1-grav-waves
git checkout cdf218b
# 如需回滚到备份之前的状态
git checkout cdf218b~1
```

---

## 验证

- [x] git add -A 通过（56 files changed）
- [x] commit 创建成功 (cdf218b)
- [x] tarball v13 存在于磁盘 (1,996,610 bytes)
- [x] 所有 v5-v13 tarball 已纳入版本控制
- [x] Fig3 已纳入版本控制

---

## 完成时间

2026-07-01 20:23:47 +0800

---

## 回滚

可直接覆盖此文件进行重做
