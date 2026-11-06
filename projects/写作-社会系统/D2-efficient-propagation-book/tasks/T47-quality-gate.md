【执行前必读】
1. 本任务必须走 1-loop：先读 sop/arena-loop-pipeline.md + loop/prompt-first/00..04.5
2. 每阶段产出落盘 loop-artifacts/stages/<N>/
3. 完成后 commit + push
4. 通道故障 → 报告 Lead 降级，不得静默跳过

# T47: D2 全书质量门禁（drift-check + 交叉引用）

## 目标
对 15 章跑 drift-check + 交叉引用检查，产出 quality-gate-report.md。

## 执行步骤（纯本地，Lead 直接执行）

1. `for f in drafts/*.md; do python3 ../AI-计算科学/D1-persona-align/scripts/drift-check.py "$f" | tail -3; done`
2. 汇总分数表 → report §1
3. grep "第.*章" 提取所有章间引用 → 核对目标存在 → report §2
4. <90 章节：定位漂移句 + 修复建议 → report §3
5. git add + commit + push

## 验收
- [ ] 15 行分数表 (chapter × score × signals)
- [ ] 每个 <90 有句子级修复建议
- [ ] broken_refs = 0 或列出
- [ ] report committed + pushed
