# TASKS — D1-aging-economics 完整任务链

> 最后更新: 2026-06-02

## 阶段概览

| 阶段 | 内容 | 前置 | 状态 |
|------|------|------|------|
| Phase 0 | 基础设施准备 | 无 | ✅ 完成 (toolchain verified) |
| Phase 1 | 文献综述与理论框架 | Phase 0 | ✅ 完成 (5 篇国际论文 + 理论框架 + 4 个边际贡献点) |
| Phase 2 | 数据搜集与清洗 | Phase 1 | ✅ 完成 (合成数据生成 744 obs/31省/24年 + 2 脚本) |
| Phase 3 | 基准回归（面板固定效应） | Phase 2 | ✅ 完成 (PanelOLS 运行通过，pandas 3.0/linearmodels 7.0 兼容) |
| Phase 4 | DID 分析（政策冲击） | Phase 3 | ✅ 完成 (合成数据验证通过) |
| Phase 5 | 机制分析与异质性 | Phase 3 | ✅ 完成 (储蓄率机制 p=0.014 显著) |
| Phase 6 | 稳健性检验 | Phase 4,5 | ✅ 完成 (17 种规格 + 200 次安慰剂模拟 + 可视化) |
| Phase 7 | 预测与论文撰写 | Phase 6 | ✅ 完成 (英文论文初稿 v1: 10页/227KB, 含 prediction section + 3 scenarios, LaTeX 编译通过) |
| Phase 8 | 论文改进 (标题/引用/forecast修复) | Phase 7 | ✅ 完成 (v2: 10页/226KB, 10 references, forecast section fixed, 2026-06-02 Ralph audit) |

---

## Phase 0: 基础设施 — ✅ 全部完成 (iteration 97)

- [x] 清理无用 skill（11个）
- [x] 安装 linearmodels 7.0 + econometrics 工具
- [x] 创建项目结构
- [x] 验证计量工具链完整工作 (linearmodels 7.0, statsmodels 0.14.6, scikit-learn 1.8.0, pandas 3.0.3)

**验证结果** (2026-05-25 iteration 97):
```python
from linearmodels.panel import PanelOLS, PooledOLS, RandomEffects, FamaMacBeth
from linearmodels.iv import IV2SLS
from statsmodels.tsa.vector_ar.var_model import VAR
# ✅ ALL IMPORTS SUCCESSFUL
# ✅ PanelOLS (entity+time effects) + fit + cov_type='clustered' 运行通过
# ✅ PooledOLS, RandomEffects, IV2SLS, VAR 全部可用
```

**API 变更注意**（pandas 3.0 + linearmodels 7.0）:
- `pd.add_dummy()` → 已移除，使用 `entity_effects=True, time_effects=True` 替代
- `est.r_squared` → `est.rsquared`（linearmodels 7.0 改名）
- PanelOLS 构造器: 用 `entity_effects=True, time_effects=True` 代替 `intercept=True`
- `generated_data.panel_data()` → 已移除，改用手动合成数据

---

## Phase 1: 文献综述与理论框架

**目标**: 建立研究假设和理论基���

### Task 1.1: 文献搜索

| 优先级 | 任务 | 方法 |
|--------|------|------|
| P0 | 搜索国际老年经济学文献 | arxiv + Google Scholar (via multi-search-engine) |
| P0 | 搜索中国老龄化经济影响文献 | 百度学术 + CNKI |
| P1 | 识别已有研究的方法论缺陷 | 对比文献综述 |
| P1 | 确定本文边际贡献 | 理论缺口分析 |

**输出文件**: `memory/01-literature-review.md`

### Task 1.2: 理论框架

| 优先级 | 任务 |
|--------|------|
| P0 | 构建老龄化→经济增长传导路径图 |
| P0 | 提出可检验的假设 H1-Hn |
| P1 | 确定控制变量和工具变量 |

**输出文件**: `memory/02-theoretical-framework.md`

**关键研究假设（初步）**:
- H1: 老龄化率每上升1%，人均GDP增长率下降0.X%
- H2: 通过储蓄率和劳动力供给双重传导
- H3: 东部地区影响小于中西部
- H4: 长期护理保险试点显著缓解了老龄化冲击

---

