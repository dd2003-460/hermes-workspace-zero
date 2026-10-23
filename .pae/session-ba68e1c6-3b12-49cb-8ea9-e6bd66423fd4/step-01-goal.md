# Step 01: 在目标会话按 episodes.md 重建 goal

## 目标
本会话无法操作另一个会话（d1-video-recreation 会话）的 goal——目标会话已被误 clear，处于裸奔状态（无 goal、不会自己动）。本步产出**可直接粘贴的一句话触发指令**，成璐把这句话发到目标会话，即可在该会话内重建"AI 拟人化系列化"goal 并按 `d1-video-recreation/docs/episodes.md` 跑批。

## 涉及文件（只读）
- `d1-video-recreation/docs/episodes.md` — 全集目录（E01-E24 四幕 + batch-5~10 批次规划），实质内容已在此落盘
- `d1-video-recreation/docs/status-table.md` — 当前 13 视频全部 done（batch-4 收尾于 PR#13）
- `d1-video-recreation/sop/01-arena-agent-mode.md` — arena 外包流程 + 已知教训（prompt 必须显式编号步骤；arena "No Changes" 模式需 follow-up）

## 做法
1. 本会话**不做任何变更操作**，仅调研（已读 episodes.md / status-table.md / sop/01）。
2. 产出一条自包含的 goal 触发指令，内容要点：
   - 目标：AI 拟人化连续剧系列化，按 `docs/episodes.md` 完成 E01-E24（batch-5 → batch-10，每批 4 集）
   - 每批 = 1 次 arena agent mode 任务（SOP 01：单会话 3-4 集上限；prompt 必须含显式编号步骤，防 "No Changes"）
   - 完成判据：每集提取到 main + check_overlap PASSED → episodes.md 状态列改 ✅
   - 当前起点：batch-5（E01-E04，第一幕：感受）
   - 循环纪律：每轮三写（todo → loop-state.json → 门禁自检），状态回写 `d1-video-recreation/loop-state.json`
3. 指令控制在 1 屏内，目标会话收到后即可 create_goal 开跑，不需要成璐再补信息。

## 验收标准
- [ ] 给出 1 条可直接粘贴的触发指令（中文，含目标/起点/批次/判据/状态回写）
- [ ] 指令引用的文件路径全部真实存在（已验证：episodes.md / status-table.md / sop/01）
- [ ] 明确告知：本会话无法代操作目标会话 goal，必须由成璐在目标会话发这句话

## 为何这是合理的一步
"创建 goal"这个动作本身只能在目标会话执行（goal 绑定会话）。本会话能做的最大价值 = 把触发指令写到可直接粘贴的完成度，并核实所有前提文件在位。
