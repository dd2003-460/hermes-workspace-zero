# origin: ai

# arXiv:2608.27734 直验报告（03 阶段 T01 节点）

- **观察时间**：2026-10-17（Asia/Shanghai，主机真实日期）
- **任务**：用 bash curl 直验 arXiv:2608.27734 编号真实存在性（02 阶段 stability-criteria.md 的关键引用源）
- **节点**：`03-r1-node-T01` / orthogonal_key=`arxiv-verify`

---

## verdict: **exists**

**confidence: 0.95**

编号 arXiv:2608.27734 **真实存在**。标题/作者/日期/摘要要点与 stability-criteria.md（C8、C10、§建议输入）所引用的内容**逐项一致**，无需降级处理。

---

## 1. 元数据（经 HTTP 200 页面核验）

| 字段 | 值 | 来源 |
|---|---|---|
| 标题 | What survives honest evaluation? Leakage-safe, search-aware assessment of LLM-driven trading strategy discovery | export.arxiv.org/abs + arxiv.org/abs |
| 作者 | Eray Gençay（单一作者） | `<meta name="citation_author" content="Gençay, Eray">` |
| 提交日期 | 2026-08-27（v1，Thu, 27 Aug 2026 21:50:28 UTC，343 KB） | `<meta name="citation_date" content="2026/08/27">` + dateline |
| 主分类 | Statistical Finance (q-fin.ST)；父类 q-fin | Subjects 元数据 |
| arXiv ID | 2608.27734 | `<meta name="citation_arxiv_id">` |
| DOI | https://doi.org/10.48550/arXiv.2608.27734 | abs 页面 DataCite 链接 |
| URL | https://arxiv.org/abs/2608.27734 | 官方 canonical |

> 注：提交日期 2026-08-27 与 stability-criteria.md line 84 所记 "2026-08-27" 完全一致；作者 "Gençay" 一致；分类 q-fin.ST 与 line 66（MinervaScore 同列 q-fin.ST 语境）一致。

## 2. 摘要要点（curl 原文抓取，非虚构）

1. **问题**：LLM 用于发现交易策略的文献普遍有方法学弱点——生成大量候选策略、只报告最优者，且既不修正 look-ahead bias，也不修正搜索强度（search intensity）。
2. **修正一（结构性，非程序性）**：agent 只能通过"注册表校验的工具"行动，其**特征空间按构造排除 look-ahead**。该护栏**与统计校正不冗余**——原话："a deliberately leaky oracle posting a Sharpe ratio of 35 survives Deflated Sharpe and probability-of-backtest-overfitting testing completely"（故意泄漏的 oracle，Sharpe=35，能完整通过 DSR 与 PBO 检验）。
3. **修正二（trial-count deflation）**：系统记录搜索执行的**每一次**策略评估，并按该试验次数（trial count）deflate 所有报告绩效；追踪最优 in-sample Sharpe 随每次试验爬升、而由 agent 自身搜索驱动的 deflation 阈值爬升更快。
4. **实证范围**：453 只 point-in-time 美股 + 39-ETF 多资产宇宙，含真实交易/冲击/借券成本。
5. **结果**：honest evaluation **认证被动基准**（OOS 置信区间不含零），**拒绝所有 LLM 发现的策略**（两个前沿模型、搜索预算 ≤100 候选、5 次重复运行），并通过互补工具捕捉 selection luck / 预测 rank 退化 / OOS 崩溃；并用相同工具评估一位人类交易员的生产规则系统。
6. **形式化**：论证为何**预注册假设的证据门槛低于暴力搜索**；并量化"可信认证中等 edge 实际所需样本量"。

## 3. 原始 curl 证据（关键响应片段）

**命令 1**：`curl -sL "https://export.arxiv.org/api/query?id_list=2608.27734"`（arXiv API，最可靠通道）
- 响应：`Rate exceeded.` **[HTTP_CODE:429] [SIZE:14]**（API 限流，重试 2 次仍 429）
- 判定：API 通道本次不可用（限流，非 404/error），**不构成 not_found 证据**；改用 abs 页面（arXiv 官方同源数据）。

**命令 2**：`curl -sL "https://export.arxiv.org/abs/2608.27734"`
- 响应 **[HTTP_CODE:200] [SIZE:43008]**，`<title>`：
  ```
  [2608.27734] What survives honest evaluation? Leakage-safe, search-aware assessment of LLM-driven trading strategy discovery
  ```
- 关键 citation meta（原样抓取）：
  ```
  <meta name="citation_title"  content="What survives honest evaluation? Leakage-safe, search-aware assessment of LLM-driven trading strategy discovery" />
  <meta name="citation_author" content="Gençay, Eray" />
  <meta name="citation_date"   content="2026/08/27" />
  <meta name="citation_arxiv_id" content="2608.27734" />
  <meta name="citation_pdf_url" content="https://arxiv.org/pdf/2608.27734" />
  ```
