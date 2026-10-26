# tools
# origin: ai

## 本文件夹主要功能

独立工具脚本与本地实验环境集合：arXiv 检索（`arxiv-search.py`、`adscite-graph.py`）、网页 LLM 审查流水线（`llm-review-pipeline.py`、`t18-review-pipeline.py`、`web-llm-review.js`、`browser-review.js`、`test-web-llm-review.js`）、persona 保真度打分（`persona_fidelity_scorer.py`、`persona_profile_prompt.md`）、mem0 记忆实验（`mem0-experiment.py`、`mem0-smoke-test.py`）、联网检索（`search_web.py`，需 DEEPSEEK_API_KEY，默认禁用）、分析框架说明（`analysis_framework.md`）。子目录为本地虚拟环境与数据：`ollama/`、`mem0-venv/`、`mb-server-venv/`、`memory-benchmarks/`（子模块）、`context-mode/`。

## 接口

- 输入：各自命令行参数（arXiv 查询词、persona profile、审查目标 URL 等）
- 输出：检索结果 / 审查 JSON 回执 / 打分明细
- 对外函数签名：无统一 API，逐脚本独立入口

## 调用说明

- Python 脚本：`python3 tools/<脚本名>.py [args]`（mem0 系列需用 `mem0-venv`）
- JS 脚本：`node tools/<脚本名>.js [args]`（审查类依赖 ego-browser 登录态）
- 各脚本无跨脚本依赖；venv 目录为一次性环境，不纳入 git
