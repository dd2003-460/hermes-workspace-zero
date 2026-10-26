# Step 04: GPU 子模块方法论整理

## 目标
把 step-02 抓取的 arena 会话中 GPU PRO 系列专业卡价格预测的完整方法、假设、TCO 计算逻辑整理成结构化方法文档，作为模型实现和 tex 报告的依据。

## 涉及文件
- `market-alpha/gpu-price-prediction/docs/methodology.md`（方法文档）
- `market-alpha/gpu-price-prediction/docs/assumptions.md`（假设清单）

## 做法
1. 通读 `data/arena-session-raw.md`，抽取：
   - 预测目标定义（哪些 PRO 卡型、价格口径：发售价/市场价/二手价）
   - TCO 计算方法（购买成本+电费+折旧+运维，公式与全部参数）
   - 价格预测模型（原会话用什么方法：时间序列/供需/类比推理，完整保留）
   - 历史预测轮次（每轮：时间点、目标卡型、预测值、依据）——用户强调"轮次注意区分"
2. 写 methodology.md：问题定义 → 数据 → TCO 方法（含公式）→ 价格预测方法 → 轮次设计 → 验证方式
3. 写 assumptions.md：假设逐条列出，每条标注来源（会话原文位置）+ 置信度（高/中/低）+ 敏感性说明
4. 原会话未覆盖的空缺显式标 "TODO: 待 arena 核验补充"

## 验收标准
- [ ] methodology.md 含 6 节完整方法链，TCO 公式与参数完整
- [ ] assumptions.md ≥5 条假设，每条有来源+置信度
- [ ] 会话中关键数字（卡型/价格/TCO 参数/轮次）全部保留可追溯（抽样 5 项核对）