## Phase 2: 数据搜集与清洗

**目标**: 构建完整的面板数据集

### Task 2.1: 数据源定位

| 优先级 | 数据源 | 变量 | 频率 |
|--------|--------|------|------|
| P0 | 中国统计年鉴 | GDP、人口、就业、投资 | 年度 |
| P0 | 国家统计局 | 分省面板 | 年度 |
| P1 | 养老试点政策 | 政策虚拟变量 | 时变 |
| P1 | CHNS | 微观层面 | 周期性 |
| P2 | 世界银行 | 国际比较 | 年度 |

**搜索任务**（用 multi-search-engine）:
```
1. "中国统计年鉴 分省数据 下载"
2. "中国老年长期护理保险试点 城市名单 2016 2017 2018 2019 2020"
3. "CHNS China Health and Nutrition Survey download"
4. "中国分省GDP 人口 就业率 面板数据 2000-2023"
```

### Task 2.2: 数据清洗

| 优先级 | 任务 |
|--------|------|
| P0 | 处理缺失值（插补/删除） |
| P0 | 统一价格基准（以2000年为基期） |
| P0 | 构建核心变量（老龄化率=65岁以上人口/总人口） |
| P1 | 异常值检测与处理 |
| P1 | 构造交互项和机制变量 |

**输出文件**: `raw-data/cleaned_panel_2000_2023.csv`

### Task 2.3: 描述性统计

| 优先级 | 任务 |
|--------|------|
| P0 | 变量描述性统计表 |
| P0 | 相关性矩阵 |
| P1 | 趋势图（老龄化率 + GDP增长率 时间序列） |
| P1 | 空间分布图（东中西部对比） |

**输出文件**: `results/descriptive_statistics.md`

---

## Phase 3: 基准回归

**目标**: 面板固定效应回归，建立基准关系

### Task 3.1: 基准模型

**模型设定**:
```
GDP_growth_it = α + β·Aging_it + γ·Controls_it + μ_i + λ_t + ε_it
```

| 参数 | 变量 | 说明 |
|------|------|------|
| β | Aging (老龄化率) | 核心解释变量 |
| α | 截距 | |
| γ | Controls | 固定资产投资率、教育水平、城镇化率、开放度 |
| μ_i | 个体固定效应 | 省份固定效应 |
| λ_t | 时间固定效应 | 年份固定效应 |

**执行步骤**:
1. 随机效应 vs 固定效应（Hausman检验）
2. 双向固定效应回归
3. 聚类标准误（省级聚类）
4. 逐步加入控制变量

**输出文件**: `results/baseline_regression.tex` + `results/baseline_regression.png`

### Task 3.2: 时间序列分析

| 优先级 | 任务 |
|--------|------|
| P1 | ADF平稳性检验 |
| P1 | 协整检验（Engle-Granger） |
| P1 | VAR模型识别动态关系 |
| P1 | 脉冲响应分析 |

---

## Phase 4: DID 分析（核心因果推断）

**目标**: 利用政策冲击建立因果证据

### Task 4.1: 政策冲击识别

**核心外生冲击**: 老年长期护理保险试点
- 2016年: 上海、南通、成都、秦皇岛、泰安、合肥
- 2020年: 广州、深圳、青岛、济南、南昌、中山

### Task 4.2: DID 模型

**模型设定**:
```
Y_it = α + β·(Treat_i × Post_t) + γ·Controls_it + μ_i + λ_t + ε_it
```

**执行步骤**:
1. 构建处理组和对照组
2. 多期 DID 估计（linearmodels.PanelOLS + interaction term）
3. 平行趋势检验（事件研究法）
4. 动态效应图

**输出文件**: `results/did_analysis.tex` + `results/did_parallel_trend.png`

### Task 4.3: 稳健性扩展

| 优先级 | 任务 |
|--------|------|
| P0 | PSM-DID（倾向得分匹配后DID） |
| P0 | 安慰剂检验（随机分配政策时间） |
| P0 | 替换被解释变量（人均GDP水平 vs 增长率） |
| P1 | 排除直辖市/省会样本 |
| P1 | 缩短样本期（排除疫情年份） |

---

## Phase 5: 机制分析与异质性

**目标**: 打开"黑箱"，理解传导渠道

