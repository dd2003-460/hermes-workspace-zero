# Iteration 273: integrate_persona.py 改进 + Team shutdown 文档

## 执行

1. 扫描所有项目 idea 文件 — 确认 104 个都在 D1-persona-align/memory/ 下
2. 更新 integrate_persona.py：区分 can_use_alignment 和 can_use_hermes_sync
3. 修复 D1-academic-AI/integrate_persona.py — 更新后正确显示 ⚠️ 无 idea 文件
4. 创建 team-shutdown-workaround.md — 文档化 Team 功能 shutdown bug

## 结果
- integrate_persona.py 现在对无 idea 文件的项目给出明确指引
- Team shutdown 问题已记录，绕过方法：不要 TeamDelete，手动清理目录

## 产出
- scripts/integrate_persona.py (更新)
- memory/team-shutdown-workaround.md
