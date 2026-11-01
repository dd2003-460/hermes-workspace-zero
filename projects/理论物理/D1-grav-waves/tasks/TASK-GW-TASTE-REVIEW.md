# TASK-GW-TASTE-REVIEW — 引力波论文顶刊 taste/方法/背景审查

**origin: ai** · 2026-11-02 · Lead 派发，arena 执行

## [任务]
以同行评审视角（对标 PRL/PRD/JCAP 近 3 年已发表论文），对 `projects/理论物理/D1-grav-waves/papers/2026-GW-BacQFT/GW-BacQFT-paper.tex` 做三类审查：taste、方法、背景。产出具体差距清单 + 修复建议。

## [背景]
- 论文标题：An Extended Functorial QFT Framework for Gravitational-Wave Source Discrimination in Pulsar Timing Arrays
- 目标期刊级别：JHEP/ApJL/PRL
- 核心主张：(1) HD 相关函数可从 extended functorial QFT 公理重新推导；(2) 不同 GW 源类对应不等价代数态，可用总变差距离判别；(3) SMBHB 各向异性 ∝ N_src^{-1}（泊松散粒噪声）vs 宇宙学本底固定 ~10^{-5}
- 当前状态：研究内容完成（21 轮迭代），静态审查做过一轮（12 项问题修了 10 项），但没做过顶刊 taste 审查
- 论文文件路径：`papers/2026-GW-BacQFT/GW-BacQFT-paper.tex`（514 行）
- 参考文献：`papers/2026-GW-BacQFT/GW-BacQFT.bib`（24 篇）
- PDF：`papers/2026-GW-BacQFT/GW-BacQFT-paper.pdf`（14 页）

## [约束]
- 中文回答，每条结论标 conf(0-1)，给来源 URL 或 arXiv ID
- 不确定的标"未验证"
- 审查时实际打开 arXiv 查同领域近 3 年论文（gr-qc / astro-ph.HE），看它们怎么呈现类似工作
- 重点对标：PTA 各向异性分析（Ellis 2024, Grimm 2025）、HD 函数非标准扩展（Mingolla 2023, Fujimoto 2026）、代数 QFT 在引力中的应用（Hollands/Wald 系列）
- 长度 ≤80 行（核心发现+关键数字+决策，过程论证放附录）

## [交付格式]
```markdown
# GW-BacQFT Taste Review

## 1. Taste 差距（对标 PRL/PRD/JCAP 写法）
| # | 位置(节/行) | 问题 | 对标论文怎么写 | 修复建议 | 严重度(H/M/L) |
|---|------------|------|--------------|---------|-------------|

## 2. 方法严谨性
| # | 位置 | 问题 | 风险等级 | 修复建议 |
|---|------|------|---------|---------|

## 3. 背景覆盖
| # | 缺失主题 | 为什么重要 | 应引哪篇(arXiv ID) | 加在哪节 |
|---|---------|----------|------------------|---------|

## 4. 总体判断
- 是否达到目标期刊水平：是/否/需大修
- 最致命的 3 个问题（审稿人最可能拒稿的理由）
- 修复工作量估计（小时级/天级/周级）

## 附录：对标论文清单
（列出实际查阅的 arXiv ID + 一句话说明它如何影响你的判断）
```

## [落盘约束]
文件不存在 = 任务未完成。落盘到 `projects/理论物理/D1-grav-waves/tasks/gw-taste-review.md`，然后 git add + commit + push。

## [正交性自检]
本任务只做审查+建议，不改论文本身。与 R121（文献核验）、正式矩阵（bench 实验）无重叠。