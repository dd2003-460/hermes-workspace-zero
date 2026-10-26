# scripts
# origin: ai

## 本文件夹主要功能

仓库级自动化脚本：活跃项目面板聚合（`aggregate-active.sh`，更新 `projects/ACTIVE.md`）、RALPH 运行时安装与启动（`install-ralph-runtime.sh`、`_start-ralph.sh`）、arXiv 投稿流水线（`arxiv_*.py/sh` 系列、`compile_paper.sh`、`papers_readness.sh`、`arxiv_submission_checklist.sh`、`arxiv_upload_helper.sh`）、索引与项目结构体检（`index_verifier.py`、`project-tidy/` 6 步体检 SOP）、论文/研究辅助（`d1_research_iteration.py`、`aggregate_profile.py`）。

## 接口

- 输入：各脚本命令行参数（项目路径、arXiv 元数据等）
- 输出：聚合面板、体检报告、投稿产物（tarball/PDF 清单）
- 对外函数签名：shell/Python 脚本入口，无导出 API

## 调用说明

- 面板聚合：`bash scripts/aggregate-active.sh`（会话最小阅读链路第 1 步的数据源）
- 项目体检：`bash scripts/project-tidy/run.sh --all`（AGENTS.md 红线 0 结构补丁配套 SOP，每日 09:00 定时）
- arXiv 投稿：按 `arxiv_prepare.py` → `compile_paper.sh` → `arxiv_submit.sh` 顺序执行，详见各脚本头部注释
