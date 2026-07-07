# Task Specification — Iteration 6: 三角形 3 卫星 OLC 手征 ORF 计算

## requirement
计算三角形 3 卫星光晶格原子钟（OLC）星座对圆极化随机引力波背景（SGWB）的手征重叠约化函数（chiral ORF, Gamma^V），验证其灵敏度是否达到 Kato & Soda 2016 和 Orlando et al. 2021 中 LISA 三角构型的量级（|Gamma^V| ~ 0.3）。

## background
Iteration 5 已证明：单臂 OLC 探测器对所有几何构型的手征 ORF 均为零（~1e-18，机器精度级别）。这是基本物理限制——单臂 OLC 是标量观测量（频率偏移），本质上缺乏区分圆极化（手征性）的张量结构。

Kato & Soda (2016, JCAP) 从理论上证明：手征 GW 检测需要非镜像对称探测器。LISA 的三角形（3 卫星、6 单向链路）构型实现了 |Gamma^V| ~ 0.3 的手征灵敏度。

当前论文草稿声称"三角形 3 卫星 OLC 可以达到与 LISA-Taiji 相当的手征灵敏度（|Gamma^V| ~ 0.3）"，但没有任何数值计算支持这一声明。

## existing_info
- `scripts/09-olc-chiral-orf.py` — 已有的手征 ORF 计算代码（单臂构型），可作为基础 fork
- `memory/01-olc-orf-formulas.md` — OLC ORF 公式推导
- `memory/02-lou-olc-transfer-function.md` — OLC 传递函数（Lou 硕士论文）
- `memory/03-olc-orf-results-summary.md` — ORF 计算结果汇总
- `chiral-olc-paper-draft.md` — 当前论文草稿（包含三角形 OLC 声明）
- `raw/JCAP2025_Chiral.pdf` — Kato & Soda 2016 原文（JCAP）
- `raw/PhysRevD.111.084065(1).pdf` — Hu et al. PRD 2025（ORF 通用框架）
- 已有天线方向图函数 `F_plus` 和 `F_cross` 的实现
- 已有球面天空积分引擎（ntheta/nphi 离散积分）

## constraints
- **硬约束 1**: 传递函数必须使用 OLC 特定形式（参考 Lou 硕士论文），不可直接使用 PTA/LISA 的传递函数
- **硬约束 2**: 天线方向图函数 `F_plus = |th·u|² - |ph·u|²` 和 `F_cross = 2 th·u ph·u` 必须保持与 Iteration 5 一致的实现
- **硬约束 3**: 手征 ORF 公式 `Gamma^V = int (F_+1*F_x2 - F_x1*F_+2) * T1 * conj(T2) * dΩ` 必须保持
- **硬约束 4**: 天空积分精度必须达到 <1%（标准 ORF），手征 ORF 收敛性必须验证
- **时间约束**: 单轮扫描不应超过 5 分钟

## priority
planning
