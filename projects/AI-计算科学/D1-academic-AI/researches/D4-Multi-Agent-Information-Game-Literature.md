# D4: Multi-Agent Information Game — Literature Review Supplement

**生成时间**: 2026-06-08 (Iteration 23)
**对应原始paper**: raw/d4-multi-agent-information-game.md
**补充目的**: 将已发现的多Agent博弈+信息理论文献整理为bib条目

---

## 核心文献

### 1. Contextual Games: Multi-Agent Learning with Side Information

**Sessa, Bogunovic, Krause, Kamgarpour.**
"Contextual Games: Multi-Agent Learning with Side Information"

**核心发现**: 研究了带round-specific context的重复博弈。用kernel techniques连接环境模式和结果，提出meta-procedure降低personal regret。证明了regret下降时稳定性和社会效益的可达到性。

**与D4的关联**: 这是D4最相关的文献——研究多Agent博弈中的信息使用。D4的"信息博弈值"和"信息保留策略"概念，与Contextual Games中"side information"的概念类似，但D4将其扩展到零和竞争场景。

### 2. Finding Equilibrium in Multi-Agent Games with Payoff Uncertainty

**Guo, Curmei, Wang, Recht, Jordan.**
"Finding Equilibrium in Multi-Agent Games with Payoff Uncertainty"

**核心发现**: 在outcome values有bounded unknowns的情况下，将ex-post稳定性作为对碎片化数据的防御。单轮零和博弈中可以用linear programming定位stable positions。

**与D4的关联**: 零和博弈的均衡理论，与D4的"零和竞争中信息守恒"直接相关。D4的猜想是：在零和博弈中，信息守恒是一个额外的约束条件。

### 3. Ratio-Based Shapley Value for Collaborative ML

**Filter, Moller, Ozcep (2025).**
"A Ratio-Based Shapley Value for Collaborative Machine Learning"
arXiv: 2510.13261v1

**核心发现**: 提出ratio-based Shapley value替代标准的additive formulation，用relative contribution measure评估各参与方的数据贡献。

**与D4的关联**: D4声称"利用Shapley值分析信息贡献的博弈论性质"——2510.13261提供了方法论基础：Shapley值可以用于评估proportional information contributions。

### 4. Game-Theoretic Learning for Wireless Networks

**Wang, Wang, Chen, Yang, Kong, Liu, Jia, Xu.**
"A Game-Theoretic Learning Framework for Multi-Agent Intelligent Wireless Networks"

**核心发现**: 将AI与strategic modeling合并，研究distributed resource balancing和anti-interference tactics。

**与D4的关联**: 展示了博弈论在多Agent系统中的实际应用，支持D4的方法论。

### 5. DuMate-DeepResearch: Multi-Agent System

**Yan, Xu, Zhao, Li, Chen, Wu, Song, Li, Shi, Chen, Ma, Li, Zhao, Wang, Wu, Yin.**
"DuMate-DeepResearch: An Auditable Multi-Agent System with Recursive Search and Rubric-Grounded Reasoning"

**核心发现**: 多Agent系统的task orchestration和tool usage分离，使用graph-based dynamic planning。

**与D4的关联**: 展示了多Agent系统的协作模式，与D4关注的竞争模式形成对比。

---

## D4创新声明的边界分析

D4声称"首次将信息瓶颈应用于非合作博弈"——这一声明的边界：

| 已有工作 | 与信息的关系 | D4的独特之处 |
|----------|-------------|--------------|
| Contextual Games | side information用于降低regret | 信息是博弈的**输入**，不是策略本身 |
| Guo et al. | payoff uncertainty下的均衡 | 没有分析信息的博弈论性质 |
| 2510.13261 | Shapley值用于data contribution | 合作场景，非竞争 |
| D4 | 信息本身是策略变量 | 信息保留 p_i: O -> {0,1}^k |

**关键区别**: 已有工作将信息视为博弈的外生参数；D4将信息策略本身作为博弈的内生变量。

---

## 建议添加到D4的bib条目

```bibtex
@article{sessacontextual,
  title = {Contextual Games: Multi-Agent Learning with Side Information},
  author = {Sessa, Pier Giuseppe and Bogunovic, Ilija and Krause, Andreas and Kamgarpour, Maryam},
  journal = {arXiv preprint},
  year = {unknown}
}

@article{guoequilibrium,
  title = {Finding Equilibrium in Multi-Agent Games with Payoff Uncertainty},
  author = {Guo, Wenshuo and Curmei, Mihaela and Wang, Serena and Recht, Benjamin and Jordan, Michael I.},
  journal = {arXiv preprint},
  year = {unknown}
}

@article{filter2025shapley,
  title = {A Ratio-Based Shapley Value for Collaborative Machine Learning},
  author = {Filter, Bj{\"o}rn and M{\"o}ller, Ralf and {\"O}z{\c{c}}ep, \"{O}zg{\"u}r L{\"u}tf{\"u}},
  journal = {arXiv preprint arXiv:2510.13261},
  year = {2025}
}
```

---

## 待验证的声明

D4的"信息守恒定律" ($\sum I(p_i; O) = const$) 是一个具体的、可证伪的猜想。

**可能的验证路径**:
1. 在零和RL环境（如2-player poker, Atari竞争）中训练N个Agent
2. 测量每个Agent在均衡时保留的互信息 $I(p_i; O)$
3. 验证sum是否随N变化保持常数

**可能的反例**: 如果Agent之间有不对称的resource constraints，信息可能不守恒（某些Agent被迫保留更少信息）。
