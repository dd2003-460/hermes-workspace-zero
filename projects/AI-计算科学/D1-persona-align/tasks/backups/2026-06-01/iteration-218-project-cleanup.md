# Iteration 218: 项目清理 + .gitignore

## 目标
清理项目中的临时文件和空目录, 添加 .gitignore 防止将来提交垃圾文件.

## 执行动作

### 清理
1. 删除 `__pycache__/` — 包含 `synthetic_data_generator_v5.cpython-314.pyc`
2. 删除 `iterations/` — 空目录

### 新增 `.gitignore`
```
# Python
__pycache__/
*.py[cod]
*.so
*.egg-info/
dist/
build/

# macOS
.DS_Store

# Eval results (可重新生成)
eval_results/

# Python env
.venv/
venv/
env/

# IDE
.idea/
.vscode/

# Temp files
*.tmp
```

## 影响
- 如果项目被 git 初始化, 不会提交 __pycache__ 和 .DS_Store
- eval_results/ 可以重新生成, 不需要版本控制
- Python venv 不会被提交
