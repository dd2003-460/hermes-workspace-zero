# Step 09：阶段 04 执行验证（无 token 可覆盖子集 open-data 管线，Step0→Step4 逐门禁）

## 目标
按任务表实际运行 `repo/scripts/stage2_mr.R`（从未跑过，首用先 `--dry-run`），通过预注册三道硬门禁并产出 L1 单变量 MR 点估计+95%CI。每个 Step 走 2-loop（备份→执行→review/verify→提交）。

## 现状约束
- 无 OpenGWAS token（用户 2026-10-28 已决：先跑可覆盖子集）。TwoSampleMR 自 2024-05 起平台取数需 JWT → 只跑覆盖表内「开放下载」pair；缺数据项标 blocked 记 execution-log，不补造。
- R 4.6.1 已装，包需 Step 02 装完（TwoSampleMR/MVMR/MendelianRandomization/ieugwasr）。
- 预注册停止规则（repo/docs/20_方法/阶段2分析计划.md，锁死）：Step1 阳性对照 2/2 且 β>0 p<0.05；Step2 负对照全部 |z|<1.96；Step3 条件 F≥10，否则停，不报点估计；条件 F 的 gencov 不能取 0（≥2 暴露共用 UKB 直接 stop，F08 已换 ieu-a-835 规避）。
- 长任务用 setsid/disown 承载，禁裸 nohup（acp-rules ⑥）。

## 涉及文件
- 读：`repo/scripts/stage2_mr.R`、`repo/data/derived/stage2_config.R`（由 audit_instruments.py --audit 生成，C14 校验同步）、`repo/data/derived/coverage_table.csv`
- 执行命令（在 repo/ 下）：`Rscript scripts/stage2_mr.R --dry-run` → `--step 1` → `--step 2` → `--step 3` → `--step 4`（或 `--all`，任一门禁不过即停）
- 写：`repo/data/derived/session_info.txt`（Step0：R 版本+包版本/commit+日期）、各 step 输出（R 脚本落盘位置以脚本为准）、`repo/execution-log.md`（blocked 项+每步结果）、`loop-artifacts/stages/04/r1/`（执行证据落盘）

## 做法
2-loop，逐 step：
1. **备份**：每 step 前 `cp -r` 相关数据目录到 /tmp（或 git stash/commit 留回滚点）。
2. **执行**：
   - Step0：写 session_info.txt（R --version、packageVersion(TwoSampleMR 等)、TwoSampleMR GitHub commit hash、运行日期）。
   - `--dry-run` 先行：只查环境参数不取数，修掉报错。
   - `--step 1` 阳性对照 2/2 → `--step 2` 负对照 → `--step 3` 条件 F（成败点，gate_fail 硬停）→ `--step 4` L1 单变量 MR（4 暴露×覆盖内结局，IVW+MR-Egger+加权中位数）。
   - 每步跑完立即核对阈值（β/z/F 值 vs 预注册规则）。
3. **review/verify**：门禁值与预注册规则逐条对照；点估计来源独立数≥3 核验；异常值不静默丢弃，记 execution-log。
4. **提交**：每步产出落盘 stages/04/r1/ + execution-log.md 更新；门禁不过 → 停在当前步，记录失败原因，不绕过门禁。

## 验收标准
- `session_info.txt` 存在且含 R 版本/包版本/commit/日期。
- Step1/2/3 门禁值有落盘证据且全部通过（任一不过：goal 记 failure 证据，降级路径=补数据源或缩范围，不报点估计）。
- Step4 产出：每暴露×结局的 IVW+MR-Egger+加权中位数点估计+95%CI+p，落盘（CSV/JSON 以脚本输出为准）。
- `execution-log.md` 记录全部 blocked 项（含 F15 抑郁 nsnp 截断）与降级动作。