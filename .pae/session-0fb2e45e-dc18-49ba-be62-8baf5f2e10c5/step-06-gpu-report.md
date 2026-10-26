# Step 06: GPU 子模块 tex 技术报告 + PDF 编译

## 目标
把 GPU 价格预测的完整方法、假设、模型、结果写成 LaTeX 技术报告并编译成 PDF，达到技术报告/手册质量。

## 涉及文件
- `market-alpha/gpu-price-prediction/reports/report.tex`
- `market-alpha/gpu-price-prediction/reports/report.pdf`
- `market-alpha/gpu-price-prediction/reports/figures/`（matplotlib 生成的 PNG 图）

## 做法
1. 检查 LaTeX 环境：`which xelatex tectonic pdflatex`；全无则安装 tectonic（`brew install tectonic` 或下载单二进制）
2. 报告结构（中文用 xelatex+ctex；若中文字体有问题改英文报告）：
   - 摘要
   - 1. 问题定义（PRO 系列专业卡、价格口径、轮次机制）
   - 2. 数据来源（arena 会话抓取说明）
   - 3. 方法（TCO 公式推导 + 价格预测方法完整描述)
   - 4. 假设清单（表格：假设/依据/置信度/敏感性）
   - 5. 结果（round-1 预测表 + 历史回测胜率）
   - 6. 局限与后续轮次计划
   - 参考文献/数据来源
3. matplotlib 生成 2-3 张图：价格走势+预测区间、TCO 对比、回测胜率
4. 编译，验证 PDF 可打开、中文无乱码、图表正常
5. 报告标注版本 round-1，预留"修订记录"节（供 step-11 arena 核验后更新）

## 验收标准
- [ ] `report.pdf` 存在且 >100KB，文本提取验证含正文
- [ ] 编译零 error（warning 记录在案）
- [ ] 报告含全部 6 节 + 假设表格 + ≥2 张图
- [ ] tex 中公式与 src/ 代码实现一致（抽样核对 TCO 公式）