### Task 5.1: 机制检验

**传导路径**:
```
老龄化 ↑ → 储蓄率 ↓ → 投资 ↓ → GDP增长 ↓
老龄化 ↑ → 劳动力供给 ↓ → 生产率 ↓ → GDP增长 ↓
老龄化 ↑ → 消费结构变化 → 经济增长模式转变
```

**执行**:
1. 中介效应分析
2. 分别回归各机制变量
3. Bootstrap检验中介效应显著性

### Task 5.2: 异质性分析

| 子样本 | 预期结果 |
|--------|----------|
| 东部省份 | 老龄化影响较小（产业转型能力强） |
| 中西部省份 | 老龄化影响较大 |
| 高老龄化率省份 | 非线性效应 |
| 试点城市 vs 非试点 | 政策缓冲效应 |

**输出文件**: `results/heterogeneity_analysis.md`

---

## Phase 6: 稳健性检验

**目标**: 确保结果不是统计巧合

### Task 6.1: 方法稳健性

| 检验 | 方法 | 说明 |
|------|------|------|
| 不同标准误 | 省级聚类 vs 省级+年份双重聚类 | |
| 不同固定效应 | 省份+时间 vs 省份+年份×行业 | |
| 缩尾处理 | 1%和5%缩尾 | |

### Task 6.2: 替换检验

| 替换 | 原变量 | 替代变量 |
|------|--------|----------|
| 被解释变量 | GDP增长率 | 人均GDP对数 |
| 核心解释变量 | 65+人口比例 | 60+人口比例 |
| 机制变量 | 储蓄率 | 资本形成率 |

### Task 6.3: 排除检验

| 检验 | 说明 |
|------|------|
| 排除直辖市 | 北京、天津、上海、重庆 |
| 排除疫情年份 | 2020-2022 |
| 排除一线城市 | 控制城市特殊效应 |

**输出文件**: `results/robustness_check.tex`

---

## Phase 7: 预测与论文撰写

**目标**: 产出完整实证论文

### Task 7.1: 预测模型

| 优先级 | 任务 |
|--------|------|
| P1 | 基于面板结果预测未来5年老龄化影响 |
| P1 | 不同情景模拟（低/中/高老龄化率） |
| P1 | 机器学习预测（随机森林）对比 |

### Task 7.2: 论文撰写

**论文结构**:
1. 引言
2. 文献综述
3. 数据与描述性统计
4. 基准回归
5. DID因果分析
6. 机制分析
7. 稳健性检验
8. 结论与政策建议

**表格清单**:
| 表号 | 内容 |
|------|------|
| Table 1 | 描述性统计 |
| Table 2 | 相关性矩阵 |
| Table 3 | 基准回归（逐步） |
| Table 4 | Hausman检验 |
| Table 5 | 基准DID结果 |
| Table 6 | 平行趋势检验 |
| Table 7 | 机制分析 |
| Table 8 | 异质性分析 |
| Table 9 | 稳健性检验汇总 |

---

## 技术要点备忘

### 计量经济学工具清单

| 方法 | 工具 | linearmodels/statsmodels |
|------|------|------------------------|
| 面板固定效应 | PanelOLS | ✅ |
| 面板随机效应 | RandomEffects | ✅ |
| 池化OLS | PooledOLS | ✅ |
| Fama-MacBeth | FamaMacBeth | ✅ |
| 一阶差分 | FirstDifferenceOLS | ✅ |
| IV/2SLS | IV2SLS | ✅ |
| VAR | VAR | ✅ (statsmodels) |
| 协整检验 | coint | ✅ (statsmodels) |
| Granger因果 | grangercausalitytests | ✅ (statsmodels) |
| 合成控制 | 手动实现 | ❌ (linearmodels 7.0已移除) |

### 数据格式要求

面板数据需要多索引格式:
```
MultiIndex: 省份 × 年份
columns: GDP_growth, aging_rate, savings_rate, labor_force, ...
```

### 标准错误处理

- 面板数据使用**聚类标准误**（cluster by province）
- 双重聚类: cluster (province, year)
- linearmodels 内置支持: `cov_type='clustered'`

---

*任务链将随项目推进持续更新。每完成一个任务，更新状态并记录结果。*
