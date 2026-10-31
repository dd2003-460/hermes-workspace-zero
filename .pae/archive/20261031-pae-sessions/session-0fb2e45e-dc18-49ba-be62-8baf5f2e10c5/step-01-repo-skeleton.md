# Step 01: 大仓库骨架创建（market-alpha）

## 目标
在 workspace 下创建 `market-alpha` 大仓库本地骨架：标准目录结构 + 两个子模块占位 + git 初始化，为后续所有步骤提供落点。

## 涉及文件
- `market-alpha/`（新建目录，git init）
  - `README.md`（大仓库定位：利用专业技术信息差预测市场；子模块索引表）
  - `INDEX.md`（纯索引：只列子模块，不抄内容）
  - `.gitignore`（Python/p LaTeX 产物/临时文件）
  - `gpu-price-prediction/`（README.md + data/ docs/ src/ reports/ outputs/）
  - `transformer-sector-valuation/`（README.md + data/ docs/ src/ reports/ outputs/）
  - `tasks/`（arena 任务书目录）
  - `loop-artifacts/`（arena 核验/loop 工件目录）

## 做法
1. `mkdir -p` 建完整目录树，空目录放 `.gitkeep`
2. 写大仓库 `README.md`：定位说明 + 子模块表（名称/领域/状态/当前轮次/胜率占位列）+ 更新机制说明（每子模块独立更新预测、修正模型、检验胜率）
3. 写 `INDEX.md`：纯索引两子模块
4. 两子模块各写 `README.md` 占位（定位/数据源/方法概览/目录说明）
5. `git init` + 全量 add + 首次 commit

## 验收标准
- [ ] 目录树完整存在（两子模块 × 5 子目录 + tasks/ + loop-artifacts/）
- [ ] 大仓库 README 含子模块索引表
- [ ] `git -C market-alpha log --oneline` 有初始 commit
- [ ] 命名全部 kebab-case，无空格无中文目录名
