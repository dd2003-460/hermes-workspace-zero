# 02-backup（备份）

**输入**：`pre-check-result.md`（来自阶段 1）
**输出**：备份文件（`backups/YYYY-MM-DD/<file>.bak`）

---

## 操作步骤

### Step 1：确定需要备份的文件
从 `task-decomposition.md` 中提取所有涉及的文件路径。

### Step 2：创建备份目录
```bash
mkdir -p backups/$(date +%Y-%m-%d)
```

### Step 3：执行备份
**批量修改时每个文件单独备份**：
```bash
cp <file> backups/$(date +%Y-%d)/<file>.bak
```

### Step 4：diff 验证完整性
```bash
diff <file> backups/$(date +%Y-%m-%d)/<file>.bak
```
确认备份与原始文件一致。

### Step 5：写入 backup-log.md
```markdown
# Backup Log
## 备份文件
- <file1>.bak
- <file2>.bak
...

## diff 验证
- [x] 所有文件备份一致
- [ ] [未通过验证的文件]

## 备份时间
$(date)
```

---

## 输出文件

**必须存在**：备份文件（`backups/YYYY-MM-DD/`）+ `backup-log.md`

---

## 前置依赖

阶段 1 输出（`pre-check-result.md`）

---

## 后置依赖

本阶段通过 → 进入执行（阶段 3）

---

## 约束

- **修改前必须备份**，不可跳过
- 批量修改时每个文件单独备份
- `diff` 验证完整性
