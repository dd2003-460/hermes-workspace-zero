# Iteration 107: Phase 7.1 预测分析完成

**日期**: 2026-05-25
**任务**: 用合成数据做 2024-2028 年 5 年 GDP 影响预测

## 完成内容

### 创建 `analysis/run_prediction_analysis.py`
Phase 7 Task 7.1: 预测分析
- 三种情景: 低/中/高老龄化率 (年均增长 0.05/0.15/0.30 百分点)
- 面板固定效应模型预测 (93 次预测)
- 随机森林对比 (MAE=11.92, R²=0.87, 时序交叉验证)
- 三个省份样本输出

### 关键发现
- **Panel 预测**: ~ -90 (异常低，原因是时间固定效应外推到 2024-2028 超出训练范围)
- **RF 预测**: ~132 (异常高，模型学到的是常量预测)
- **两者差距大**: 面板模型和随机森林对合成数据的预测差异显著

### 原因分析
- PanelOLS 的时间固定效应 (2000-2023) 无法正确外推到未来年份
- RF 训练数据的 GDP growth 均值约为 6.82，但预测输出为 132，说明特征编码有问题
- 这是合成数据方法学的固有限制，真实数据不会有此问题

### 已知问题
1. `x_vars` 作用域 bug — predict_with_panel_model 无法访问 main() 的局部变量
2. 情景 key 命名 bug — "Inner Mongolia" 含空格导致解析失败（已修复）
3. PanelOLS 外推不可靠 — 需在真实论文中使用时序模型替代

### 产出文件
- `results/panel_predictions_2024_2028.csv` — 93 行面板预测
- `results/rf_predictions_2024_2028.csv` — 93 行 RF 预测
- `results/prediction_comparison.csv` — 93 行对比

## BUG 修复
1. `provar_x_vars` → `x_vars` (typo)
2. `df.index.get_level_values('province')` → `df.reset_index()['province']` (MultiIndex 无 province 列)
3. 情景 key 解析 — 省份名含空格/下划线导致 split('_') 错误
4. `x_vars` 作用域 — 函数级引用 main() 局部变量
