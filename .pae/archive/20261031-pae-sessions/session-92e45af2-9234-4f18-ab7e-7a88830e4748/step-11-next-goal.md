# Step 11：goal 验收 → complete → 同回合扫仓找下一可推进工作 → create 新 goal（永不停止）

## 目标
按 goal-template §5 生命周期收口当前 goal（goal-aeb926f3）：验收标准逐条核对 → `update_goal complete` → **同一回合**扫描仓库找下一个可推进工作 → `create_goal` 新 goal（objective 必含完整链路规则，不得只写「继续优化」）。仅当仓内确无可推进工作且已落盘记录时才允许 `blocked`（须满足连续 3 轮同一阻塞条件）。

## 验收核对（当前 goal 的【验收标准】，逐条可机器检查）
1. `session_info.txt` 含 R 版本+包版本/commit+运行日期（ls + grep）。
2. Step1 阳性对照 2/2 β>0 且 p<0.05（stage04 落盘值）。
3. Step2 负对照全部 |z|<1.96。
4. Step3 双变量条件 F≥10（F08 用 ieu-a-835）。
5. Step4 L1 点估计+95%CI+p，每暴露≥3 独立来源。
6. `verify_integrity.py` exit=0 且 push 成功（新 HEAD hash 已记录）。

## 下一 goal 候选（按 P2 完成度低优先 + 预注册 Step 顺序）
- **首选：Step 5 L2 MVMR 主分析**（含教育协变量，用 ieu-a-1239 之外的配置化教育暴露——注意原硬编码 ieu-a-1239 已删，须从 stage2_config.R 读）+ 东亚轨对照（FinnGen/BBJ 东亚端点对照欧洲主轨）。前置：本 goal 的 Step0-4 全过。
- 备选：F15 抑郁（ieu-a-1187）nsnp=10000 截断问题修复后补跑；T4b 覆盖外数据源补 token 后全量 MR；东亚轨资源深化（repo/data/raw/api_cache/east_asian_* 既有缓存）。

## 做法
1. 逐条核对验收（grep/ls/python 可检查，不凭记忆）。
2. `get_goal` 回读确认 id/revision → `update_goal {goal_id, revision, action:"complete"}`。
3. **同一回合**：扫 `tasks/decomposition.md`/`loop-state.json`/repo 结构（field-apply 路径已废弃，不再用 ralph CLI 任务命令），选下一个任务（首选 Step 5）。
4. `create_goal`（max_goal_rounds 按新任务量定，如 30），objective 必须含：完整五字段（【目标】【阶段】【SOP索引】【验收标准】量化【失败降级】）+ 链路规则 5 条（①严格 1-loop 六阶段落盘 loop-artifacts/stages/<N>/，pass 才进下一阶段；②调研/核验/复核默认外包 arena，故障降级本地 conf-0.2 不豁免 loop；③每步 2-loop 备份→执行→review/verify→提交；④goal 完成必须 commit+push；⑤永不停止：complete 后同回合扫仓找下一可推进工作并 create 新 goal）。
5. `get_goal` 回读验证落库值（防 runtime 静默钳制 max_goal_rounds）。

## 验收标准
- `update_goal complete` 成功（get_goal 显示 phase 非 active 或等价完成态）。
- 新 goal 已落库（新 id，max_goal_rounds 与提交值一致，objective 含完整链路规则）。
- 若仓内确无可推进工作：落盘记录（扫仓证据）后才允许 `blocked`，blocked_reason 写明具体阻塞条件。