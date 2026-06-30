{
  "requirement": "分析 OLC 探测器的 ORF 频率依赖关系，生成 f-L 二维灵敏度响应图",
  "background": "OLC（光晶格原子钟）是一种新兴的引力波探测器。Hu et al. PRD 111, 084065 (2025) 提供了通用 ORF 计算公式，楼明智论文 (2026) 完成了特定构型的数值计算。但尚未有工作系统性分析 ORF 对臂长 L 和频率 f 的依赖关系。",
  "existing_info": [
    "调研报告.md — 包含 ORF 核心公式、理论框架、8 个研究空白",
    "Hu PRD 提取文本 — 通用 ORF 计算公式（留数定理方法）",
    "楼论文提取文本 — OLC 构型 ORF 数值计算",
    "调研空白 A 定位: OLC 臂长 1-10m，光钟采样率极高，fL/c 覆盖 10^-15 到 10^3 范围",
    "OLC 的 arm response 与 PTA 和 LISA 完全不同（频段跨度 3 个量级以上）"
  ],
  "constraints": [
    "时间: 预计 2-3 天（纯计算，无需新实验）",
    "工具: Python + scipy/numpy + matplotlib",
    "已有 Hu PRD 的通用公式作为理论基础",
    "不需要新文献调研（调研空白已有充分理论铺垫）"
  ],
  "priority": "planning",
  "phase": "1-loop stage 1",
  "date": "2026-06-28"
}
