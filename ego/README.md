# ego
# origin: ai

## 本文件夹主要功能

ego-lite / ego-browser 与 LMArena（arena.ai/agent）通道相关脚本及批次工作目录。存放 arena agent mode 的提交、检查、清理脚本（如 `arena-b8-submit.mjs`、`arena-b8-check.mjs`、`arena-b8-submit2.mjs`）和通道连通性检查（`channel-check-20261023`）、批次产物/清理记录目录（`arena-b8-20261024`、`arena-cleanup-20261024`）。

## 接口

- 输入：ego-lite 已登录会话状态（arena.ai 登录 + GitHub 绑定）、批次 prompt 文件
- 输出：arena 会话提交回执、批次检查结果
- 对外函数签名：Node 脚本（.mjs），无导出 API，直接执行

## 调用说明

- `node ego/arena-b8-submit.mjs` 等脚本直接运行；依赖 ego-browser 登录态，不可在无头浏览器下运行
- 通道验证流程见 `.claude/skills/ego-verify/SKILL.md` 与 `agents/arena-loop-pipeline.md`
- 子目录功能见各自文件（批次目录为一次性产物，不展开）
