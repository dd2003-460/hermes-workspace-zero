# CONTINUE_MSG — keepalive 续推起点

## 当前状态（2026-11-03 16:10）
- **T17 full01 数据污染已确诊**（本轮最大发现）：conv0 的 ingestion checkpoint 是 10/21 smoke01 残留（user_id=locomo_0_smoke01），该 user 在 mem0 qdrant 里 0 条记忆 → conv0 全部 152 题检索为空、得分全 0。真实分数被拉低 ~24pp。
- **真实水平**：conv2+3（健康 ingestion）top_10 = **0.755 (262/347)**；temporal conv2+3 = 0.835（修复有效）。conv1 只有 10 条记忆（ingestion 残缺，checkpoint 谎报 369 chunks done），0.259 也不可信。
- runner PID 62585 健康，conv3 195/199，预计 ~1h 跑完 conv3 + ~10h 跑完 conv4-9（这些是新 ingestion，会正常）。
- 空答案率 13-15%（answerer 经 ClashX TUN 代理到局域网 vLLM 超时，smoke 时直连无此问题）——轻微噪声源，先不修。
- pfb：blocked_human（web-llm 登录 ≥2 回执）不变。F8：done→monitoring。decomp：稳定。

## 下一步（下次唤醒从这里接）
1. **等 runner 退出后做 T17-full 收口分析**（脚本已备好逻辑，直接重算）：
   - 排除 conv0/conv1（污染）后的 overall / by-category / temporal 分数
   - 对照表：smoke01(0%) vs smoke-temporal-quick(100%@5题) vs full01 conv2+3(0.835@130题)
   - 结论落盘 `tools/memory-benchmarks/results/locomo/locomo-full01-analysis.md` + decomp loop-state 更新 + commit
   - 判定：temporal 目标线 ≥50% 是否达标（按当前趋势大概率达标，以全量为准）
2. **conv0/conv1 补跑决策**：~10h 新 ingestion + ~3h 答题。建议成璐拍板要不要为完整 10-conv 数字补跑；不补的话报告里明确标注"有效样本 conv2-9"。
3. F8-4 等 IV ≥90 天；G1 等 pfb；候选池 #2 起草可顺手做。

## 授权边界（不变）
可逆直接做；不可逆偏好不明写 APPROVALS 跳过；红线不碰。