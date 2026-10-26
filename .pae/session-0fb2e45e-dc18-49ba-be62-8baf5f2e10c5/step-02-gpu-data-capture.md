# Step 02: GPU 价格预测会话数据抓取（arena）

## 目标
用 ego-browser 打开 arena.ai/agent，找到用户已有的"预测显卡价格"会话（PRO 系列专业卡 TCO 计算与价格平衡），完整抓取对话内容落盘到 GPU 子模块 data/ 目录。

## 涉及文件
- `market-alpha/gpu-price-prediction/data/arena-session-raw.md`（原始会话全文）
- `market-alpha/gpu-price-prediction/data/README.md`（数据来源说明：会话 URL、抓取时间、完整性）
- 备选数据源：`projects/AI-计算科学/archive/gpu-to-decomp/`（本地 GPU 调研归档，含 D1-gpu-research-2026、D1-gpu-inference-hardware）

## 做法
1. ego-browser 打开 `https://arena.ai/agent`，进入会话列表
2. 定位"预测显卡价格"会话（关键词：PRO 系列/专业卡/TCO/价格预测）
3. 逐屏滚动抓取完整对话（用户 prompt + AI 回复 + 代码块 + 表格 + 轮次记录），拼接去重
4. 重点提取：TCO 计算公式与参数、价格预测方法、历史预测轮次（每轮时间/预测值/依据）、PRO 系列卡型清单
5. 落盘 raw 全文 + 写 data/README.md 记录来源元数据
6. **降级路径**：若 arena 会话不可达/找不到 → 从本地 `gpu-to-decomp` 归档提取 TCO/价格相关产物作为数据源，data/README.md 明确标注"来源=本地归档（arena 会话不可达降级）"

## 验收标准
- [ ] `arena-session-raw.md` 落盘且 >5KB，含可识别的 TCO/价格预测/轮次内容
- [ ] data/README.md 记录来源、抓取时间、完整性说明
- [ ] 卡型清单、TCO 参数、历史轮次数据可从中提取（抽样验证 3 项）
