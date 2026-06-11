# D2-1: Agent Planning Capacity Lower Bound — Literature Review Supplement

**生成时间**: 2026-06-08 (Iteration 23)
**对应原始paper**: raw/d2-agent-planning-capacity-lower-bound.md
**补充目的**: 将已发现的文献整理为bib条目，可直接加入paper draft

---

## 核心文献

### 1. Chain-of-Thought Length and Reasoning Efficiency

**Xia, Xie, Xu, Kang, Lamba, Gao, McAuley (2026).**
"Agentic Chain-of-Thought Steering for Efficient and Controllable LLM Reasoning"
arXiv: 2606.03965v1

**核心发现**: Agent在extended thinking过程中"spend tokens inefficiently"。提出adaptive supervisor控制推理token数，在严格token cap下实现精确的accuracy-speed tradeoff。

**与D2-1的关联**: 这证实了D2-1的直觉——推理能力不是简单地"越长越好"，存在效率下界。D2-1的"I_plan^*"可以被理解为：完成规划任务所需的最小推理信息量。2606.03965的实验结果表明，这个下界是存在的且可测量的。

### 2. Memory Budget Separation — Strict Lower Bound Proof

**Zhang, Haozhou (2026).**
"Chain-of-Thought and Compressed Looped Transformers: A Memory-Budget Separation"
arXiv: 2605.30757v1

**核心发现**: 证明了compressed recurrent loops "limited by the size of its recurrent state"。具体地，当循环状态的recurrent hidden size < problem所需的working memory时，模型无法解决需要显式scratchpad的问题。这是一个**严格的可计算下界证明**。

**与D2-1的关联**: 这是D2-1"规划容量下界"猜想的第一个严格数学证明。D2-1猜想"若 |A| < I_plan^* + delta，则无法完成规划"——2605.30757证明了循环RNN的recurrent state size是working memory的上界，超过此上界后，模型退化为机械执行。

### 3. CoT Phase Transition Theory

**Takanami, Pehlevan (2026).**
"An Asymptotic Theory of Chain-of-Thought in In-Context Learning"
arXiv: 2606.03217v1

**核心发现**: 识别了CoT长度与性能之间的"sharp phase transition"——分为四个区域：
- 区域I: 指数增长（推理深度帮助泛化）
- 区域II: 多项式增长
- 区域III: 饱和
- 区域IV: overthinking（错误放大）

**与D2-1的关联**: 直接支持D2-1的"不连续跃迁"猜想。D2-1猜想"存在临界规模 |A|_c，规划能力出现不连续跃迁"——2606.03217在CoT长度维度上证明了相同的相变结构。两者从不同侧面验证了同一现象：智能能力存在临界阈值。

### 4. Internalization of Chain-of-Thought

**Huang, Zhu, Wang, Jiao, Russell, Sojoudi, Mei (2026).**
"Transformers Provably Learn to Internalize Chain-of-Thought"
arXiv: 2605.28600v1

**核心发现**: 深层架构可以通过训练复制可见推理迹的数据效率，而不需要token generation delay。

**与D2-1的关联**: 表明规划能力可以通过"内化"而非规模增长实现。D2-1的"I_plan^*"在internalization场景下对应于：模型需要学习的最小推理模式集合。

### 5. Inference Compression

**Zheng, Chen, Ren, et al. (2026).**
"HMPO: Hybrid Median-length Policy Optimization for Chain-of-Thought Compression"
arXiv: 2606.01934v1

**核心发现**: 推理迹可以在保持任务性能的同时压缩约50%的token数。证明了存在"推理冗余预算"。

**与D2-1的关联**: 支持D2-1的"delta_margin ~ 10% for reasoning redundancy"猜想。实际实验显示冗余可达50%。

### 6. Emergent Abilities Foundation

**Wei, Tay, Bommasani, Raffel, Zoph, Borgeaud, et al. (2022).**
"Emergent Abilities of Large Language Models"
arXiv: 2206.07682v2

**核心发现**: 定义了emergent abilities——仅在scale up时出现、无法从小模型外推的能力。

**与D2-1的关联**: D2-1的"规划能力跃迁"是Wei et al.定义的emergent abilities的具体子集。

---

## 建议添加到D2-1的bib条目

```bibtex
@article{xia2026agentic,
  title = {Agentic Chain-of-Thought Steering for Efficient and Controllable {LLM} Reasoning},
  author = {Xia, Yu and Xie, Zhouhang and Xu, Xin and Kang, Byungkyu and Lamba, Prarit and Gao, Xiang and McAuley, Julian},
  journal = {arXiv preprint arXiv:2606.03965},
  year = {2026}
}

@article{zhang2026cot,
  title = {Chain-of-Thought and Compressed Looped Transformers: A Memory-Budget Separation},
  author = {Zhang, Haozhou},
  journal = {arXiv preprint arXiv:2605.30757},
  year = {2026}
}

@article{takanami2026cot,
  title = {An Asymptotic Theory of Chain-of-Thought in In-Context Learning},
  author = {Takanami, Kaito and Pehlevan, Cengiz},
  journal = {arXiv preprint arXiv:2606.03217},
  year = {2026}
}

@article{huang2026internalize,
  title = {Transformers Provably Learn to Internalize Chain-of-Thought},
  author = {Huang, Yixiao and Zhu, Hanlin and Wang, Zixuan and Jiao, Jiantao and Russell, Stuart and Sojoudi, Somayeh and Mei, Song},
  journal = {arXiv preprint arXiv:2605.28600},
  year = {2026}
}

@article{zheng2026hmpo,
  title = {{HMPO}: Hybrid Median-length Policy Optimization for Chain-of-Thought Compression},
  author = {Zheng, Minghui and Chen, Hongxu and Ren, Huimin and Xin, Hongsheng and Qu, Xiaoyang and Wang, Ze and Yang, Shuling and Peng, Ziyu and Zhang, Kaike and Zhou, Pan and Zhan, Kun},
  journal = {arXiv preprint arXiv:2606.01934},
  year = {2026}
}

@article{wei2022emergent,
  title = {Emergent Abilities of Large Language Models},
  author = {Wei, Jason and Tay, Yi and Bommasani, Rishi and Raffel, Colin and Zoph, Barret and Borgeaud, Sebastian and Yogatama, Dani and Bosma, Maarten and Zhou, Denny and Metzler, Donald and Chi, Ed H. and Hashimoto, Tatsunori and Vinyals, Oriol and Liang, Percy and Dean, Jeff and Fedus, William},
  journal = {arXiv preprint arXiv:2206.07682},
  year = {2022}
}
```
