# Step 03: 撰写 batch-5 arena 任务书（E01-E04）

## 目标
连续剧的第一个批次 = 第一幕"感受"的 E01 好奇 / E02 快乐 / E03 悲伤 / E04 愤怒。按既有模式（`arena-prompts/batch4-companion-fix-v1.1.md`）写一份 arena 任务书，让目标会话的新 goal 第一轮就能直接投 arena，不用现场构思。

## 涉及文件
- 新建: `d1-video-recreation/arena-prompts/batch5-episodes-v1.0.md`
- 参考（只读）: `d1-video-recreation/docs/episodes.md`（E01-E04 一句话剧情）、`sop/05-style-benchmark.md`（像素标准 v1.4.0）、`sop/01-arena-agent-mode.md`（prompt 要求 + 教训）、`arena-prompts/batch4-companion-fix-v1.1.md`（多任务格式样板）
- 仓库: push 到 origin/main（arena 要 clone）

## 做法
1. 任务书结构（沿用 batch4 多任务格式）:
   - 任务 1-4 = E01-E04，每个含：主题、3 场景×10s 设计（依据 episodes.md 一句话展开，场景文字具体到终端命令/字幕/Clawd 表情）、技术要求
   - 统一技术要求: BW=640 BH=360 SCALE=2 → 1280×720@60fps 1800 帧；像素标准 SOP 05（4-6px 块 + fusion-pixel 字体 + Clawd 40×17）；终端 440×200（companion v1.1 标准）；键盘音与文字同步
   - 参考文件清单: `src/pixel_arena_v2.js`、`src/pixel_story_arena.js`、`src/render_reboot_arena.js`（batch-4 最新布局标准）、`sop/05-style-benchmark.md`
   - 输出文件命名规范: `src/render_E01_curiosity_arena.js` / `check_overlap_E01_arena.js` / `outputs/E01_curiosity_arena_v1.0.mp4` / `audio/E01_mix.wav`（E02-E04 同理）
   - 验收: 每集 check_overlap PASSED + commit + push + PR
   - **防 "No Changes" 条款**: 明确编号步骤（clone → 读 SOP → 逐集写脚本 → 本地验证 → 提交），引用 goodbye 教训（初始 prompt 无编号步骤时 arena 只读文件不产出）
   - **防全局改写条款**: 禁止修改既有 LINES/STARTS/SCENES 数组
2. commit + push

## 验收标准
- [ ] 任务书 4 集剧情与 episodes.md 一致（不偏离一句话设定）
- [ ] 含显式编号执行步骤 + 防 No Changes / 防全局改写条款
- [ ] 输出文件命名规范统一（E0N_<trait>_arena）
- [ ] 已 push 到 origin/main

## 风险
- 无（新增文件，不改既有）
