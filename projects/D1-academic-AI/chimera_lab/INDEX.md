# chimera_lab 实验索引

## 实验列表

### D27：共发现阈值理论
- `d27-co-discovery-simulation.py` — 共发现首次通过时间模拟（5 命题 D27）
- `d27-results.json` — 5 命题+4 协议结果汇总
- `d27-noise-sensitivity.py` — 噪声敏感性分析（R² > 0.8 仅在噪声 < 0.01）
- `d27-noise-sensitivity.json` — 噪声分析结果

### D31：信息几何语义绕路
- `d31-semantic-distance-geometric-info.py` — 语义绕路的几何路径优化
- `d31-results.json` — 浅类比几何路径最优（91.5%）

### D32：观测保真度理论
- `d32-observation-fidelity-experiment.py` — 预测误差随观测精度单调递增
- `d32-results.json` — 高噪声下容量增益显著更大（0.0046 vs 0.0001）

### D33：行为惯性 — 理性质询阈值
- `d33-behavioral-inertia-experiment.py` — Kramers 逃逸时间 + 大偏差理论
- `d33-results.json` — D33-4 验证 R_change = 19.5x，D33-2 验证 1/x 拟合 R² = 0.995

### D34：自适应信息编码粒度
- `d34-adaptive-encoding-granularity.py` — 自适应编码粒度（4 命题：帕累托前沿、多用户折衷、自适应收敛、加权优化）
- `d34-results.json` — D34-A g*=0.0391, D34-B 排序正确, D34-C 改进 12.1%, D34-D g*加权≠g*平均

### D35：变步长精度 — 信息通信视角
- `d35-variable-step-precision.py` — 变步长精度信息论等价（4 命题：对数律、均匀退化、非均匀优势、RK45 验证）
- `d35-results.json` — D35-A R²=1.0（对数律精确匹配）, D35-B 退化成立, D35-C 优势 91.16%, D35-D RK45 更优

### D35：变步长精度 — 信息通信视角
- `d35-results.json` — 等比特预算下自适应分配降低 43% 总误差

### D36：代际观点收敛动力学
- `d36-viewpoint-convergence-simulation.py` — Lyapunov 吸引子 + 遗传-环境权重转换
- `d36-results.json` — D36-A R²=0.76(α=0.9)，D36-C 灵敏度比=4.48，D36-B 阈值 χ_c 存在

### D37：关系开销均衡动力学
- `d37-relationship-equilibrium-simulation.py` — Nash 均衡 + 反馈控制 + 迟滞效应
- `d37-results.json` — D37-B 非对称鲁棒性测试（4 组参数），D37-D 迟滞面积=0.078

### D38：信号膨胀与衰减动力学
- `d38-signal-burst-simulation.py` — 信号博弈纳什均衡 + 指数衰减 + 遗传异质性 + 最优停止
- `d38-results.json` — D38-A 均衡膨胀100%, D38-B R²=1.0, D38-C corr=-0.986, D38-D T*递减于V_future

### D39：复杂与简单的信息论区分
- `d39-simplicity-experiment.py` — 奥卡姆剃刀信息论证明 + 4 实验协议验证
- `d39-results.json` — D39-A：ΔI_fit=0.035>0 但 ΔI_gen=-0.024<0（伪复杂化记忆噪声不泛化），D39-B：C_crit≈degree 4，D39-C：σ 递增 1.52x，D39-D：高预算收敛比 74:1

### D40：AI市场化精度权衡
- `d40-precision-tradeoff-simulation.py` — 精度-可访问性理论模拟（4 命题验证）
- `d40-results.json` — D40-A：单调递减率 100%，D40-B：D*_general=17.0, D*_expert=31.7（专家需要更高精度），D40-C：log-log r=-0.973（slope ∝ 1/sigma），D40-D：改进 119.9%（p<0.05）

### D41：社会舆论信用系统
- `d41-discourse-credit-simulation.py` — 话语质量的信息论动力学（4 命题验证：Lyapunov 稳定性、信用补偿、相变临界点、实名制效应）
- `d41-results.json` — D41-A：信用稳定（Lyapunov 稳态存在），D41-B：理性反超但无交叉点，D41-C：需优化相变检测，D41-D：实名优势 2529.8%

### D42：流量经济
- `d42-traffic-economy-simulation.py` — 信息网络结构对经济网络的影响（4 命题验证：信息寡头相变、不平等放大、中介租金均衡、市场有效性崩溃）
- `d42-results.json` — D42-A：相变检测通过，D42-B：经济不平等放大成立，D42-C：τ*=1/λ 验证通过，D42-D：市场有效性崩溃

### D28：正交维度的关联生成理论
- `d28-orthogonal-association.py` — 正交幻觉定理 + 类比路径最短性 + 度规退化 + 正交-独立不等式（4 命题）
- `d28-results.json` — D28-A 低维幻觉 0.888 > 高维 0.511, D28-B 类比距离比 0.897, D28-C 退化成立, D28-D 边界 100%

