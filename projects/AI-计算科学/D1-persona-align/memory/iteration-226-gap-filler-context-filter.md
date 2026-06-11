# Iteration 226: gap_filler 上下文提取模板残留过滤

## 目标
修复 gap_filler 上下文提取 — 之前从源文件提取 key_point/secondary_point 时, 混入了之前 --apply 生成的模板建议段落。

## 执行动作

### persona_v3_gap_filler.py 修改
- extract_context() 新增 TEMPLATE_MARKERS 过滤
- 过滤掉包含模板特征词的段落: 磨刀理论、探索策略、贝叶斯闭环、同构映射、观测者视角等 21 个特征词
- 新增: "后验信念", "injection_point", "补全建议" 等残留标记

### 验证
- idea-01 测试: key_point 从模板残留改为实际源内容 "形式化: 设训练数据 X 的分布为 P(X)"
- secondary_point 仍有少量自适应精度模板残留 (待改进)

### 已知问题
- secondary_point 仍可能混入其他维度模板 (如自适应精度、自适应先验)
- 完整修复需要检测 #### 标题区块边界, 跳过整个 suggestion section

## 影响
- key_point 提取质量显著提升
- secondary_point 改善但非完美
- 完整的区块边界检测是后续改进项
