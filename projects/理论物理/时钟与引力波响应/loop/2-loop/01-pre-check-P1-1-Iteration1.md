# Pre-check — P1-1 JCAP 手征引力波物理深化

## 状态
**PASS**

## 检查项

- **Python 环境**: Python 3.14.4 — 可用
- **依赖库**: numpy 2.4.4, scipy 1.17.1, matplotlib 3.10.9 — 全部可用
- **磁盘空间**: 331 GiB 可用 (63% 使用率) — 充足
- **前置文件完整性**:
  - `raw/JCAP2025_Chiral.pdf` (1.4 MB) — 可用
  - `raw/JCAP2025_Chiral.txt` (60 KB) — 可用
  - `raw/PhysRevD.111.084065(1).pdf` (816 KB) — 可用
  - `raw/PhysRevD.111.084065(1).txt` (72 KB) — 可用
  - `note/P1-1-chiral-physics.md` (10.8 KB) — 可用（主笔记，已完成）
  - `note/P0-1-hu-prd-understanding.md` (32.4 KB) — 可用（Subtask 4 交叉参考）
  - `note/OLC与手征引力波_对比分析报告.md` (13 KB) — 可用
  - `note/手征-GW-ORF-文献调研2026.md` (14 KB) — 可用
  - `scripts/debug_rv_zero.py` (26 KB) — 可用（数值验证参考）
  - `scripts/09-olc-chiral-orf.py` — 可用
  - `scripts/11-multi-constellation-chiral-orf.py` — 可用
  - `loop/1-loop/02-目标澄清-手征物理-Iteration1.md` — 可用
  - `loop/1-loop/03-任务分解-P1-1-Iteration1.md` — 可用
  - `loop/1-loop/04-信息搜集-P1-1-Iteration1.md` — 可用
  - `loop/1-loop/05-完备核验-P1-1-Iteration1.md` — 可用
  - `loop/1-loop/06-决策-P1-1-Iteration1.md` — 可用（决策: enter_2loop, 置信度 0.85）
- **阶段允许执行**: `ralph-loop.local.md` 中 `loop_phase = idle` — 允许进入 2-loop
- **修改位置**: 产出写入 `note/P1-1-appendix-normalization.md`（追加模式），符合项目规范
- **可回滚性**: 所有子任务产出追加到单一附录文件，可完全删除

## 子任务就绪度评估

| 子任务 | 输入文件 | 工具可用性 | 评估 |
|--------|----------|-----------|------|
| Subtask 1 (归一化验证) | JCAP eq. 2.3-2.4, 笔记 §1.2 | Python 代数验证 | 就绪，纯数学验证 |
| Subtask 2 (Gamma^V 张量推导) | JCAP eq. 2.10, Appendix B.2, 笔记 §5.3, 记忆 16, `debug_rv_zero.py` | Python 数值验证 | 就绪，无外部依赖 |
| Subtask 3 (chi(f) 频谱) | JCAP §3.3, 引用列表 | arXiv 获取（备选降级） | 降级后可执行，无阻塞 |
| Subtask 4 (Hu vs JCAP 对照) | Hu PRD PDF+txt, JCAP txt, 笔记 §7, P0-1 笔记 | 双文献对比 | 就绪，预判结论已明朗 |
| Subtask 5 (整合评审) | Subtask 1-4 输出 | 评审性质 | 依赖明确，无阻塞 |

## 风险警告

1. **Subtask 3 — 外部文献降级策略**：Seto 2006 (PRL)、Alexander 2006、Satoh 2008 等 5+ 篇关键引用未本地存档。如 arXiv 获取失败，降级为基于 JCAP 引用摘要的有限分析。新�性从 N2 降级为 N1。不影响 AC 判定，但影响"手征光谱学"框架的完整度。

2. **Subtask 2 与 Subtask 1 互为校验**：归一化验证的正确性是张量推导正确性的前提。建议 Subtask 1 先完成或至少部分完成后再启动 Subtask 2 的严格推导，以确保中间结果的一致性。

3. **Subtask 4 预判风险**：预判"Hu 框架不包含手征"可能出错。2-loop 中必须严格阅读 Hu PRD 的 ORF 定义章节而非仅依赖关键词搜索（chiral/parity/helicity 计数为 0 是必要但不充分的证据）。

4. **Git 状态**：仓库存在未跟踪文件（`?` 标记），P0-1 已完成 git commit f456cd8。P1-1 产出追加到笔记文件，不涉及 git tracking 更新，回滚只需删除附录文件。

## 结论
**预检查通过。P1-1 可立即进入 2-loop 执行，Subtask 1 + Subtask 2 可并行启动。**