### D29：方法论的矛盾
- `d29-methodological-contradiction.py` — 不完备性定理 + 悖论分类 + 创造性势能 + 不一致传递（4 命题）
- `d29-results.json` — D29-A 不完备性恒成立, D29-B 互斥性 1.0, D29-D R²=0.998

### D30：层级数据理论与 CoT 模型大小下限
- `d30-hierarchical-data-cot.py` — 层级深度最优 + CoT 下限 + RAG 带宽权衡 + 冗余压缩对偶（4 命题）
- `d30-results.json` — D30-A L*=3, D30-B R²=1.0, D30-D 相反符号 100%

### D43：历史周期率 — 正负反馈动力学
- `d43-history-cycle-feedback-dynamics.py` — 正反馈相变 + 负反馈吸引域 + 极限环 + 临界衰减率（4 命题）
- `d43-results.json` — D43-A 相变 α*=1.2 确认, D43-B 吸引域稳定, D43-C 极限环 6/6 存在

### D44：耦合的非双射自由度
- `d44-coupling-decoupling-beyond-bijection.py` — 耦合度非双射定义 + 最小步解耦 + 测试下界 + 渐近存在性（4 命题）
- `d44-results.json` — D44-A 非对称 0.279 > 对称 0.053, D44-D 耦合随维度递减, 完美耦合 3/20 渐近存在

### D45：自证预言的正反馈动力学
- `d45-self-fulfilling-prophecy-dynamics.py` — 信念 S 形增长 + 临界点相变 + 外部干预抑制 + 记忆持久性（4 命题）
- `d45-results.json` — D45-A S 形增长确认, D45-B 高敏感相变更强, D45-C 干预抑制率 0.961, D45-D 最长半衰期 1 年留存 0.707

### D46：自适应多尺度理论
- `d46-adaptive-scale-transition-dynamics.py` — 多尺度动态切换实验（4 命题：必要性、复杂度匹配、单尺度惩罚、记忆持久性）
- `d46-results.json` — D46-A 多尺度优势 2.27%, D46-B R²=-0.987, D46-C 平均惩罚-0.016, D46-D 半衰期→保留率

### D47：多尺度工具选择动力学
- `d47-multi-scale-tool-selection-dynamics.py` — 自适应路由实验（4 命题：Pareto 最优边界、路由匹配、固定工具惩罚、决策持续）
- `d47-results.json` — D47-A Pareto 最优 3 工具, D47-B R²=1.0, D47-C 能力下降 37.15%, D47-D 半衰期→保留率

### D48：发现同步临界点动力学
- `d48-discovery-criticality-dynamics.py` — 科学发现相变实验（4 命题：临界点、拓扑依赖、涨落发散、机制切换）
- `d48-results.json` — D48-A ρ_c=0.100, D48-B 拓扑依赖显著, D48-C 4.6x 方差放大, D48-D 半衰期→合作比值

### D49：探索-利用折衷动力学
- `d49-exploration-exploitation-tradeoff-dynamics.py` — 工具搜索频率优化实验（4 命题：最优折衷、时间动态、先验影响、过探索惩罚）
- `d49-results.json` — D49-A λ*=0.902, D49-B 比值≈3, D49-C 斜率=-0.8, D49-D 失败率 0→100%

### D4-S18：梯度锁定实验（已迁移至 chimera_lab）
- `phase_transition_analysis.py` — D4-S18-r18 相变分析实验
- `phase_transition_discovery_experiment.py` — D4-S18-r16 相变发现实验
- `timing_var_params_experiment.py` — D4-S18-r16 时序参数实验

### D50：冷启动信息扩散动力学
- `d50-cold-start-diffusion-dynamics.py` — Cahn-Hilliard 方程 + 相变理论（4 命题：涌现临界阈值、遗忘率影响、注入策略、路径迟滞）
- `d50-results.json` — D50-A ρ_c≈0.152，D50-B 遗忘率↔ρ_c 正相关，D50-C burst 最优效率 48.4x，D50-D 迟滞需优化

### D51：多Agent信息博弈
- `d51-multi-agent-information-game.py` — 博弈论 + 信息瓶颈 + 最大熵（4 命题：信息守恒、竞争强度、纳什均衡最大熵、信息囤积）
- `d51-results.json` — D51-A 信息守恒 SD=0.0309，D51-C 纳什熵率 0.458（部分成立）

### D52：频率-动力学对偶理论
- `d52-frequency-dynamics-duality.py` — Euler-Lagrange + 记忆阻尼振荡（4 命题：最优路径振荡、记忆核衰减压冲、预规划-回调博弈、长期记忆滞后）
- 状态：**需调优** — 模型可运行但区分度不足，D52-A R=-0.14（弱），D52-D 检测阈值过严
- 来源：D3-1（频率-动力学对偶猜想）+ 黏弹性力学

---

*创建时间：2026-05-04 | 更新：2026-05-04 D50/D51 完成 + D52 待调优*
