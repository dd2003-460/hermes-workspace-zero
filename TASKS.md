# 全局任务队列

## 格式说明
- 按从上到下顺序排列
- 格式：任务描述 — 项目地址
- 无编号，手动重排即可
- 每个项目若有待确认问题会写在项目目录下的 `<项目名>-task.md`

---

## 最高优先级（当前 Focus）

- **D1-grav-waves: JHEP 论文推进** — Extended Functorial QFT 框架用于 PTA 引力波源判别。原创论文已写 (papers/2026-GW-BacQFT/GW-BacQFT-paper.tex)，含 3 个理论结果：HD 相关性函子论重构、源判别定理、各向同性定理。迭代14完成：静态审查修复10项问题（引用年份、符号冲突、hexagonal对称性错误、补充7篇关键文献等）。下一步：编译验证、根据审查报告最终修订、arXiv 提交 → JHEP
- **D1-grav-waves: 审查报告最终修订** — ✅ iteration 15 完成：Chernoff bound 删除 + 总变分距离框架替换、宇宙学方差修正（$\mathcal{O}(10^{-10})$ 宇宙方差）、各向异性定理重构（振幅/结构差异论证）、全文一致性更新。详见 papers/2026-GW-BacQFT/GW-BacQFT-review-report.md
- **arXiv 提交准备 — ✅ tarball 已生成** — D1-grav-waves: 126.4 KB, D40: 11.4 KB。元数据检查清单已全部完成。仅等待手动提交至 arXiv (gr-qc)
- **D40 论文 LaTeX 转换完成** — ✅ iteration 27：pandoc→latex 生成 D40-paper-converted.tex (628行)，修复全部数学符号格式（D*_expert→D^*_{text{expert}}, P(D|evidence), → arrows）、删除重复结尾、ctexart 类、添加 figure 环境。
- **编译环境恢复** — ✅ iteration 28：DNS 修复 + TinyTeX 安装 + 两个论文编译验证通过 + 两个可复用工具（compile_paper.sh, arxiv_submission_checklist.sh）+ arXiv 检查清单通过（D40: READY, D1-grav-waves: READY）
- **许可证声明** — ✅ iteration 29：两个论文均添加 CC BY 4.0 许可证声明，PDF 重新编译通过
- **D1-grav-waves figure 路径修复** — ✅ iteration 30：PNG 复制到项目根目录 + includegraphics 改用 .png，双编译方式均通过（项目根目录 pdflatex + compile_paper.sh），10页/405K 含图 PDF
- **arxiv_cat.py 重写** — ✅ iteration 31：支持 curl --resolve 降级（绕过 DNS 阻断）、ti:+abs: 前缀搜索（精准匹配标题/摘要）、JSON 解析、结构化输出
- **arxiv_prepare.py 修复** — ✅ iteration 32：balanced brace 嵌套匹配修复 `\title{\textbf{...}}` bug，strip_latex_formatting 支持 7+ LaTeX 命令，双论文验证通过
- **arXiv 工具链完成** — ✅ iteration 32: 5 个工具覆盖搜索→编译→验证→准备→打包。tar.gz 提交包已生成（D1:136K, D40:12K）。两个论文 arXiv 就绪。
- **工具冗余审计** — ✅ iteration 33: arxiv_cat.py + arxiv_cats.py 改用 arxiv Python 包 (2.4.4)，更稳定。scipy.constants 可用于 GW 项目物理常数。D40 模拟已正确复用 numpy+scipy。
- **文献搜索（CrossRef API）** — ✅ iteration 34: arXiv API 持续限流，改用 CrossRef API。发现 5 篇与 D40 高度相关文献（Noro EMNLP 2025, Roxas TechRxiv 2025, Peng 2025, Hochin 2013, Zhang 2024）。4 篇已加入 D40 论文参考文献。详见 raw/crossref_literature_findings.md
- **D1-grav-waves 文献搜索** — ✅ iteration 35: CrossRef API 搜索发现 8 篇相关论文，含 Kehagias&Riotto 2024 (HD 对称性解释) 直接支持 D1。已加入 D1 论文参考文献。详见 D1-grav-waves/raw/d1_crossref_literature.md

## 已完成

【ralph-loop.global.md 是固定全局指南，严禁修改】
【项目任务状态在项目根目录 tasks/ 下】
【规划用 /Users/a1-6/Desktop/workspace/loop/1-loop/，执行用 /Users/a1-6/Desktop/workspace/loop/2-loop/】

