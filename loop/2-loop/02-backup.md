# 02-backup（备份）

**输入**：`pre-check-result.md`（来自阶段 1）
**输出**：git commit 记录

---

## 操作步骤

### Step 1：检查 git 仓库
确认项目根目录已有 git 仓库。如未初始化，执行：
```bash
cd /path/to/project
git init
git add -A
git commit -m "initial backup before 2-loop"
```

### Step 2：执行备份
在修改任何文件前，用 git 创建带时间戳的 commit：
```bash
cd /path/to/project
git add -A
git commit -m "backup before 2-loop 03-execute: $ISSUE_NAME"
```

### Step 3：记录 commit hash
记录备份的 git commit hash，写入 backup-log.md

### Step 4：写入 backup-log.md
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
