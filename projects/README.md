# projects — 项目容器
# origin: ai

## 本文件夹主要功能

所有研究项目的领域分层容器。按学科分领域目录（`理论物理/`、`AI-计算科学/`、`decomp/`、`写作-社会系统/`、`媒体/`、`知识/`、`金融/`、`persona-prompt-lab/`、`research-prompt/`），每个领域下按 `D*-<项目名>` 编号放项目。权威索引见 [INDEX.md](INDEX.md)（纯索引，逐层递归可达每个最小项目），活跃状态面板见 [ACTIVE.md](ACTIVE.md)（由 `scripts/aggregate-active.sh` 自动聚合各项目 `loop-state.json` 生成）。

## 接口

- 输入：新任务/新项目（须先按 INDEX.md 命名规范建领域/项目目录）
- 输出：各项目的成果、论文、报告
- 对外函数签名：无（纯目录层）

## 调用说明

- 导航：`INDEX.md` → 领域 `INDEX.md` → 项目 `INDEX.md` → 各 paper/idea（AGENTS.md 红线 0：递归可达）
- 领域层子目录数量应保持 3-7 个（结构补丁 ②；迭代/编号方案与 `archive/` 豁免）
- 新建项目前检查 `memory/` 是否已有同概念项目，禁止重复创建
