# Step 08: 变压器板块估值模型实现

## 目标
基于 step-07 方法文档，用 Python 实现变压器板块估值模型：个股估值分位计算 + 目标价模型 + 贡献因子分解回测，输出可复算结果。

## 涉及文件
- `market-alpha/transformer-sector-valuation/src/config.py`（标的全清单 + 财报数据 + 美股对标数据）
- `market-alpha/transformer-sector-valuation/src/valuation.py`（PE/PS 分位 + 目标价区间计算）
- `market-alpha/transformer-sector-valuation/src/decomposition.py`（贡献因子对数分解：盈利预期修正 vs 估值压缩）
- `market-alpha/transformer-sector-valuation/src/global_compare.py`（A 股 vs 美股/日韩估值对比表）
- `market-alpha/transformer-sector-valuation/src/main.py`（入口，产出 outputs/round-1/）
- `market-alpha/transformer-sector-valuation/outputs/round-1/`（估值Snapshot + 目标价表 + 分解结果 JSON）

## 做法
1. config.py 把元宝报告中的财务/行情数据结构化（每股：现价、高点、回撤、PE-TTM、EPS 预测、订单、毛利率、现金流）
2. valuation.py：输入 EPS 预测 + 目标 PE 区间 → 目标价；板块 PE/PS 分位复算
3. decomposition.py：实现元宝会话中的对数分解法（如思源案例：-56.1% = 盈利修正 15-19% + 估值压缩 81-85%），对所有覆盖标的复算
4. global_compare.py：生成 A 股 vs GEV/ETN/VRT 等对比表（回撤、YTD、估值倍数）
5. main.py 汇总产出 round-1 JSON + Markdown 汇总表
6. 数据为元宝报告快照（2026-10-26），模型标注数据截止日；只用标准库 + numpy/pandas

## 验收标准
- [ ] `python3 src/main.py` 成功，产出 `outputs/round-1/valuation.json` + `summary.md`
- [ ] 思源电气分解案例复算结果与元宝原文一致（估值压缩占比 81-85%）
- [ ] 目标价表覆盖 ≥8 家 A 股标的，含区间（如金盘 55-100 元）
- [ ] 全球对比表含 ≥3 家美股对标
