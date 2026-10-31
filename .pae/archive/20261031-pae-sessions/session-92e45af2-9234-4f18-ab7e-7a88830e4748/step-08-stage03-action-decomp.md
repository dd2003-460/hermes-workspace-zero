# Step 08：阶段 03 行动分解（更新 decomposition.md + 任务表）

## 目标
基于阶段 02 覆盖表与 02.5 交叉验证结论，更新项目 `tasks/decomposition.md`（分解树 + 正交性核对 + 空缺清单 + 任务表），把阶段 04 要执行的任务逐条写成可派发、可验证的原子任务。规划纪律（m02353）：派发只执行任务表内条目。

## 涉及文件
- 读：`tasks/decomposition.md`（现有 T1-T9）、`repo/data/derived/coverage_table.csv`、`loop-artifacts/stages/02/r1/*`、`repo/docs/20_方法/阶段2分析计划.md`（预注册 Step0-6，禁跳步）
- 写：`tasks/decomposition.md`（更新任务表：标记 T1/T2 实际状态，T4a 由本 goal 阶段02 收口，T3-T9 细化为执行级原子任务并标注依赖/并行）、`loop-artifacts/stages/03/r1/`（行动分解落盘）

## 做法
2-loop：
1. **备份**：`cp tasks/decomposition.md /tmp/decomposition.bak-$(date +%H%M)`。
2. **执行**：
   - 依覆盖表裁决：无 token 下实际可跑的暴露×结局组合（F01/F03/F04/F08[ieu-a-835] × 覆盖内结局），不可跑项标 blocked。
   - 更新任务表：T1（R 包，Step 02 完成后标 done/failed）→ T3 Step0 环境锁定（session_info.txt：R 版本 + 包版本/commit + 日期）→ T5 Step1 阳性对照 2/2 → T6 Step2 负对照 → T7 Step3 条件 F（双变量：戒烟 ukb-b-20261 + BMI ieu-a-835，gencov 硬门禁）→ T8 Step4 L1 单变量 MR（4 暴露×结局，IVW+MR-Egger+加权中位数，每暴露≥3 独立来源）→ T9 verify_integrity.py exit=0 + commit + push。
   - 标注依赖（Step 顺序不许跳步）与可并行项（如 4 个暴露的 L1 可并行跑）。
3. **review/verify**：任务表每行含「任务/输入/输出/验收/状态」；与预注册计划 Step 顺序一致；blocked 项与 coverage_table 一致。
4. **提交**：落盘 stages/03/r1/，判定 pass 才进 04。

## 验收标准
- `tasks/decomposition.md` 任务表覆盖 Step0→Step4 全部执行级任务，无「完整/充分」类不可验证表述。
- 预注册顺序（Step0-6 不许跳步）在任务表依赖列中显式体现。
- 阶段 04 每个执行动作都能对应到任务表某行（规划纪律可抽查）。