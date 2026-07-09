{
  "requirement": "整合手征引力波计算解析 ORF — 从 Hu PRD 通用框架出发，推导适用于 OLC 网络的手征交叉相关 ORF (Gamma^I + i Gamma^V)",
  "background": "项目已运行 31 轮 RALPH Loop。所有已知 bug (6个) 已被 P4-1 独立审计确认修复。P0-1/P1-1/P2-1/P3 已完成理解材料。核心物理发现：(1) 单三角 Michelson-like 变量 Gamma^V = 0；(2) Gamma^V 非零需要非共面网络；(3) JCAP 框架提供完整手征 ORF 数学工具。但还没有实际的 chiral ORF 解析公式产出。",
  "existing_info": [
    "note/P0-1-hu-prd-understanding.md — Hu PRD 通用 ORF 框架 (QC PASS, conf 0.97)",
    "note/P1-1-chiral-physics.md — 手征物理推导 (QC PASS, conf 0.87)",
    "note/P2-1-olc-principles.md — OLC 原理 (QC PASS, conf 0.90)",
    "note/P3-phase3-cross-comparison.md — 三文献交叉对比 (QC FAIL, 缺少 unified formulas)",
    "scripts/11-multi-constellation-chiral-orf.py — 已有 chiral ORF 代码 (含 bug，结果被标记废弃)",
    "memory/13 — Iteration 6 chiral ORF 调查报告 (JCAP 辅助张量/几何因子/SNR 公式)",
    "memory/14 — Iteration 7 多星座 chiral ORF (已标记废弃)"
  ],
  "constraints": [
    "RALPH Loop 规则：必须经 1-loop(6阶段) → 2-loop(6阶段)",
    "规则7铁律：Commander 不亲自执行底层计算，通过 Agent 分发",
    "副脑永续：每轮结束必须派发质疑 agent",
    "任务粒度：Agent 单次调用不超过上下文长度"
  ],
  "priority": "immediate"
}
