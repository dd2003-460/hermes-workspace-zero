# scripts/project-tidy/ — 项目结构整理 SOP

**origin: ai** · 2026-10-21 · 配套 AGENTS.md 红线 0（项目分类原则）

> 用法：`bash run.sh <project-dir>...` 或 `bash run.sh --all`（扫 projects/ 全部 D1-*）。
> 只报告 + 只自动做安全项（空目录/.DS_Store）；git 操作只 stage 不 commit/push（commit/push 留给 Lead 判断）。

## SOP（6 步，与 check.sh 对应）

1. **INDEX 完整性** — 每层（领域目录、D1-* 项目）必须有 INDEX.md，纯索引（只描述下一层），不写描述性长文。
2. **标准结构** — 项目 = `INDEX.md + memory/（完整探索记录，不可删除）+ tasks/（当前临时状态）+ loop-state.json`；缺一即报 MISSING。
3. **杂物扫描** — .DS_Store、空目录、顶层散文件（项目根 >10 个非标准文件时提示归类建议）。
4. **gitignore 完整性** — 检查 node_modules/、venv（.ttsenv/）、大二进制（>100MB 文件）、渲染中间产物是否在 ignore；未覆盖的报 MISSING-RULE。
5. **git 状态** — 未跟踪大文件（>10MB）、已跟踪但应 ignore 的文件，只报告。
6. **层级扇出** — 每层 INDEX 下项目数 >7 时提示考虑拆子域（目标 3-7；迭代编号方案如 bench/runs/ablation-L1/{V}/ 豁免）。

## 自动执行项（run.sh 默认开启）
- 删 `.DS_Store`（全部层级）
- 删空目录（排除 .git、node_modules、venv 目录）
- 其余只报告，输出 `REPORT.md` 到项目根

## 豁免规则
- 迭代/编号方案（`runs/ablation-L1/C0..C9`、`stages/01..04.5`、`bench/prompts/variants/{V}/`）：数量不受 3-7 限制
- 归档目录（`archive/`）：不再按扇出检查
- 领域级 INDEX（`projects/<域>/INDEX.md`）：只列项目，不要求扇出

## 新增 SOP 规则（2026-10-21 · m00350 批准）
不新建 `projects/SOP/` 目录（避免第二套存放地 + 扇出爆炸）。SOP 只放三个天然家：
- **操作型 SOP** → `.claude/skills/<name>/SKILL.md`
- **流程型 SOP** → `loop/`（prompt-first 或 archived 归档）
- **脚本型 SOP** → `scripts/`
项目/领域 INDEX.md 加一行「SOP 索引」指针（准确 skill 名 + 路径）即可；某领域 SOP 多到 >5 个且需领域级导航时，才在该领域下挂 `sop/` 子目录。
