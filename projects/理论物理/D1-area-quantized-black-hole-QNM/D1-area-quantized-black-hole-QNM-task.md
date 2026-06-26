{
  "requirement": "确定 RW+旋转修正框架失效后的技术路线 — 决策已完成",
  "background": "P0+P1-v2+P1-v3 扫描完成。E_lm 高阶修正分析 (iter 4) 确认：(aω)^6+ 贡献 < 0.001，且 m=0 模式（E_lm 精确）同样在 a=0.95 失败。框架失效是结构性问题（RW 方程源自 Schwarzschild 度规，无法捕捉 frame-dragging 对径向方程的影响）。",
  "decision": {
    "route": "Teukolsky + AIM 为唯一可行路径",
    "confidence": "high",
    "rationale": "m=0 模式分析排除 E_lm 高阶修正路线；RW+旋转修正框架有效上限 a≈0.92 (l=2,m=2) / a≈0.90 (l=3,m=3)",
    "valid_range_RW": "a <= 0.90 (保守估计，覆盖所有 l,m)",
    "valid_range_teukolsky": "a > 0.90 (统一覆盖)",
    "date": "2026-06-16"
  },
  "next_steps": [
    "Teukolsky + AIM 文献综述与实现方案",
    "a∈[0, 0.9] 综合扫描报告 (合并 P0+P1-v2+P1-v3)",
    "验证已有 FDTD 求解器在 a<=0.9 的可靠性 (92.9% 通过)"
  ],
  "constraints": [
    "时间: RALPH LOOP 100000 轮次内完成",
    "工具: Python/NumPy/SciPy",
    "无外部 API 依赖",
    "Teukolsky 实现：ODE 求解器 + AIM 迭代"
  ],
  "priority": "immediate"
}
