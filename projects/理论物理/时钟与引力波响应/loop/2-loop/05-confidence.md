# 05-confidence（置信度检查）

**所属规格**：`/Users/a1-6/Desktop/workspace/loop/2-loop/05-confidence.md`
**状态**：completed
**输入**：loop/2-loop/04-verify.md 产出
**输出**：confidence-report.md

---
## 产出内容

### 置信度评估

| 方面 | 置信度 | 说明 |
|------|--------|------|
| 公式正确性 | 0.90 | 空间 OLC 传递函数使用与 1-loop 一致的公式 |
| 数据一致性 | 0.95 | CSV 数值与 PNG 图一致，npz 数据可复载 |
| 物理合理性 | 0.85 | 灵敏度量级正确，但空间噪声参数是估计值 |
| 可视化准确性 | 0.90 | 六面板布局清晰，物理趋势正确 |

### 综合置信度
**overall_confidence = 0.85** — **高于阈值 0.6 → 进入 06-decision**

### 不确定性来源
1. 空间 OLC 噪声参数是估计值（非精确文献引用）
2. Taiji/TianQin 灵敏度参数来自公开文档估算
3. 干涉仪比较未考虑真实任务配置（如激光功率、测试质量等细节）

### 改进建议
- 引入最新的 LISA/Taiji/TianQin 设计灵敏度曲线
- 空间 OLC 噪声参数从 Schaffrath 论文精确提取

---
## 完成时间
last_completed_at: 2026-06-30

---
## 回滚
若置信度 < 0.6，回到 04-verify 或 03-execute