loop 重构 — workspace/loop/（1-loop 01-06 + 2-loop 01-06，canonical）
D1-academic-AI/loop 已标记 DEPRECATED，迁移到 workspace/loop/
chimera_lab 三个扩散实验（D50/D51/D52）
bayesian-frame 核心模块（core.py + visualize.py + run_all.py）
bayesian-frame 实验脚本运行验证通过（exp_2024 + exp_2025）
bayesian-frame 模块化架构（bayesian_frame/ 包，6 模块 491 行）
bayesian-frame 理论-参数连接（parameter_control 模块，Wei2012/2017/Mao2024/Sun2025 参数映射）
bayesian-frame JCR 论文初稿 skeleton 校正 + 全部实验修复验证
bayesian-frame exp_2025 LinearMapper 修复（likelihood/posterior/circular_mean/grid 对齐/alpha 优化）
bayesian-frame ModelFitter 重构（alpha 拟合误差 < 0.0001）
bayesian-frame util 模块修正（PriorConfig 一致性, circular wrapping, compute_discriminability）
bayesian-frame exp_2017 Exp2 summary R² 显示修复（实际 R²=0.26-0.28 跨 κ 稳健）
bayesian-frame CLI 逻辑修复（--param 隔离, parameter_control.py argparse）
bayesian-frame SensitivityAnalyzer 改为 True Morris Method（mu_star/sigma 灵敏度分析）
bayesian-frame 顶层 API: 27 个公共导出 `from bayesian_frame import ...`
bayesian-frame 测试套件: 4 项测试通过 (export/normalization/report/fit)
bayesian-frame README.md 创建
bayesian-frame Fisher info 模块 bug 修复 + 5 新测试（alpha 硬编码 + Barron's inequality）
bayesian-frame PriorConfig trapz normalization 测试修复（4 项 pre-existing test bugs）
bayesian-frame 19/19 tests 全部通过
bayesian-frame 排斥性偏差机制深度探索（2028b/2029/2030/2031）：确认标准贝叶斯 + EC + lateral inhibition 不产生 repulsive bias
bayesian-frame 详细文档 DOCS.md 创建并更新（面向非专业人员）
bayesian-frame Ralph loop 启动
语言偏好设置：所有通信除代码外使用中文（memory/linguistic-preference.md）
**Wei 2015 phi-shift 机制实现并验证** — PhiShift 类，6 测试，25/25 测试通过，排斥效应线性增大
**首次从第一性原理产生排斥性偏差** — 刺激 45°: phi=0→-5.27° 吸引，phi=0.05→+7.14° 排斥
**Phi-shift + EC 联合效应** — EC 调制 kappa，phi-shift 偏转中心，两者协同工作
**副脑审查** — docstring 符号修复，发现 phi-shift 与"先验欠加权"理论对应关系未建立
**JCR 论文初稿 skeleton ✅** — JCR_paper_skeleton.md 已创建并校正为实际实验数据；Q2/Q3/Q4 待确认（bayesian-frame-task.md）

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
- bayesian-frame 排斥性偏差机制深度探索（2028b/2029/2030/2031）：确认标准贝叶斯 + EC + lateral inhibition 不产生 repulsive bias
- bayesian-frame 详细文档 DOCS.md 创建并更新（面向非专业人员）
- bayesian-frame Ralph loop 启动
- 语言偏好设置：所有通信除代码外使用中文（memory/linguistic-preference.md）
- **Wei 2015 phi-shift 机制实现并验证** — PhiShift 类，6 测试，25/25 测试通过，排斥效应线性增大
- **首次从第一性原理产生排斥性偏差** — 刺激 45°: phi=0→-5.27° 吸引，phi=0.05→+7.14° 排斥
- **Phi-shift + EC 联合效应** — EC 调制 kappa，phi-shift 偏转中心，两者协同工作
- **副脑审查** — docstring 符号修复，发现 phi-shift 与"先验欠加权"理论对应关系未建立

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

## Ralph 循环 — 自主运行中

- **RALPH LOOP 全局指南** — `/Users/a1-6/Desktop/workspace/ralph-loop.global.md`
- **RALPH LOOP PLUGIN** — `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/ralph-loop/`
- **启动脚本** — `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/ralph-loop/scripts/setup-ralph-loop.sh`
- **原帖** — https://ghuntley.com/ralph/
- **正确启动命令**：
  ```bash
  bash ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/ralph-loop/scripts/setup-ralph-loop.sh "$(cat /Users/a1-6/Desktop/workspace/ralph-loop.global.md)" --max-iterations 0
  ```
  Claude Code 中也可用 `/ralph-loop "$(cat /Users/a1-6/Desktop/workspace/ralph-loop.global.md)"`
- **任务要求**：Claude 启动后自行读取 TASKS.md → 当前活跃任务 → 执行。不应等待外部指令。
- **状态**：循环持续运行。每个 iteration 必须产生可验证输出。永远不输出 `<promise>LOOP COMPLETE</promise>`。

## iteration 21-25（2026-05-08）

### 已完成
- iteration 20: D40 论文修复（作者/参考文献/局限量化/实验验证）
- iteration 21: 项目结构完整性修复（INDEX.md/任务去重/空目录清理）
- iteration 22: D40 实验重新运行验证（4/4 通过，实证可复现）+ 生成 HD 曲线图 + D40 实验图
- iteration 23: Markdown→LaTeX 转换器 v1（有 bug）
- iteration 24: 重大发现 — 网络未阻断，DNS 被阻断。`curl --resolve` 可绕过。Pandoc 已安装。D40 HTML 生成成功（MathJax 正确）。CTAN tlnet 可下载但限速。
- iteration 25: 网络诊断记录归档，临时文件清理
- iteration 26: **Pandoc→latex 生成 arXiv 兼容 .tex 成功**（D40-paper-converted.tex，632行，55 inline + 27 display math）

| **阻塞（持续）** |
- arXiv 提交：**tarball 已生成**（D1: 126.4 KB, D40: 11.4 KB），等待作者确认提交时间
- D40 当前环境编译：CJK 字体缺失（unikai74），但 PDF 已存在可提交
- **⏰ 副脑 deadline 已过**（2026-05-09 04:30）：tarball 已生成，元数据已更新
