# Step 05: GPU 价格预测模型实现

## 目标
基于 step-04 方法文档，用 Python 实现 GPU PRO 系列专业卡价格预测 + TCO 计算模型，支持多轮预测（轮次可区分），输出 round-1 预测结果和历史回测胜率。

## 涉及文件
- `market-alpha/gpu-price-prediction/src/config.py`（卡型清单、价格参数、TCO 参数）
- `market-alpha/gpu-price-prediction/src/tco.py`（TCO 计算模块）
- `market-alpha/gpu-price-prediction/src/model.py`（价格预测主逻辑）
- `market-alpha/gpu-price-prediction/src/backtest.py`（历史轮次回测：预测 vs 实际）
- `market-alpha/gpu-price-prediction/src/main.py`（入口）
- `market-alpha/gpu-price-prediction/outputs/round-1/predictions.json` + `summary.md`

## 做法
1. 按 methodology.md 实现（原会话是规则/类比方法就用规则引擎；有时间序列数据就用简单统计模型——优先可解释，不引入黑盒）
2. 轮次机制：`outputs/round-N/` 目录，`predictions.json` 结构含 round 号、predicted_at、targets[]（卡型/预测价/区间/依据）、method_version
3. TCO 模块：输入卡型+使用场景（电价/负载/年限），输出 3/5 年 TCO，参数可配置
4. backtest：对会话中已有历史轮次计算方向胜率 + 价格偏差
5. 运行 main.py 产出 round-1，验证输出格式
6. 依赖仅标准库 + numpy/pandas（本机 Python3 可用）

## 验收标准
- [ ] `python3 src/main.py` 成功运行，产出 `outputs/round-1/predictions.json`
- [ ] predictions.json 含 round/predicted_at/targets 完整结构
- [ ] TCO 模块对 ≥3 个卡型输出数值且可手动复算验证
- [ ] backtest 对历史轮次给出方向胜率数字（或标注"历史轮次不足，待积累"）
