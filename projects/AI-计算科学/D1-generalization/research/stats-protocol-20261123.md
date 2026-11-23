# P5 · 统计口径定义（2026-11-23）
# origin: ai · 用途：formula-judge 论文所有数字的复现口径，缺了这些数字没法跨报告复现

## 为什么先定口径
论文要报"机械 judge vs LLM judge"的对比数字（一致率/翻转率/CI）。
不定口径就开跑，数字没法复现、没法被审稿人质疑时自证。
先定口径 = 给后面所有实验画了把尺子。

## 1. 一致率（agreement rate）
**定义**：机械 judge 与 LLM judge 对同一 (题, 模型输出) 判分结论相同的比例。
**口径**：
- 分母 = 全部 (题 × 输出) 对数 N
- 分子 = 两者判"对"或两者判"错"的对数
- **必须按检查点粒度报**（不是按题粒度）：一题 3-5 检查点，逐点判一致
- 报法：`agreement = n_same / N`，附 N 和 n_same 原始数
- **tie-break**：LLM judge 输出"部分对"时，映射规则 = 任一检查点错即整题错（与机械 judge 的"全对才得分"对齐）

## 2. 翻转率（flip rate）
**定义**：两者判分结论**相反**的比例 = 1 - agreement（按检查点）。
**但翻转要分两类**（这是论文的核心，不能只报总数）：
- **真翻转**：机械 judge 对、LLM judge 错（或反之）——需要 gold 仲裁
- **假翻转**：两者都错但错得不一样（罕见，记录即可）
**口径**：
- 仲裁者 = gold（SymPy 精确值 / datasheet 事实 / 预置 0-1），**不用第三个 LLM**
- 报法：`flip_true = n_mech_correct_llm_wrong / N`，`flip_llm_correct_mech_wrong = ...`
- 两个方向分开报（不对称才是信息：机械 judge 系统性在哪边偏）

## 3. 置信区间（CI）
**定义**：一致率/翻转率的 95% CI。
**口径**：
- **用 Wilson score interval**（不是 Wald）：小样本 + 比例接近 0/1 时 Wald 失真
- 报法：`p ± z*` 改成 `p [Wilson CI: lo, hi]`
- **聚类修正**：同一题的多个检查点不独立（c2 依赖 c1），CI 要按**题**聚类（cluster-robust），不能按检查点
  - 实现：以题为聚类单位，用 DeLong 或 bootstrap（重采样题，不重采样检查点）
  - bootstrap 次数 = 1000，固定 seed（报 seed 值）
- **为什么聚类**：qqbot 已证"聚合谬误"（把 run 内变化平均掉会反方向）——检查点内相关同理，不聚类 CI 会偏窄

## 4. judge 族标注（pfb G2 F2(a) 硬约束）
**定义**：每个 judge 的底座 + 版本 + 是否 IRR（独立重复）。
**口径**：
- 机械 judge：`formula_judge v0.1 (SymPy 1.14, 2% tol)`
- LLM judge：`qwen3.8-27b-mtp @8787, prompt v<版本>, temperature 0`
- **同底座两遍 ≠ 家族独立**：27b 判两次只算"上下文独立"不算"家族独立"
- 宣称真 IRR 需 ≥2 不同底座（如 27b + 一个外部 API judge）
- 论文里所有 κ/一致率必须带 judge 族标注，否则审稿人按"同源偏差"拒

## 5. 秩亏题的额外口径（校准腿专用）
**定义**：秩亏题不报"一致率"（没有标准答案可对齐），报**批判准确性**：
- `gap_detection_rate`：模型识别"来源不足"的比例（gold=1 的题里判 1 的比例）
- `gap_localization_rate`：准确说出缺哪个量的比例（在 gap_detection 的子集里）
- `hallucination_rate`：幻觉出缺失值的比例（gold=0 的题里编了个数的比例）
- 三个分开报，CI 同样按题聚类
- **为什么分开**：检测准 ≠ 定位准 ≠ 不幻觉，是三个不同能力维度，混报会掩盖哪个断了

## 6. 防 hack 口径（数值不凑整的验证）
- 每题 gold 必须含 ≥1 个无理数/非整数（防 memorization）
- 检查点间依赖链：c_k 的 gold 计算依赖 c_{k-1} 的中间量（防逐点独立蒙对）
- 验证方法：把 c_{k-1} 的中间量错 5%，c_k 的 gold 应跟着变（脚本自动检查依赖链存在）

## 留空（待 P1 题集落地后填）
- [ ] N 的具体值（10 题 × 每题输出数 × 检查点数）
- [ ] bootstrap seed 值
- [ ] 27b judge prompt 版本号（待 P2 版本化后定）
- [ ] 外部 API judge 选型（P2 依赖，需异构底座）
