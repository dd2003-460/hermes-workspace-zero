# Step 04: GPU 价格预测方法论整理

## 目标
把抓取到的 arena 会话中 GPU PRO 系列专业卡价格预测的完整方法、假设、TCO 计算逻辑整理成结构化方法文档，作为模型实现和 tex 报告的依据。

## 涉及文件
- `market-alpha/gpu-price-prediction/docs/methodology.md`（方法文档）
- `market-alpha/gpu-price-prediction/data/assumptions.md`（假设清单：每条假设标注来源+置信度）

## 做法
1. 通读 step-02 落盘的会话 raw，抽取：
   - 预测目标定义（哪些卡型、价格口径：发售价/市场价/二手价）
   - TCO 计算方法（购买成本+电费+折旧+运维，公式与参数）
   - 价格预测模型（时间序列/供需/类比推理等，原会话用什么方法就用什么）
   - 已做的预测轮次（用户要求"轮次注意区分"：每轮预测的时间点、预测值、实际值）
2. 整理成 methodology.md：问题定义 → 数据 → 方法 → 假设 → 验证方式
3. 假设逐条列出，标注 confidence（高/中/低）和依据
4. 空缺项（原会话没覆盖的）明确标 "TODO: 待 arena 核验补充"

## 验收标准
- [ ] methodology.md 含完整方法链（目标/数据/方法/假设/验证 5 节）
- [ ] assumptions.md 假设 ≥5 条，每条有来源和置信度
- [ ] 原会话中的关键数字（卡型、价格、TCO 参数）全部保留可追溯
