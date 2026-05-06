"""D1-r02 对话流分析原型验证"""
from modules.cognitive_topology.char_hash import CognitiveTopologyEstimator

dialogue = "我在想一个很有意思的问题：耦合振荡器的 chimera 态是否真实存在，还是我们只是错误地解释了观测数据。通过统计分析我发现所有 chimera 检测都是伪阳性。现在关键问题是：那我们在高耦合强度下观测到的多相凝聚是什么？从统计力学角度看，这更像是噪声和耦合竞争产生的多稳态。这让我想到认知过程，I_C 不变量是否能在概念空间中描述思维状态的演化？"

est = CognitiveTopologyEstimator(n_dim=64, window=3)
result = est.full_analysis(dialogue)
print(f"I_C: {result['I_C']}")
print(f"|dI_C/dt|: {result['dIC_dt']}")
print(f"T_cog: {result['T_cog']}")
print(f"IC sequence: {result['ic_sequence']}")
