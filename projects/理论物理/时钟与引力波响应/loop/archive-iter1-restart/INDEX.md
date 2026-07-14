# Archive: iter1-restart (2026-07-12 ~ 2026-07-13)

此归档包含 RALPH Loop 重启后的全部产出，在清理和重新规划前保存。

## 目录结构

```
archive-iter1-restart/
├── 1-loop/              — 78 文件: 全部 1-loop 阶段产出 (01~06)
├── 2-loop/              — 77 文件: 全部 2-loop 阶段产出 + P2-3 结果
├── memory/              — 22 文件: memory/ 下所有探索记录
├── note/                — 25 文件: note/ 下所有分析笔记
├── tasks/               — 9 文件: 任务分解和规格文件
├── paper/               — 38 文件: paper/ 下所有论文中间文件
├── root-temp/           — 根目录临时文件 (backup-log, backups/)
├── ralph-loop.local-state.md — 归档前的 RALPH 状态文件
└── INDEX.md             — 本文件
```

## 关键发现（来自此轮）

- v17 之谜已破解: -7.75e-3 是单天区方向值 (θ≈36.51°, φ≈82.58°)
- Script 11 使用 Michelson TF 代替 OLC TF 导致 577x 差异
- P2-3 精确匹配完成: 相对误差 0.02%

## 归档后处理

- 当前 loop/1-loop/ 和 loop/2-loop/ 已清空，等待重新运行
- ralph-loop.local.md 已重置为 idle
- 论文最终版本: paper-archive/main-paper-v17.tex
