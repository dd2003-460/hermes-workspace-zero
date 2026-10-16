origin: ai
time: 2026-09-29T20:45+08:00
stage: 04 / round: r4 / status: 3 isolated re-probes RUNNING (D-r2, E-r2, C-r3)

# r4 = 实现 ≥2-clean 规则（一手）

## 已真实做的本 round
1. 一手确认浏览器有：`ego-browser --version` exit=0（chromium 152）。
2. 一手确认喂目标句存在：goal_C/D/E.txt 三句一字一致与已落工件。
3. 启动 3 并行完全-naive 隔离执行者（general-purpose/haiku），各只喂 prompt_fed.md + 该域 goal + harness_rules.md，禁读其他路径、禁写。
   - D 语言 rerun → 目标 D 2/2
   - E 软件交付 rerun → 目标 E 2/2
   - C 理财 rerun#3 → 目标 C 2/2（r2 为 defective 样本，不计）

## 判定标准（我落结果后一手 parse 才填）
- 每 probe 须：tool_use=0 且 §0 echo 一字不改 且 自名量 P 来源逐字回写 且 零补造数值/名称 且 ≤3000字节。
- 缺任何 ⇒ revise，记 defect class。

## 结果（一手，本 round 收）
- D `a827ff53` = 环境未提供（API 超时, raw 不可回收）。
- C `a5eca00a` = 环境未提供（API 超时, raw 不可回收）。
- E `a80c0075` = invalid：执行者收到无任务文本（harness 喂 bug），做只读状态核实不分解。

## 已修（测试者侧，一手落）
- **判准自矛盾**（E 一手发现）：prompt 第7步强制浏览器调用 vs 旧 gate 要求 tool_use=0 ⇒ 两不可同时满足 ⇒ 之前所有"clean"样本缺第7步那一腿（=5-r1 已记副作用）。fix = gate 改「允许工具={读两文件,读goal,ego-browser第7步}, tool_use恰=1且=第7步」落 /tmp/fed/harness_rules.md ✓。
- **账无单文件**（红线5）⇒ 落 tasks/04-ledger.md ✓。

## 阻塞（精确）
1. r4 三 run 皆 invalid（2 API 超时 + 1 喂 bug）⇒ 零进展到 2/2。
2. round87–98 我输出退化连续"把"循环 = 模型采样故障（非任务缺陷）。
3. 下一步须 relaunch 后 fix；若 API 仍超时 ⇒ 该域记 env-blocked，不伪造样本。

## 下一步
- 收到通知 ⇒ 一手 parse 三 raw answer ⇒ 落 03d-result-r2 / 03e-result-r2 / 03c-result-r3 ⇒ 更新 ledger ⇒ 若三 PASS 则 D2/2 E2/2 C2/2 且 DONE（待用户打分）。
