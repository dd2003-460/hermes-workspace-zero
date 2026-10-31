# Step 01：创建 goal（五字段 + 链路规则 + 永不停止条款）并验证落库

## 目标
按 `agents/goal-template.md` §1 五字段格式创建「推进寿命正交贡献排序研究（GitHub 仓 dd2003-460/longevity-orthogonal-contribution）阶段2 MR 实际执行」goal，objective 内置完整链路规则（§1-§5）与「complete 后同回合扫仓找下一个可推进工作并 create 新 goal，永不停止」条款；get_goal 回读验证防 runtime 钳制。

## 涉及文件
- 读：`workspace/agents/goal-template.md`（模板）、`workspace/agents/acp-rules.json`（6 条硬规则）、`projects/健康长寿/D1-longevity-orthogonal/loop-state.json`（legacy.goal_text 五字段底稿可复用）
- 写：`projects/健康长寿/D1-longevity-orthogonal/loop-state.json`（legacy 节追加 goal 落库记录：goal id、objective 摘要、max_goal_rounds、日期；不动已有键）

## 做法
0. **幂等（现状：goal 已存在）**：先 `get_goal` 回读——若本任务已有 active goal（现状：goal-aeb926f3，armed，max_goal_rounds=30，已在本计划 step-01 执行时落库），则**不新建**，只回读核对五字段 + 链路规则 + rounds 值，验证结果记入 loop-state.json；仅当不存在 active goal 时才 `create_goal`。
1. 以 loop-state.json → legacy.goal_text 为底稿，五字段齐全：【目标】【阶段】【SOP 索引】（arena-loop-pipeline + loop/prompt-first/01-04.5 + 预注册稿 + stage2_mr.R）【验收标准】（机器可查六条，禁用"完整/充分"）【失败降级】（arena→本地 conf-0.2；R 失败→miniforge；无 token→open-data 子集；门禁不过→gate-fail 结案不降级）。
2. objective 末尾追加【链路规则】：① 严格 1-loop 六阶段逐阶段落盘 loop-artifacts/stages/<N>/，pass 才进下一阶段；② 调研/核验/复核默认外包 arena，降级不豁免 loop；③ 每步 2-loop（备份→执行→review/verify→提交）；④ goal 完成必须 commit+push；⑤ **永不停止**：complete 后同一回合扫仓找下一个可推进工作并 create 新 goal（新 goal 必含本链路规则），仅仓内确无可推进工作且已记录才允许 blocked。
3. `create_goal`（max_goal_rounds=30）→ 立即 `get_goal` 回读，核对五字段与 rounds 值（模板 §3 规定 runtime 会静默钳制）。
4. 读 `agents/acp-rules.json`：本会话工具列表无 `acp_rule` 工具 → 按模板 §3「工具不存在则跳过」，跳过事实一行记入 loop-state.json。

## 验收标准
- get_goal 返回 objective 含五字段 + 链路规则⑤（永不停止条款原文可 grep）；max_goal_rounds=30（如实记录钳制值）。
- loop-state.json `python3 -c "import json;json.load(open('...'))"` exit=0 且含新 goal 记录。