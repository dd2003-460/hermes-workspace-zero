{
  "requirement": "persona-v3 系统持续改进：修复自适应感知维度全量增强（当前平均分 40.4，最低维度 0.22），将整体对齐度提升至 50+",
  "background": "persona-v3 已建成 8 原则 + 6 维度 + 3 行为约束，gap_filler auto-cite 闭环完成，15 篇研究 review。但 dashboard 扫描 53 文件平均仅 40.4 分，自适应感知维度 avg=0.22 为最弱维度。",
  "existing_info": ["/Users/a1-6/Desktop/workspace/projects/D1-persona-align/scripts/persona_v3_gap_filler.py", "/Users/a1-6/Desktop/workspace/projects/D1-persona-align/scripts/persona_v3_alignment_checker.py", "/Users/a1-6/Desktop/workspace/projects/D1-persona-align/scripts/persona_v3_dashboard.py", "/Users/a1-6/Desktop/workspace/projects/D1-persona-align/memory/idea-*.md (52 files)", "/Users/a1-6/Desktop/workspace/projects/D1-persona-align/memory/review-*.md (14 files)", "/Users/a1-6/Desktop/workspace/loop/ 1-loop 和 2-loop 流程文件"],
  "constraints": ["MBST 限制，不能修改 ralph-global.md 的非临时状态内容", "必须按 1-loop/2-loop 流程执行", "跳过用户阻塞，每轮必须产出", "工具优先：复用 gap_filler、alignment_checker、dashboard"],
  "priority": "planning"
}