- 页面 dateline：`[Submitted on 27 Aug 2026]`；submission-history：`[v1] Thu, 27 Aug 2026 21:50:28 UTC (343 KB)`
- 页面含完整 abstract（与 §2 一致）、Subjects=`Statistical Finance (q-fin.ST)`、DataCite DOI 链接。

**命令 3（变体，arxiv.org 主域二次独立确认）**：`curl -sL "https://arxiv.org/abs/2608.27734"`
- 响应 **[HTTP_CODE:200]**，grep 命中：
  ```
  <title>[2608.27734] What survives honest evaluation? Leakage-safe, search-aware assessment of LLM-driven trading strategy discovery</title>
  <meta name="citation_title"  content="What survives honest evaluation? ... discovery" />
  <meta name="citation_author" content="Gençay, Eray" />
  <meta name="citation_date"   content="2026/08/27" />
  <meta name="citation_arxiv_id" content="2608.27734" />
  ```

**判定链**：两个独立 arXiv 官方域（export.arxiv.org + arxiv.org）abs 页面均 HTTP 200 且元数据自洽一致 → **exists**。API 429 仅为限流，非编号错误证据。

## 4. 与 02 stability-criteria 候选判据集的关系

**（a）是否属于该判据集？** —— **是，属于且是承重引用源。**
stability-criteria.md 在 3 处引用 arXiv:2608.27734：
- **C8**（line 84）：列作 DSR/PBO/PSR + CSCV "规范三件套"的**可核验应用来源3**（trial-count deflation 实践 + 453 美股/39-ETF 实证 + 预注册 vs 暴力搜索）。
- **C10**（line 98）：列作"统计门槛防不住未来信息泄漏"的**来源1**（leaky oracle Sharpe=35 完整通过 DSR/PBO）。
- **§对阶段03的建议输入**（line 126）：验证栈第一层"结构性 point-in-time（前提，统计门槛防不住泄漏，arXiv:2608.27734）"。

**（b）强化还是削弱 02.5 的 0.85 置信度判断？** —— **强化，不削弱；引用字段无需降级。**
- 本核验确认该编号**真实存在**，且 curl 抓取的**标题/作者/日期/摘要要点与 stability-criteria.md 所记逐项一致**（尤其 C10 引用的原话 "a deliberately leaky oracle posting a Sharpe ratio of 35 survives ... completely" 在摘要中逐字出现）。
- 因此 02.5 若以 0.85 置信度依赖此引用（"统计门槛不能替代结构性 point-in-time"这一层），**该证据链成立且被强化**：承重源可核验、内容无矛盾。
- **降级处理：不需要。** 若此编号为 not_found，则 C8/C10/§建议输入 第一层"结构性 point-in-time 是前提"论证失去主承重源，0.85 置信度须显著下调——但该情形未发生。

> 诚实边界：本节点 input_refs 仅含 `stability-criteria.md`（02 阶段），**未直接读取 02.5 交叉验证回执文件**，故 "0.85" 这一具体数值未在本文档中二次核对；本文结论基于"该引用真实存在且内容一致"这一可核验事实，推断其**强化**（而非削弱）任何建立在该引用之上的 02.5 置信度。若需精确核对 0.85 数值本身，应另派节点直读 02.5 回执。

## 5. 结论

- **verdict = exists**，**confidence = 0.95**（两个独立 arXiv 官方域 HTTP 200 自洽确认；仅 API 通道限流，无矛盾证据）。
- 对 02.5：0.85 置信度所依赖的承重源**真实且内容一致** → 该判断**被强化**，引用字段**无需降级**。
- 对阶段03：C8 第三层验证栈（按 trial count deflate）与 C10 第一层结构性 point-in-time 论证的主承重源已核验成立，可继续作为设计依据。

---

## §Lead 内联补验（PDF 正文级，2026-10-17 15:53）

方法：curl arxiv.org/pdf/2608.27734（713,635 B, PDF 1.7）→ pdftotext（1007 行）→ grep 定位。

| claim | 正文位置 | 判定 |
|-------|---------|------|
| C10 "deliberately leaky oracle posting a Sharpe ratio of 35 survives Deflated Sharpe and probability-of-backtest-overfitting testing completely" | txt L21-22 逐字命中 | ✅ 正文级 |
| C8 "453-stock point-in-time US equity universe and a 39-ETF multi-asset universe" | txt L26, L405 | ✅ 正文级 |
| C8 trial-count deflation（"records every strategy evaluation its search performs and deflates all reported"） | txt L23, L88, L91 | ✅ 正文级 |
| PBO 章节（Bailey et al. 2014, §4.2 Probability of backtest overfitting） | txt L89, L128, L333 | ✅ 正文级 |

**验证层级升级**：摘要级 → **PDF 正文级**。原"摘要级残留"关闭。
**残余（provenance，非正确性）**：arXiv 单一库两镜像（export.arxiv.org + arxiv.org），无第三方独立索引交叉（Semantic Scholar 等）；撤稿风险未复查（概率低）。此残余记入 T08 gap 列表。
# origin: ai (Lead 内联, 2026-10-17)
