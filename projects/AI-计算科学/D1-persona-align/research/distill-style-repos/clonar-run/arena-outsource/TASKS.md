# arena 外包任务卡 — clonar 风格蒸馏（MAP×4 + REDUCE×3）

## 任务 T1（核心，先做）：MAP × 4
对 `chunk_000-map-task.md` ~ `chunk_003-map-task.md` 各做一遍 MAP 分析。
每个文件自带完整方法（clonar-escrita 的 map_analysis 方法）+ 80 条真实消息。
**照方法里的 5 条规则做**：每条观察必须有字面证据（原文引用）/ 只看形式不看内容 / 尽量量化 / 出现 1 次的标 [fraco] / 不跨 chunk 泛化。
**输出要求**：中文，markdown，按方法里的 6 节结构（词汇/话语标记/句法/正字法约定/语域切换/总结）。
每个 chunk 的完整分析贴回（不截断）。

## 任务 T2（等 T1 完成后）：REDUCE × 3
拿到 4 个 MAP 结果后，用 reduce_synthesis 方法做 3 遍综合（每遍打乱 chunk 顺序）。
**关键规则**：3 遍都出现的特征=真特征；只出现 1 遍的=噪音，丢弃。
输出：final_synthesis.md（每特征带：出现遍数/证据样例/置信度）。
