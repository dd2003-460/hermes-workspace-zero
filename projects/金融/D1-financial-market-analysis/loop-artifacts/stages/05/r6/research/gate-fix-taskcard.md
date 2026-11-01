# F10-R3 门禁修复任务卡

仓库: dd2003-460/hermes-workspace-zero @ arena/f10-r3-gate-fix (从 main 拉)
产出: research/A.md 和 research/D.md 各补 ≥1 条独立证据行 + receipts.json subdomain_gate 重算

## A 域缺口 (当前 4/5)

现有 4 线: Farmer(2002) / Brock-Hommes(1998) / Scholl-Calinescu-Farmer(2021) / 第4线(见A.md §2)
缺: 第5条独立团队证据。候选方向:
- Challet & Bouchaud (统计物理视角的 trader ecology, arXiv cond-mat)
- Egorov et al. 或类似的 order book ABM 预测偏离持续时间的论文
要求: 不同作者团队 + 可核验来源(arXiv DOI / 出版方页) + ≤8行摘要

## D 域缺口 (当前 2/3)

现有 2 线: 两篇预印本为同一作者 Part I/II 只算1线 + 日历型数据源1线
缺: 第3条独立团队证据。候选方向:
- Griffin & Shiller (forced selling / liquidity spirals, JFE 2013)
- 或其他 forced flow prediction 的已发表实证 (非预印本优先)
要求: 同上

## 交付格式

直接在 A.md / D.md 的 §2 证据列表追加条目 (保持现有编号风格), 
更新 receipts.json: independent_lines +1, gate 重算, commit_sha 回填。
每条新证据必须带 URL + 日期 + 团队名。

## 执行记录 (2026-11-01, arena agent mode)

- 落盘: `A.md` §2 新增 **A7** (Tóth/Lempérière/Deremble/de Lataillade/Kockelkoren/Bouchaud 2011, PRX 1:021006) ; `D.md` §2 新增**行 8** + **D8 条目** (Coval & Stafford 2007, JFE 86(2):479-512)
- 候选替换 (两处候选均检索不到, 如实登记, 未虚构出处):
  - A: "Challet & Bouchaud (trader ecology)" — 无联合署名文献 (Challet 的订单簿 ABM 合作者为 Stinchcombe) → 改用 CFM/Bouchaud 组 PRX 论文 (arXiv 摘要页 + DOI 双路核验)
  - D: "Griffin & Shiller (2013, JFE, forced selling)" — 无此文献 → 改用 Coval & Stafford (2007) JFE (已发表、非预印本, 摘要直核)
- 门禁: A **5/5 pass** · D **3/3 pass**; 行数约束 A=80 / D=61 (≤80 ✓)
- 计数口径已写入 `receipts.json` 的 `subdomain_gate.A/D.counting_rule`, 可审计 (保守: A5 动理学、Ni-Pearson-Poteshman、Cheng-Madhavan 仍不计入线数)
