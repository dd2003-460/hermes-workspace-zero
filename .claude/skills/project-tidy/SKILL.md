---
name: project-tidy
description: 项目结构整理 SOP（2026-10-21 批准）。触发：用户说"整理项目/结构"、定时巡检、或某项目产出变乱时。原则：只理结构不删探索过程（AGENTS.md 红线0）。
---

# 项目整理 SOP（project-tidy）

红线：**不删除任何探索过程，只整理结构**。删除仅适用于：空目录、node_modules/缓存、已作废实验（移 archive/ 不 rm）。

## 流程（每项目 5 查）

1. **标准结构查**：`INDEX.md` + `memory/`（完整探索记录，不可删）+ `tasks/`（当前临时状态）。缺则补（空目录加占位说明）。
2. **层级数查**：每层 INDEX 的次级子模块 3–7 个为宜（迭代编号方案 D*/d* 豁免）。>7 → 归类合并或下沉新子层；<3 且非叶 → 检查是否该与兄弟合并。
3. **顶层杂物查**：项目顶层只允许标准结构 + 项目级文档（README/loop-state.json）。散落的输出/脚本/截图 → `outputs/`（工程产出）或 `archive/`（作废/过期）。
4. **临时物查**：node_modules、.npmcache、__pycache__、.DS_Store、空目录 → 删（先确认 .gitignore 覆盖）。**git add -A 前必须 `git status` 扫一遍**（2026-10-21 教训：tmp 目录 npm 缓存被误提交）。
5. **索引查**：新/移文件是否更新了本层 INDEX.md + 上级 projects/INDEX.md 的行（状态列：进行中/交付/归档）。

## 收尾（git 纪律）

1. 每个嵌套独立仓（如 projects/decomp）单独 commit+push。
2. 根仓：整理前留备份 commit → 改动 → `git status` 全量核对 → commit（message 注明"整理：动了什么"）→ push。
3. 归档操作记入项目 `loop-state.json` 的 last_action（日期+原因+去向）。

## 审计脚本

```bash
python3 scripts/tidy_audit.py            # 全 projects/ 审计，输出超 3-7 层 + 缺标准结构清单
python3 scripts/tidy_audit.py projects/decomp   # 单项目
```

报告落 `loop-artifacts/tidy/<YYYYMMDD>/audit.md`。审计只读，不改文件。

## 定时巡检（可选，需成璐批准后建 schedule）

频率建议：每周一次；流程 = 跑 tidy_audit → 只对"新增超界/缺结构"项目执行本 SOP → commit+push → 在对应项目 loop-state.json 记一行。
