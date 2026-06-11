# Iteration 227: gap_filler 上下文提取完整修复 — #### 标题边界 + 元数据过滤

## 目标
修复 gap_filler 上下文提取 — 从源文件提取 key_point/secondary_point 时混入了模板建议和元数据 footer。

## 执行动作

### persona_v3_gap_filler.py 修改
1. **重构 extract_context()**: 段落现在带 heading 上下文存储 (元组 (heading, text))
2. **SUGGESTION_HEADINGS 常量**: 定义 6 个建议区块标题, 检测 #### 边界
3. **in_suggestion 状态**: 在 #### 标题下跳过整个建议区块
4. **元数据过滤**: `**` 和 `>` 行总是跳过, 不受 suggestion 模式影响

### 验证
- 所有上下文字段 (key_point, secondary_point, perspective_1, perspective_2) 现在来自源内容
- 无模板残留, 无元数据 footer 混入

### 效果对比
| 字段 | 修复前 | 修复后 |
|------|--------|--------|
| key_point | 模板残留文本 | "成璐问了一个关于**数据表示的结构**的根本问题" |
| secondary_point | "后验信念: ..."(自适应先验模板) | "形式化: 设训练数据 X 的分布为 P(X)" |
| perspective_1 | 混合元数据+模板 | "与 idea 20/44 形成统一的三层框架" |
| perspective_2 | "后验信念: ..."(自适应先验模板) | "不要将训练数据视为 flat distribution" |

## 影响
- gap_filler 建议质量显著提升 (上下文感知从"部分"到"可靠")
- TEMPLATE_MARKERS 过滤不再需要 (被更精准的边界检测取代) — 后续迭代可清理
- 四个工具改进后, gap_filler 的上下文质量问题完全解决
