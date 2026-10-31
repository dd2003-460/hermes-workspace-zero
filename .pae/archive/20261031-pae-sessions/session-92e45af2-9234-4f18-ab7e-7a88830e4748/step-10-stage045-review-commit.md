# Step 10：阶段 04.5 反方复核 + 完整性自检 + commit/push

## 目标
对阶段 04 的全部产出做独立反方复核（找方法学漏洞/门禁绕过/数据伪造风险），运行 `verify_integrity.py` 全量自检，全部通过后 commit + push 到 GitHub main（goal-template §3：goal 完成必须 commit+push）。

## 涉及文件
- 读：`loop-artifacts/stages/04/r1/*`、`repo/execution-log.md`、`repo/data/derived/coverage_table.csv`、预注册稿 `repo/docs/20_方法/阶段2分析计划.md`
- 写：`loop-artifacts/stages/04.5/r1/review-notes.md`（反方复核意见 + 裁决）、`loop-artifacts/stages/04.5/r1/verdict.json`（pass/fail + 理由）、必要时回改 stage04 产出
- 执行：`python3 repo/scripts/verify_integrity.py`（C14 校验 stage2_config.R 与 audit_instruments.py 同步等全部检查）

## 做法
2-loop：
1. **备份**：`cd repo && git status` 确认改动清单，先 commit 一个「stage04 完成」快照（回滚点），再复核。
2. **执行**：
   - 反方复核（独立视角，优先外包 arena；不可用则本地自答 conf-0.2 并在 review-notes 标注）：逐条质询——门禁是否被绕过（gencov=0？UKB 重叠暴露？）、负对照阈值用对没有（|z|<1.96）、独立来源≥3 是真独立（非同一研究两条记录）、blocked 项有没有被补造数据、LDL 用哪个样本量/哪个 accession 与裁决一致。
   - `python3 scripts/verify_integrity.py` → exit=0。
3. **review/verify**：review-notes 每条意见有裁决（fix/accept/risk-accepted+理由）；verify_integrity exit=0；`git diff` 无意外文件（不提交 /tmp、密钥、大数据文件）。
4. **提交**：`git add -A && git commit`（commit message 含阶段号+日期）→ `git push origin main` → push 成功后记录新 HEAD hash 到 workspace `tasks/` 验证文件（断点 A 验证证据）；push 失败（403/credential）→ 记 knowledge/efficiency-bottlenecks.md，降级 GitHub REST API 或 gh 重新认证，不静默跳过。

## 验收标准
- `verdict.json` = pass（反方意见全部裁决）；`verify_integrity.py` exit=0（可机器检查）。
- GitHub main 新 HEAD ≠ 5d64174，commit message 含阶段标识，hash 已记录到 workspace 验证文件。
- 若 verdict=fail：回改 stage04 后重跑 04.5，不直接 complete goal。