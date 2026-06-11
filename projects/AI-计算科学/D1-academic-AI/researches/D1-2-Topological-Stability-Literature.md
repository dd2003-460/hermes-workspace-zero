# D1-2: Topological Representation Stability — Literature Review Supplement

**生成时间**: 2026-06-08 (Iteration 23)
**对应原始paper**: raw/d1-topological-representation-stability.md
**补充目的**: 将已发现的TDA+generalization文献整理为bib条目

---

## 核心文献

### 1. TDA for Generalization (最接近D1-2)

**Dindin, Umeda, Chazal (2019).**
"Topological Data Analysis for Arrhythmia Detection through Modular Neural Networks"
arXiv: 1906.05795v1

**核心发现**: 使用TDA减少deep learning模型的bias，明确关注generalization。通过拓扑约束构建网络，使得拓扑结构有助于新患者数据的分类准确性。

**与D1-2的关联**: 直接研究了TDA与generalization的关系。D1-2的创新在于：不是用TDA减少bias，而是用TDA的拓扑特征（beta_1）作为OOD泛化的**预测指标**。两者都认可拓扑结构与generalization的关联，但角度不同。

### 2. TDA + Deep Learning Beyond Persistent Homology

**Su, Liu, Bou Hamdan, Maroulas, Wu, Carlsson, Wei (2025).**
"Topological Data Analysis and Topological Deep Learning Beyond Persistent Homology -- A Review"
arXiv: 2507.19504v1

**核心发现**: 综述了TDA在DL中的应用，指出persistent homology的局限性（高维抽象损失信息），并探索了spectral和sheaf-based的替代方法。

**与D1-2的关联**: 说明了D1-2使用beta_1（persistent homology的基础特征）作为OOD预测指标是合理的简化。同时，文献指出的局限也意味着D1-2可能需要探索更丰富的拓扑统计量（如persistence landscapes）。

### 3. TDA in Molecular Sciences

**Wee, Jiang (2025).**
"A Review of Topological Data Analysis and Topological Deep Learning in Molecular Sciences"
arXiv: 2509.16877v1

**核心发现**: TDA特征提取在分子 sciences中的应用，涵盖drug discovery和protein engineering。

**与D1-2的关联**: TDA作为特征提取的方法已在molecular sciences中被广泛验证——但D1-2的创新在于：不是用拓扑特征做特征提取，而是用它作为**表征质量的度量**。

### 4. PersGNN: TDA + GNN for Protein Function

**Swenson, Krishnapriyan, Buluc, Morozov, Yelick (2020).**
"PersGNN: Applying Topological Data Analysis and Geometric Deep Learning to Structure-Based Protein Function Prediction"
arXiv: 2010.16027v1

**核心发现**: 端到端可训练的GNN模型，集成TDA捕捉"局部和全局结构特征"。在protein function prediction中取得了显著提升。

**与D1-2的关联**: 证明了TDA可以作为训练中的有效信号——这与D1-2的"beta_1预测OOD泛化"一致：拓扑结构确实影响模型的行为。

### 5. Topological Deep Learning Review

**Zia, Khamis, Nichols, Hayder, Rolland, Petersson (2023).**
"Topological Deep Learning: A Review of an Emerging Paradigm"
arXiv: 2302.03836v1

**核心发现**: 拓扑方法提供"principled global descriptions of multi-dimensional data"，具有"stable properties such as robustness to deformation and noise"。

**与D1-2的关联**: D1-2的核心直觉是：拓扑复杂性高的表征（高beta_1 = 更多环/循环）更脆弱（OOD泛化差）。这与Zia et al.的"robustness to deformation"一致——拓扑结构决定了对扰动的敏感度。

---

## 与已有文献的关键区别

D1-2的原始声明声称"首次提出用拓扑复杂性作为表征质量的度量，而非特征"——这一声明的边界：

| 已有工作 | 使用TDA的方式 | D1-2的创新 |
|----------|--------------|------------|
| 1906.05795 | TDA减少generalization bias | beta_1 **预测**OOD泛化（不是减少bias） |
| 2010.16027 | TDA作为特征提取（PersGNN） | TDA作为表征**质量度量** |
| 2507.19504 | 综述TDA+DL（强调persistent homology局限） | 指出beta_1作为简单统计量的预测价值 |
| 2302.03836 | TDA提供global description | 将global description与generalization建立定量关系 |

**关键区别**: 已有工作用TDA增强模型性能；D1-2用TDA**诊断**模型表征质量。这是一个从"prescriptive"到"diagnostic"的范式转换。

---

## 建议添加到D1-2的bib条目

```bibtex
@article{dindin2019tda,
  title = {Topological Data Analysis for Arrhythmia Detection through Modular Neural Networks},
  author = {Dindin, Meryll and Umeda, Yuhei and Chazal, Frederic},
  journal = {arXiv preprint arXiv:1906.05795},
  year = {2019}
}

@article{su2025tda,
  title = {Topological Data Analysis and Topological Deep Learning Beyond Persistent Homology -- {A Review}},
  author = {Su, Zhe and Liu, Xiang and Bou Hamdan, Layal and Maroulas, Vasileios and Wu, Jie and Carlsson, Gunnar and Wei, Guo-Wei},
  journal = {arXiv preprint arXiv:2507.19504},
  year = {2025}
}

@article{wee2025tda,
  title = {A Review of Topological Data Analysis and Topological Deep Learning in Molecular Sciences},
  author = {Wee, JunJie and Jiang, Jian},
  journal = {arXiv preprint arXiv:2509.16877},
  year = {2025}
}

@article{swenson2020persgnn,
  title = {{PersGNN}: Applying Topological Data Analysis and Geometric Deep Learning to Structure-Based Protein Function Prediction},
  author = {Swenson, Nicolas and Krishnapriyan, Aditi S. and Buluc, Aydin and Morozov, Dmitriy and Yelick, Katherine},
  journal = {arXiv preprint arXiv:2010.16027},
  year = {2020}
}

@article{zia2023tda,
  title = {Topological Deep Learning: {A} Review of an Emerging Paradigm},
  author = {Zia, Ali and Khamis, Abdelwahed and Nichols, James and Hayder, Zeeshan and Rolland, Vivien and Petersson, Lars},
  journal = {arXiv preprint arXiv:2302.03836},
  year = {2023}
}
```
