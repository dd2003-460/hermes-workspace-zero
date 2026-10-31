# Step 06：阶段 02 信息调研（research_queue 6 项 + 覆盖表 T4a）

## 目标
按 stage 01 unknown 字段的 research_queue（6 项）完成一手调研，产出免凭据可组「暴露×结局」MR 覆盖表，供阶段 03 行动分解。优先外包 arena（首选通道），通道故障降级本地 conf-0.2，loop 工件仍落盘。

## 涉及文件
- 读：`loop-artifacts/stages/01/r1/fields.json`（research_queue 6 项）、`repo/data/raw/api_cache/*`（既有缓存，能复用不重查）、`repo/data/derived/cache_crossvalidation.csv`
- 写：`loop-artifacts/stages/02/r1/`（调研产出落盘：每项 queue topic 一个 md 或合并 research-notes.md + conf 标注）、`repo/data/derived/coverage_table.csv`（覆盖表：暴露×结局 pair、暴露来源/样本量、结局来源/样本量、独立来源数≥3 核验列、blocked 标记）

## 做法
2-loop：
1. **备份**：`cp -r loop-artifacts/stages/01/r1 /tmp/`（沿用 Step 05 备份即可）。
2. **执行**（每项 queue 先查本地缓存，缓存没有才联网，网络只走 ego-browser；禁 web_search）：
   - P1-①GIANT 官网（Locke 2015 BMI，ieu-a-835 等价公开包）免凭据下载路径与格式 → 记录 URL/格式/许可。
   - P1-②FinnGen R13 公开端点（含 I9_IHD 等主结局映射）免凭据摘要统计下载 → 记录端点 id 与可下载范围。
   - P1-③Biobank Japan 公开端点（bbj-a-107 等）免凭据下载 → 同上。
   - P2-④TwoSampleMR 对 FinnGen/BBJ 端点的免凭据 `get_sumstats` 行为（装完包后本地实测，Step 02 完成才可做；若 R 包未装完，记为 blocked 并降级用文档查证）→ 实测结果优先。
   - P2-⑤LDL ieu-a-300 样本量 173,082 vs 94,595 差异核实（查 Willer 2013 论文/GWAS Catalog 一手源）→ 结论写进 `repo/data/derived/ldl_sample_size_check.md`，并明确 ieu-a-300 与 ebi-a-GCST002222 选哪条进 stage2_config.R。
   - P3-⑥汇总覆盖表：可组合法 MR 对清单 + 每对「独立来源≥3」核验 + blocked 项（如 F15 抑郁 nsnp 截断）记入 execution-log。
3. **review/verify**：每项 topic 有结论 + 来源 + conf；覆盖表与 `stage2_config.R` 的 A 级暴露清单（F01/F03/F04/F08[换 ieu-a-835]/F15-blocked）对得上，无凭空暴露。
4. **提交**：落盘 `loop-artifacts/stages/02/r1/` 全部工件 + coverage_table.csv；判定 pass 才进 02.5（pass 标准：6 项全有结论且 conf≥0.7，独立源≥3 按 goal-template §4；达不到则标 blocked 项并记录，不伪造）。

## 验收标准
- `loop-artifacts/stages/02/r1/` 存在且 6 项 topic 各有落盘结论（含来源 URL/缓存引用 + conf）。
- `repo/data/derived/coverage_table.csv` 存在，行数≥1，含 blocked 列；LDL 样本量核对有明确裁决（用哪个值/哪个 accession）。
- 网络操作全部走 ego-browser（或复用本地缓存零联网），无 web_search 调用。