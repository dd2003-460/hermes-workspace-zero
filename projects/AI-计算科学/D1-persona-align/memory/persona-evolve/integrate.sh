#!/bin/bash
# persona 集成脚本 — 将 persona manifest 集成到任何项目
# 用法: ./integrate.sh <project_path>

PROJECT_PATH="$1"

if [ -z "$PROJECT_PATH" ]; then
    echo "用法: ./integrate.sh <project_path>"
    echo "示例: ./integrate.sh ~/Desktop/workspace/D1-academic"
    exit 1
fi

if [ ! -d "$PROJECT_PATH" ]; then
    echo "错误: 项目目录不存在: $PROJECT_PATH"
    exit 1
fi

echo "=== 集成 persona 到 $PROJECT_PATH ==="

# 1. 创建 persona 符号链接
PERSONA_MANIFEST="$HOME/Desktop/workspace/projects/D1-persona-align/persona-manifest.md"
LINK_PATH="$PROJECT_PATH/persona-manifest.md"

if [ -f "$LINK_PATH" ]; then
    echo "  [SKIP] persona-manifest.md 已存在"
else
    ln -s "$PERSONA_MANIFEST" "$LINK_PATH"
    echo "  [OK] 符号链接创建: $LINK_PATH -> $PERSONA_MANIFEST"
fi

# 2. 更新 INDEX.md（如果存在）
if [ -f "$PROJECT_PATH/INDEX.md" ]; then
    if ! grep -q "persona" "$PROJECT_PATH/INDEX.md"; then
        echo "- [persona](persona-manifest.md) — 成璐思维模式完整对齐" >> "$PROJECT_PATH/INDEX.md"
        echo "  [OK] INDEX.md 更新（添加 persona 链接）"
    else
        echo "  [SKIP] INDEX.md 已包含 persona"
    fi
else
    echo "  [INFO] INDEX.md 不存在，跳过"
fi

# 3. 创建 .persona-env 环境变量文件（供项目脚本使用）
echo "PERSONA_MANIFEST=$PERSONA_MANIFEST" > "$PROJECT_PATH/.persona-env"
echo "  [OK] .persona-env 创建"

echo ""
echo "集成完成。项目现在可以加载 persona manifest 作为系统提示词。"
