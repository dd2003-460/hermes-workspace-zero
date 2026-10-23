# Step 02: episodes.md 入库 + loop-state.json 重建

## 目标
连续剧目录表 `docs/episodes.md`（E01-E24 全集 + batch-5~10 批次规划）目前只在本地工作区，**未提交**（git status 显示 `?? docs/episodes.md`）。目标会话裸奔状态下任何会话都可能丢它。本步把它提交进 git，并重建项目 `loop-state.json`，让新 goal 一启动就有状态锚点。

## 涉及文件
- `d1-video-recreation/docs/episodes.md`（提交，不改内容）
- `d1-video-recreation/loop-state.json`（**新建**，目前项目无此文件）
- git 仓库 `dd2003-460/d1-video-recreation`（main 分支，当前 HEAD f39e016）

## 做法
1. 写 `d1-video-recreation/loop-state.json`，内容：
   - project: d1-video-recreation
   - 当前任务: AI 拟人化连续剧系列化（E01-E24）
   - 起点: batch-5（E01-E04），依据 `docs/episodes.md`
   - 已完成: batch-1~4 共 13 个视频（status-table.md v1.5.0）
   - 每批流程: 写 arena prompt → push → arena agent mode 执行 → PR 提取 → check_overlap → episodes.md 改 ✅
   - 更新: 2026-10-23
2. `git add docs/episodes.md loop-state.json` + commit + push origin main
3. push 是 arena 前置条件（SOP 01：arena 要 clone 仓库读 episodes.md 才知道剧情表）

## 验收标准
- [ ] `git status` 干净，episodes.md 与 loop-state.json 在 main 上
- [ ] origin/main 同步（push 成功）
- [ ] loop-state.json 是合法 JSON（`node -e "JSON.parse(...)"` 或 python 验证）

## 风险
- push 到 GitHub 是外发动作，但属本项目常规流程（此前 13 个 PR 均走此通道），且内容无敏感信息，L1 级自主执行
