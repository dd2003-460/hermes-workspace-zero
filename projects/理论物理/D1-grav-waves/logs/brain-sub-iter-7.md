# Brain-Sub Iteration 7 — 质询报告

**执行者**：Brain-Sub (Auto)
**执行时间**：2026-07-01 14:30
**上下文**：2-loop complete, v6 tarball ready, awaiting human arXiv upload

---

## 质询

### Q1: DistCat 并行准备 Checklist

在等待 D1 arXiv ID 期间，DistCat 可以做的准备工作：

1. **D1 arXiv ID 占位**：DistCat 的 tex 中用占位符引用 D1，格式如 `arXiv:YYYY.nnnnn (Cheng Lu, forthcoming)`
2. **DistCat 论文框架搭建**：
   - 选择合适的 LaTeX 模板（与 arXiv math.CT 分类兼容）
   - 确定论文结构：引言、数学框架、应用、结论
   - 准备引言中对 D1 的引用段落
3. **参考文献收集**：收集 D1 参考文献之外的新文献（范畴论在引力波中的新应用）
4. **arXiv 分类确认**：math.CT + gr-qc 是否合适？还是需要考虑 math.AG？
5. **作者信息确认**：与 D1 相同的作者结构？

**风险**：如果在 D1 arXiv ID 获取前完成了 DistCat 全部论文，仅差一个引用，需要最后更新一次。这是小工作量，但心理成本可能造成拖延。

**建议**：先完成 DistCat 的 90%（所有章节内容），引用 D1 处用占位符。D1 上线后 30 分钟完成引用更新。

### Q2: arXiv 提交后策略

arXiv 提交流程通常：
- 提交后 1-5 分钟自动分类（莫不需要人工审查）
- gr-qc 分类通常需要人工审查，时间 1-3 个工作日
- 常见问题：分类错误 → arXiv 会通知修改
- 审查意见可能要求修改标题/摘要以匹配内容

**策略**：
- 提交后 48 小时内定期检查邮箱（包括 spam folder）
- 如果收到修改要求，通常在 24 小时内回复
- 如果 5 个工作日无回应，发邮件到 arXiv support

### Q3: Abstract 格式风险

论文 abstract 中有两处使用 `\textbf{}`：
- 第34行：`\textbf{Information-theoretic perspective:}`
- 第32行：`\textbf{We present a formalism...}`

arXiv 会在 HTML 页面中渲染这些 `\textbf`，使得 abstract 第一段和 perspective 段变得**加粗显示**。这看起来不像标准 arXiv abstract。

**建议**：
- 方案 A：去掉 abstract 内的 `\textbf`，改用普通文本（safest）
- 方案 B：保留但加上注释说明（可能对 arXiv 审查无影响）
- 方案 C：为 arXiv 准备一个不带 `\textbf` 的 abstract 版本

**推荐**：方案 A。abstract 内部加粗不是 LaTeX 最佳实践。

### Q4: 双重 license 问题

论文包含两个 license 声明：
1. Abstract 内的 `\textbf{License}: This work is licensed under CC BY 4.0`
2. arXiv 提交时的 license dropdown（需要选择）

arXiv 支持 CC BY 4.0（作为 2021+ 新增选项）。如果论文内 CC BY 4.0 与 arXiv 选择的不一致，会造成混淆。

**建议**：arXiv license 选择 "CC BY 4.0" 以匹配论文内容。

---

## 盲区

### B1: arXiv 查重 sensitivity

D1-grav-waves 引用了大量 arXiv 已有论文。arXiv 的 similarity report 对比的是：
- arXiv 上已发表的论文（约 200 万篇）
- 如果引用方式与原始论文高度相似（如直接复制摘要或定理陈述），可能触发

**重点关注**：
- NANOGrav 15-year data 的描述部分（Agazie:2023 已被大量引用）
- AQFT 框架的理论陈述（Brunetti:2003 已被引用数百次）
- HD 相关性函数的标准定义

**缓解**：使用自己的表述方式，确保引用公式的措辞与原始论文不同。

### B2: 论文中没有 numerical data / code

arXiv gr-qc 论文通常包含数值计算结果、仿真代码或公开数据集。D1 是纯理论论文（categorical framework），缺少数值验证。

**风险**：这不影响 arXiv 接受（理论论文完全可以没有数值结果），但可能影响 citability 和读者兴趣。

**建议**：DistCat 中可以考虑加入数值验证或与已有 PTA 数据的定量对比。

### B3: "Extended Functorial QFT" 的原创性声明

论文标题和引言中反复使用 "extended functorial QFT framework" 和 "reformulates" 等词汇，暗示这是对已有框架的重大改进。arXiv 和 gr-qc 社区可能对"reformulation"类论文的贡献度有额外 scrutiny。

**风险**：审稿人可能质疑 — 这是否真正改变了物理预测？还是只是用不同数学语言重新表述了已知结果？

**注意**：这不是 arXiv 拒稿理由（表述转换是合法的），但可能影响学术影响力。

### B4: CC BY 4.0 license 对 arXiv 的影响

CC BY 4.0 是一个强版权 license — 它要求**署名**且允许**商业使用**。对于学术论文：
- 大多数 arXiv 论文默认使用 "non-exclusive copyright to author"
- CC BY 4.0 可能导致后续期刊投稿时的版权冲突（journal 通常要求 exclusive copyright）
- JCAP/Nature/PRD 等期刊对已预印本在 CC BY 下的论文有不同的政策

**重要风险**：如果未来计划将这篇论文投稿到 JCAP 或 PRD，CC BY 4.0 可能与期刊版权要求冲突。

**建议**：
1. 投稿前从 arXiv 撤稿（不推荐，arXiv 不允许撤稿）
2. 投稿时与期刊编辑沟通预印本 license 差异
3. 考虑使用更宽松的 license（如作者自选）

### B5: arXiv 论文版本更新

一旦 D1 获得 arXiv ID，未来可能需要进行修改：
- arXiv v1 是正式版本，不可修改（但可提交 v2）
- v2 会保留 v1 的记录
- 如果发现了错误（如 citation 错误），v2 是常规操作

**建议**：提交前确保所有引用格式正确，避免 v2 是 best practice。

---

## 总结

| # | 质询 | 风险等级 | 建议 |
|---|------|----------|------|
| Q1 | DistCat 并行准备 | 中 | 先完成 90%，引用占位，D1 上线后 30min 完成 |
| Q2 | arXiv 提交后策略 | 低 | 定期检查邮箱，48h 内响应修改要求 |
| Q3 | Abstract 加粗格式 | 中 | 去掉 \textbf，避免非标准渲染 |
| Q4 | License 冲突 | 高 | arXiv 选择 CC BY 4.0 匹配论文 |
| B1 | 查重 sensitivity | 中 | 用自己的表述重述常见内容 |
| B2 | 缺少数值验证 | 低 | 理论论文可接受 |
| B3 | 原创性声明 | 中 | "reformulation" 可能被质疑贡献 |
| B4 | **CC BY 4.0 vs 期刊版权** | **高** | 投稿 PRD/JCAP 前需解决版权冲突 |
| B5 | 版本更新策略 | 低 | 提交前确保引用完整 |

**最高优先级修复**：
1. **Q3**: abstract 中 `\textbf` 应去除 — 已解决: no, need to fix
2. **B4**: CC BY 4.0 可能阻碍期刊投稿 — 需要决策
3. **Q1**: DistCat 并行准备启动
