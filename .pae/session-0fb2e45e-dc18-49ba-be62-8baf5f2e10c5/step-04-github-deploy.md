# Step 04: GitHub 建仓推送 + loop/SOP 部署（为 arena 准备环境）

## 目标
创建 GitHub 远程仓库 `market-alpha` 并推送本地骨架+已移植的会话数据；同时把 1-loop 阶段文件和 arena-loop-pipeline SOP 复制进仓库推送，使 arena 拉取后即可走完整 loop 流程。

> ⚠️ 外部影响操作：创建远程仓库并推送，需用户确认。

## 涉及文件
- 远程仓库：`https://github.com/dd2003-460/market-alpha`
- 本地 `market-alpha/` 新增：
  - `loop/prompt-first/`（7 个阶段文件，rsync 自 workspace `loop/prompt-first/`）
  - `sop/arena-loop-pipeline.md`（cp 自 workspace `agents/arena-loop-pipeline.md`）

## 做法
1. `gh repo create dd2003-460/market-alpha --private --source ./market-alpha --push`（私有，含未公开预测）
2. 按 arena-loop-pipeline §4.1 模板部署 loop+SOP：
   - `rsync -av --delete workspace/loop/prompt-first/ market-alpha/loop/prompt-first/`
   - `cp workspace/agents/arena-loop-pipeline.md market-alpha/sop/`
3. commit + push，`git ls-remote` 验证 HEAD
4. 确认 Arena OAuth 授权覆盖新仓库（GitHub Settings → Applications → Arena AI Coding Agent → Repository access = All repositories）
5. 落盘 `market-alpha/loop-artifacts/push-verification.md`（commit hash + ls-remote 输出，断点 A 门禁）

## 验收标准
- [ ] 远程仓库存在，`git ls-remote` 返回 HEAD hash
- [ ] 远程含 loop/prompt-first/（7 文件）+ sop/arena-loop-pipeline.md + 两子模块 data/ 已移植数据
- [ ] push-verification.md 落盘
- [ ] Arena OAuth 授权状态确认
