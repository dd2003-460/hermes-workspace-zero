# 2-loop · 04-项目分类与索引原则（递归编号体系）

> **用途：** D1-* 项目的创建、迁移、整理时必须遵守的分类规范。
> **验收标准：** 任何一个 D1-* 目录下不允许出现没有 INDEX.md（如果有子目录）的结构。每一层的 INDEX.md 只描述下一层有哪些项目，不存储实际内容。

---

## 1. 编号原则：论文式递归定位

所有工作产出（脚本、记忆、任务状态）必须按**精确编号体系**分类存放，定位到最小粒度：

```
projects/D1-<项目名称>/                          # 第 N 块（一级项目）
├── INDEX.md                                     # [N]项目的概述、目标、子目录索引
├── scripts/                                    # 第 N.1 块（脚本）
│   ├── INDEX.md                                # [N] → scripts/ 有哪些文件，无实际内容
│   └── <script-name>.py                        # [N.1.<随机>] 实际脚本文件
├── memory/                                     # 第 N.2 块（记忆）
│   ├── INDEX.md                                # [N] → memory/ 的条目索引，无实际内容
│   └── entries.json                            # [N.2.<随机>] 实际记忆条目
├── tasks/                                      # 第 N.3 块（任务）
│   ├── INDEX.md                                # [N] → tasks/ 的任务索引，无实际内容
│   └── <task-name>.json                        # [N.3.<随机>] 实际任务文件
```

### 编号规范（与论文 1.2.3.4 对应）
- **N** = D1-*项目名（如 `workspace-org` → 第3块）
- **N.1** = scripts（第一大类：脚本工具链）
- **N.2** = memory（第二大类：记忆和知识资产）  
- **N.3** = tasks（第三大类：任务状态和工作项）
- 每个具体的文件通过 `memory/entries.json`、`tasks/task-name.json`等精确路径定位

### 编号示例
```
projects/D1-workspace-org/scripts/automation/cron-jobs/index.md       # [3.1] 脚本自动化 - cron任务
projects/D1-workspace-org/memory/entries.json                         # [3.2] 实际记忆条目
projects/D1-workspace-org/tasks/state.json                            # [3.3] 任务状态文件
```

---

## 2. INDEX.md 政策：纯索引，零内容冗余

**核心规则：** 每个目录下（包含子目录的）**只保留一个 INDEX.md，不存储实际内容**。

| 位置 | 文件 | 作用 |
|------|-----|------|
| `projects/D1-X/` | `INDEX.md` | 描述 D1-X 的用途、目标；列出 scripts/ memory/ tasks/ 目录索引 |
| `projects/D1-X/scripts/` | `INDEX.md` | "以下脚本由本目录管理"；列出实际文件名（如 `[3.1] auto_backup.sh`），**不存储脚本内容本身** |
| `projects/D1-X/memory/` | `INDEX.md` | "本目录索引已归档的条目"；列出 entries.json 的版本/日期，**不存储记忆内容本身** |
| `projects/D1-X/tasks/` | `INDEX.md` | "本目录存储 D1-* 的任务"；列出 task-id.json，**不重复全局 single_loop_state.json** |

### INDEX.md 模板（所有 D1-* 项目通用）
```markdown
# [N].<name> — <title>

## 项目描述
（一句话说明这个 D1-* 做什么）

## index.md policy
- scripts/ → [N.1.*] — （脚本目录索引描述）
  - <file_name>.<ext> [N.1.<random>] — （文件说明）
- memory/ → [N.2.*] — （记忆目录索引描述）  
  - entries.json — （条目列表/日期版本引用，不存实际内容）
- tasks/ → [N.3.*] — （任务目录描述，仅引用单热全局状态）
  - state.json

## 关联项目
（如需要与其他 D1-* cross-reference）
```

---

## 3. memory/raw/ 的归档规则（迁移协议）

`memory/raw/`是临时池。整理时：
1. 读取每个文件的标题+前5行内容（只读，不搬移）
2. 根据文件**第一句话/标题+前5行内容**判断领域归属：
   - workspace 整理 → `projects/D1-workspace-org/memory/entries.json`  
   - AI/GPU研究想法 → `projects/D1-ai-gpu-research/memory/entries.json`（或创建新项目）
   - 通用笔记 → `projects/D1-general-memory/memory/entries.json`  
3. **不要删除源文件**（参考用户纠正："只移动" → 这里指从 raw/移动到 D1-X/memory，但保留原始副本在raw/dumps中作为备份）
4. 在每个 D1-X 的 INDEX.md memory/section 引用该条目

---

## 4. task state 按项目分类规则
- **全局热状态：** `tasks/single_loop_state.json` — 唯一活链路，所有跨项目协调任务的状态
- **每个 D1-*有自己的 tasks/目录：** 仅存储该项目**冷待办池**。任何任务必须先在本地 `projects/D1-X/tasks/` 记录，只有进入热链路后才导入全局状态。
- **索引隔离：** `tasks/single_loop_state.json` 引用时只使用 `[D1-X]: <task-id>` 格式，不存储完整任务内容。

---

## 5. D1-*项目创建流程（执行标准）
当需要新建一个领域项目时：

| 步骤 | 动作文件/目录状态 |
|------|-------------------|
| CREATE | `projects/D1-<name>/` + INDEX.md + scripts/memory/tasks 目录（仅目录，无文件） |
| WRITE-INDEX | 在 D1-X/ INDEX.md中列出 scripts/memory/tasks 的索引描述 |
| FILL-SCRIPTS | `D1-X/scripts/`下的脚本文件存入实际代码，INDEX.md更新引用 |
| FILL-MEMORY | `D1-X/memory/entries.json` 存入实际记忆，INDEX.md更新引用列表但不存内容 |
| FILL-TASKS  | `D1-X/tasks/*.json`（冷待办），然后导入全局单热状态 |
| VERIFY  | `tree projects/D1-<name>/` — 确认不存在没有 INDEX.md的有子目录，且每层只有一层索引 |
