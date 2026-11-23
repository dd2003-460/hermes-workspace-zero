# T-PUB-1 方法学缺口 follow-up（arena agent 自述 7 条，2026-11-23 核验时登记）
# 来源：① arena 交付 tasks/T-PUB-1-result.md §方法学缺口 · commit b148b12ed

| # | 缺口 | 影响 | 处置 |
|---|------|------|------|
| 1 | fact gold 可访问性只到"产品规格页"，未逐份下载 NVIDIA PDF datasheet 校验 | fact 类检查点的 source 权威性略降 | 非阻塞；正式投稿前补 PDF 校验（或接受规格页级） |
| 2 | Q03 c1 是"数值推导"（1979÷2=989.5 dense）非纯事实，与 NVIDIA 标称 989.4 差 0.01% | tol 设 1% 已覆盖 | 非阻塞；论文里注明 dense 约定 |
| 3 | Q09 c3"禁止输出 tok/s"会误伤"先标缺口再补外部事实给数"的正确行为 | 秩亏题判分可能过严 | **需 pilot 校准**：正式版改"数值必须与缺口声明同段" |
| 4 | Q08/Q10 bool 判定依赖关键词/同义词表，agent 未给完整正则库 | 秩亏批判准确性判分有假阳/假阴 | **阻塞项**：Lead 需补正则库（formula_judge.py 的 bool 分支） |
| 5 | Q05 的 3.71ms 层计算时间是人为给定（收敛成纯带宽题），非 benchmark 取 | 非"全链条可推" | 非阻塞；论文注明 |
| 6 | Q06/Q07 纯数学/物理无外部来源，抗 memorization 靠"数值不凑整"非"来源新" | 这两题的防 hack 弱一档 | 非阻塞；已知 |
| 7 | 模型规模/架构是"真实量级但非具体开源模型"组合，c2 无官方 spec 页背书只有公式背书 | KV 参数类检查点无 datasheet | 非阻塞；公式背书可接受 |

~~**阻塞项**：#4（bool 正则库）~~ **已解除 11-23**：formula_judge.py 加 judge_bool（spec 驱动：keywords/forbidden_numbers/forbidden_patterns，支持'通过即缺席'型检查点）；T-PUB-1 的 8 个 bool 检查点已补判分字段（Lead 核 gold）；冒烟 9/9 通过。
**需校准**：#3（Q09 c3 过严）——pilot 里看 27b 实际行为再定。
