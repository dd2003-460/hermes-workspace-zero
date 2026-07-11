# 02-backup（备份）

**输入**：`pre-check-result.md`（来自阶段 1）
**输出**：git commit 记录

---

## Agent 使用规范

备份阶段**必须通过 Agent 执行**。Commander 不亲自操作 git：

| 场景 | 使用 Agent | 原因 |
|------|-----------|------|
| git 仓库检查和备份 | `Explore` Agent | Agent 执行 git 操作并返回 commit hash |
| backup-log.md 写入 | `Explore` Agent | Agent 记录备份信息 |

**强制要求**：
- git 操作（init/add/commit/verify）必须通过 Agent 执行
- commit hash 必须由 Agent 确认并记录

---

## 操作步骤

### Step 1：检查 git 仓库（Agent 执行）
**通过 Agent 执行**：`Explore` Agent 确认项目根目录已有 git 仓库。如未初始化，Agent 执行：
```bash
cd /path/to/project
git init
git add -A
git commit -m "initial backup before 2-loop"
```

### Step 2：执行备份（Agent 执行）
**通过 Agent 执行**：在修改任何文件前，Agent 用 git 创建带时间戳的 commit：
```bash
cd /path/to/project
git add -A
git commit -m "backup before 2-loop 03-execute: $ISSUE_NAME"
```

### Step 3：记录 commit hash（Agent 执行）
**通过 Agent 执行**：记录备份的 git commit hash，写入 backup-log.md。

### Step 4：写入 backup-log.md（Agent 执行）
**通过 Agent 执行**，Agent 写入：
```markdown
# Backup Log
## git commit
- hash: <SHA1>
- message: backup before 2-loop 03-execute
- date: <timestamp>

## 回滚命令
git checkout <hash>

## 验证
- [x] git add -A 通过
- [x] commit 创建成功
```

---

## 约束

- **必须用 git 备份**，禁止使用文件复制方式
- 备份 commit message 必须包含时间戳和任务名
- 记录 commit hash 用于回滚
- 不可跳过备份步骤
