# 全局任务队列

## 格式说明
- 按从上到下顺序排列
- 格式：任务描述 — 项目地址
- 无编号，手动重排即可
- 每个项目若有待确认问题会写在项目目录下的 `<项目名>-task.md`

---

## 最高优先级（当前 Focus）

JCR 论文初稿 skeleton ✅ — JCR_paper_skeleton.md 已创建并校正为实际实验数据；Q2/Q3/Q4 待确认（bayesian-frame-task.md）

【ralph-loop.global.md 是固定全局指南，严禁修改】
【项目任务状态在项目根目录 tasks/ 下】
【规划用 /Users/a1-6/Desktop/workspace/loop/1-loop/，执行用 /Users/a1-6/Desktop/workspace/loop/2-loop/】

## 已完成
- loop 重构 — workspace/loop/（1-loop 01-06 + 2-loop 01-06，canonical）
- D1-academic-AI/loop 已标记 DEPRECATED，迁移到 workspace/loop/
- chimera_lab 三个扩散实验（D50/D51/D52）
- bayesian-frame 核心模块（core.py + visualize.py + run_all.py）
- bayesian-frame 实验脚本运行验证通过（exp_2024 + exp_2025）
- bayesian-frame 模块化架构（bayesian_frame/ 包，6 模块 491 行）
- bayesian-frame 理论-参数连接（parameter_control 模块，Wei2012/2017/Mao2024/Sun2025 参数映射）
- bayesian-frame JCR 论文初稿 skeleton 校正 + 全部实验修复验证
- bayesian-frame exp_2025 LinearMapper 修复（likelihood/posterior/circular_mean/grid 对齐/alpha 优化）
- bayesian-frame ModelFitter 重构（alpha 拟合误差 < 0.0001）
- bayesian-frame util 模块修正（PriorConfig 一致性, circular wrapping, compute_discriminability）
- bayesian-frame exp_2017 Exp2 summary R² 显示修复（实际 R²=0.26-0.28 跨 κ 稳健）
- bayesian-frame CLI 逻辑修复（--param 隔离, parameter_control.py argparse）
- bayesian-frame SensitivityAnalyzer 改为 True Morris Method（mu_star/sigma 灵敏度分析）
- bayesian-frame 顶层 API: 27 个公共导出 `from bayesian_frame import ...`
- bayesian-frame 测试套件: 4 项测试通过 (export/normalization/report/fit)
- bayesian-frame README.md 创建
- bayesian-frame Fisher info 模块 bug 修复 + 5 新测试（alpha 硬编码 + Barron's inequality）
- bayesian-frame PriorConfig trapz normalization 测试修复（4 项 pre-existing test bugs）
- bayesian-frame 19/19 tests 全部通过
- bayesian-frame 排斥性偏差机制深度探索（2028b/2029/2030）：确认标准贝叶斯 + EC + lateral inhibition 不产生 repulsive bias

## 高优先级（近期）

- bayesian-frame JCR 论文初稿 ✅ — JCR_paper_skeleton.md 已完成（含全部 4 实验实际数据）
- bayesian-frame Fisher information 模块 ✅ — bayesian_frame/fit/fisher_info.py (7 新导出)
- bayesian-frame tutorial panel 改用真实实验数据 ✅
- bayesian-frame Wei 2015 anti-Bayesian 自主探索 ✅ — 发现 EC 不足以产生排斥偏差

## 阻塞项（需用户输入）
- Q2: 真实数据集来源 — 需要用户确认 Supplement 数据在哪、是否需要导入
- Q3: JCR 报告格式 — 需要用户确认 notebook/LaTeX/混合
- Q4: 框架扩展方向 — Wei 2015 anti-Bayesian ✅ 已探索, Fisher information ✅ 已实现
- **当前迭代 1-loop 副脑质询**: 发现 Fisher info 模块 bug + 数字不一致，已修复
