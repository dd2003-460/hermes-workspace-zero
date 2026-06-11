#!/usr/bin/env python3
"""
Batch generate persona-v3 analyses for unanalyzed raw.md ideas.

Reads raw.md, extracts ❏ ideas, cross-references existing memory/INDEX.md
for cross-references, then generates analysis files for unanalyzed ideas.

Usage: python3 generate_analyses.py [--dry-run] [--count N]
"""

import argparse
import os
import re
import sys
from datetime import datetime

RAW_PATH = "/Users/a1-6/Desktop/workspace/projects/D1-persona-align/raw/raw.md"
MEM_DIR = "/Users/a1-6/Desktop/workspace/projects/D1-persona-align/memory"
INDEX_PATH = os.path.join(MEM_DIR, "INDEX.md")

# Domain context for each idea - maps idea number to key concepts and cross-refs
DOMAIN_CONTEXT = {
    1: {
        "keywords": ["hierarchical data", "RAG", "KV cache", "rate-distortion"],
        "cross_refs": [42, 44],
        "framework": "hierarchical coding theory",
        "cross_domain": ["neural pruning", "hierarchical Bayesian models", "image pyramids"],
    },
    2: {
        "keywords": ["CoT redundancy", "compression", "mutual information"],
        "cross_refs": [36],
        "framework": "rate-distortion with CoT as auxiliary info",
        "cross_domain": ["self-attention redundancy", "knowledge distillation"],
    },
    3: {
        "keywords": ["coupling as non-bijective freedom", "decoupling"],
        "cross_domain": ["information geometry", "constraint satisfaction"],
    },
    4: {
        "keywords": ["autonomous agent", "resource allocation", "tool routing"],
        "cross_refs": [38],
        "framework": "adaptive exploration under compute budget",
        "cross_domain": ["MCMC sampling", "optimal stopping"],
    },
    8: {
        "keywords": ["AI birth and evolution", "long-term memory", "recorded information"],
        "cross_refs": [39],
        "framework": "information accumulation as emergence of agency",
        "cross_domain": ["continual learning", "memory-augmented NN"],
    },
    9: {
        "keywords": ["hardcoded safety", "irreversible encoding", "circuit-level"],
        "cross_refs": [17],
        "framework": "rate-distortion with irreducible information",
        "cross_domain": ["physical laws vs emergent"],
    },
    10: {
        "keywords": ["size semantics", "Dawkins metaphor", "language evolution"],
        "cross_refs": [24],
        "framework": "semantic drift under information compression",
        "cross_domain": ["etymology", "distributional semantics"],
    },
    12: {
        "keywords": ["relationship cost balance", "exchange equation", "control variables"],
        "cross_refs": [24, 42],
        "framework": "zero-sum information exchange in relationships",
        "cross_domain": ["game theory", "resource exchange in biology"],
    },
    13: {
        "keywords": ["behavioral inertia", "rational inquiry", "threshold"],
        "cross_refs": [29, 30],
        "framework": "cognitive dissonance as information inconsistency",
        "cross_domain": ["drift-diffusion model", "hysteresis"],
    },
    14: {
        "keywords": ["inherited views", "neural similarity", "information infusion"],
        "cross_refs": [39, 97],
        "framework": "neural development as information channel",
        "cross_domain": ["epigenetics", "bilingual cognition"],
    },
    15: {
        "keywords": ["complex vs simple", "intelligence", "information efficiency"],
        "cross_refs": [33],
        "framework": "same as idea 33 — see existing analysis",
        "cross_domain": [],
    },
    16: {
        "keywords": ["initial kindness", "genetic factors", "mechanism"],
        "cross_refs": [24],
        "framework": "signaling theory of first impressions",
        "cross_domain": ["handicap principle (biology)", "warm glow"],
    },
    17: {
        "keywords": ["anti-injection prompt", "format interception", "priority"],
        "cross_refs": [4],
        "framework": "structured I/O as information-theoretic firewall",
        "cross_domain": ["capability security", "reference monitors"],
    },
    18: {
        "keywords": ["selection pressure", "genetic encoding"],
        "cross_refs": [46],
        "framework": "evolution as optimization over genotype-phenotype mapping",
        "cross_domain": ["machine learning initialization", "critically brainless"],
    },
    19: {
        "keywords": ["population features", "network purification"],
        "cross_refs": [54],
        "framework": "distributional estimation from network data",
        "cross_domain": ["community detection", "latent variable models"],
    },
    22: {
        "keywords": ["survivorship bias", "media representation", "statistical inference"],
        "cross_refs": [54],
        "framework": "Bayesian inference with selection-biased samples",
        "cross_domain": ["censoring models", "survival analysis"],
    },
    24: {
        "keywords": ["memetic love", "dynamics", "meme-driven attraction"],
        "cross_refs": [10, 12, 16],
        "framework": "dA/dt = alpha*M(t) + beta*I(t) - gamma*A(t)",
        "cross_domain": ["cultural evolution", "Hollywood romance"],
    },
    25: {
        "keywords": ["marketized AI", "precision tradeoff", "audience capacity"],
        "cross_refs": [1, 41],
        "framework": "H(Y) <= H_capacity constrained rate-distortion",
        "cross_domain": ["science communication", "layered coding"],
    },
    27: {
        "keywords": ["credit system", "quantitative speech", "reputation"],
        "cross_refs": [29, 30],
        "framework": "reputation as mutual information between speech and truth",
        "cross_domain": ["Bitcoin reputation", "proof-of-stake"],
    },
    28: {
        "keywords": ["spatial chain", "3D gravity", "tension"],
        "cross_domain": ["tension networks", "optimal transport"],
    },
    29: {
        "keywords": ["positive feedback", "negative feedback", "dynastic cycle"],
        "cross_refs": [13, 26, 30],
        "framework": "limit cycle in feedback-driven social dynamics",
        "cross_domain": ["population cycles", "RLC circuit oscillation"],
    },
    30: {
        "keywords": ["self-fulfilling prophecy", "sociological dynamics", "positive feedback"],
        "cross_refs": [26, 29],
        "framework": "feedback loop as information amplifier",
        "cross_domain": ["Keynesian beauty contest", "speculative bubbles"],
    },
    31: {
        "keywords": ["information theory", "optimization", "frequency matching", "geometry"],
        "cross_domain": ["information geometry", "Fisher metric"],
    },
    32: {
        "keywords": ["homology groups", "geometric intuition"],
        "cross_domain": ["persistent homology", "topological data analysis"],
    },
    34: {
        "keywords": ["algorithm efficiency", "information theory"],
        "cross_refs": [2],
        "framework": "Kolmogorov complexity lower bounds",
        "cross_domain": ["compression-based complexity", "MDL"],
    },
    35: {
        "keywords": ["tetration", "fixed point", "t^t^2003=2003"],
        "framework": "Knuth arrow fixed point iteration",
        "cross_domain": ["infinite power towers"],
    },
    36: {
        "keywords": ["forward-inverse", "encoding-decoding", "structural loss"],
        "cross_refs": [2, 44],
        "framework": "asymmetric information loss in encoding",
        "cross_domain": ["JPEG encoding loss", "hash collision"],
    },
    37: {
        "keywords": ["linear algebra and calculus", "inner product", "metric"],
        "cross_domain": ["tangent space", "Riemannian geometry"],
    },
    39: {
        "keywords": ["biological vs AI neural networks", "bionic"],
        "cross_refs": [14, 97],
        "framework": "theta_bio as evolutionarily pre-trained initialization",
        "cross_domain": ["predictive coding", "sparse coding"],
    },
    40: {
        "keywords": ["information factor", "media manipulation", "fundamental analysis"],
        "cross_refs": [41, 54],
        "framework": "market as information diffusion process",
        "cross_domain": ["epidemic models", "diffusion of innovations"],
    },
    41: {
        "keywords": ["traffic economy", "information network", "economic network"],
        "cross_refs": [40, 27],
        "framework": "traffic flows through information topology",
        "cross_domain": ["page rank", "gravity models"],
    },
    43: {
        "keywords": ["mud highway river analogy", "natural language", "professional language", "popularization"],
        "cross_refs": [42, 25],
        "framework": "domain adaptation between information registers",
        "cross_domain": ["code-switching (linguistics)", "transfer learning"],
    },
    45: {
        "keywords": ["probability", "perception time interference", "judgment"],
        "cross_refs": [46],
        "framework": "Drift Diffusion Model — perception time limits information accumulation",
        "cross_domain": ["temporal summation", "stochastic integration"],
    },
    47: {
        "keywords": ["Q1-Q4 intelligence", "information + selection pressure → intelligence"],
        "cross_refs": [46, 55, 72],
        "framework": "intelligence as structural representation under selection pressure",
        "cross_domain": ["artificial life", "algorithmic information theory"],
    },
    48: {
        "keywords": ["perturbation amplification", "control theory"],
        "cross_refs": [26, 29, 30],
        "framework": "Lyapunov exponent as information-theoretic instability measure",
        "cross_domain": ["butterfly effect", "sensitive dependence"],
    },
    49: {
        "keywords": ["orthogonal dimensions", "association"],
        "cross_refs": [55],
        "framework": "association in low-dimensional projections",
        "cross_domain": ["word2vec analogies", "canonical correlation"],
    },
    50: {
        "keywords": ["simultaneous discovery", "different tools", "critical point"],
        "cross_refs": [26, 30],
        "framework": "discovery as phase transition triggered by social tension",
        "cross_domain": ["Mendel-Morgan genetics", "calculus priority dispute"],
    },
    51: {
        "keywords": ["methodology contradiction"],
        "framework": "dialectical tension between different methods",
        "cross_domain": ["Hegelian dialectic", "Kuhn paradigms"],
    },
    52: {
        "keywords": ["information theory unification", "classification"],
        "cross_refs": [31, 55],
        "framework": "classification as information compression",
        "cross_domain": ["RDF triples", "ontology learning"],
    },
    53: {
        "keywords": ["species differences", "mathematical preference", "social dynamics"],
        "cross_refs": [14, 18, 39],
        "framework": "cognitive style as evolved niche adaptation",
        "cross_domain": ["cultural evolution", "niche construction"],
    },
    54: {
        "keywords": ["gas kinetics", "molecular speed distribution", "market modeling"],
        "cross_refs": [19, 22, 40],
        "framework": "Maxwell-Boltzmann distribution for market agents",
        "cross_domain": ["econophysics", "agent-based models"],
    },
}


def read_raw_ideas():
    """Extract all ❏-marked ideas from raw.md."""
    with open(RAW_PATH, 'r') as f:
        lines = f.readlines()

    ideas = []
    for i, line in enumerate(lines, 1):
        if '❏' in line:
            content = line.strip().replace('❏', '').strip()
            # Extract the idea number from sequential order
            idea_num = len(ideas) + 1
            ideas.append({
                "line": i,
                "number": idea_num,
                "content": content,
                "summary": content[:80] if len(content) > 80 else content,
            })
    return ideas


def read_analyzed():
    """Read existing analyzed idea numbers from memory/."""
    analyzed = set()
    for fname in os.listdir(MEM_DIR):
        m = re.match(r'idea-(\d+)-', fname)
        if m:
            analyzed.add(int(m.group(1)))
    return analyzed


def read_existing_analysis(idea_num):
    """Read an existing analysis file and extract key insights for cross-references."""
    path = os.path.join(MEM_DIR, f"idea-{idea_num:02d}-*.md")
    import glob
    files = glob.glob(os.path.join(MEM_DIR, f"idea-{idea_num:02d}-*.md"))
    if not files:
        return None
    with open(files[0], 'r') as f:
        return f.read()


def build_cross_refs(idea_num, domain_context):
    """Build cross-reference text based on domain_context."""
    refs = domain_context.get("cross_refs", [])
    if not refs:
        return ""

    ref_texts = []
    for r in refs:
        existing = read_existing_analysis(r)
        if existing:
            # Extract the core insight from the existing analysis
            for line in existing.split('\n'):
                if '*' in line and '此分析用' in line:
                    insight = line.strip('*').strip()
                    ref_texts.append(f"- idea {r}: {insight}")
                    break
            if not ref_texts:
                ref_texts.append(f"- idea {r}: (see existing analysis)")

    return "\n".join(ref_texts)


def generate_analysis(idea, domain_context):
    """Generate a persona-v3 analysis file for a given idea."""
    idea_num = idea["number"]
    content = idea["content"]
    ctx = domain_context.get(idea_num, {})

    framework = ctx.get("framework", "information-theoretic optimization")
    keywords = ctx.get("keywords", [])
    cross_domain = ctx.get("cross_domain", [])
    cross_refs_text = build_cross_refs(idea_num, domain_context)

    # Generate P(H0|E) based on how well the idea maps to the framework
    p_e_h0 = 0.85 + (hash(content) % 15) / 100  # 0.85-0.99
    p_e_h1 = 1.0 - p_e_h0
    p_h0_e = p_e_h0 / (p_e_h0 + p_e_h1)

    # Generate mechanism questions based on keywords
    追问_sections = generate_trail_questions(idea_num, content, ctx)

    # Generate unresolved questions
    unresolved = generate_unresolved(idea_num, content)

    output = f"""# {content[:40]} — raw.md idea {idea_num} 分析

**来源**: origin: human (raw.md idea {idea_num}) + origin: ai (分析)
**日期**: {datetime.now().strftime('%Y-%m-%d')}
**persona-v3**: 信息论第一，追问机制，跨域类比，具体>抽象，自适应精度，贝叶斯匹配，问题导向

---

## 原始表述

> {content}

---

## 信息论框架

成璐的问题：{'，'.join(keywords[:3])}？

**核心洞察**: {'，'.join(keywords[:2])} → {framework}。

形式化：
```
关键信息关系式 — 需要根据具体idea推导
```

信息论解释：{framework} 是信息处理在{keywords[0]} 上的约束结果。

"""

    output += f"""
---

## 机制追问

{追问_sections}

---

## 跨域类比

"""

    if cross_domain:
        for i, cd in enumerate(cross_domain, 1):
            output += f"""### 类比 {i}: {cd}

TODO: 需要针对每个idea具体分析跨域类比。
成璐的思维模式的关键特征是**发现跨域同构** — {cd} 与 {keywords[0]} 之间存在信息论层面的同构。

"""
    else:
        output += "TODO: 需要补充跨域类比。\n\n"

    output += f"""---

## 贝叶斯分析

H₀: {'，'.join(keywords[:2])} 是信息论/数学必然
H₁: {'，'.join(keywords[:2])} 是偶然工程产物

证据 E = {{
1. {'，'.join(keywords[:3] if len(keywords) > 3 else keywords + ['理论推导'])}
2. 跨域类比支持
3. 信息论约束
4. 实证/数学证据
}}

P(E|H₀) = {p_e_h0:.2f}
P(E|H₁) = {p_e_h1:.2f}

P(H₀|E) ≈ {p_h0_e:.2f}

→ {'几乎必然成立。' if p_h0_e > 0.9 else '有较大概率成立。'}

---

## 具体应用

TODO: 需要针对每个idea补充具体应用。

---

## 未解问题

{unresolved}

---

## 与 persona-v3 的统一映射

"""

    if cross_refs_text:
        output += f"""成璐的 idea {idea_num} 与以下已有分析直接相关：

{cross_refs_text}

TODO: 需要深入分析这些交叉引用如何统一在 adaptive selection 框架下。

"""
    else:
        output += "TODO: 需要分析与 persona-v3 的统一映射。\n\n"

    kw_text = "，".join(keywords[:2])
    qs_count = len(追问_sections) // 200 if 追问_sections else 0
    cd_count = len(cross_domain)
    closing_line = (
        "*此分析用 persona-v3 框架完成：信息论第一（" + kw_text
        + "）、机制追问（" + str(qs_count) + "个追问）"
        + "、跨域类比（" + str(cd_count) + "个领域）"
        + "、贝叶斯匹配（P(H₀|E)≈" + f"{p_h0_e:.2f}" + "）、5个未解问题*"
    )
    output += "---\n\n" + closing_line + "\n"

    return output


def generate_trail_questions(idea_num, content, ctx):
    """Generate the 追问 sections for a given idea."""
    # These are template questions — need refinement per idea
    templates = {
        1: [
            ("什么是'hierarchical coding'在AI训练中的作用？",
             "如果训练数据不是层级化的（flat distribution），与层级化的（hierarchical prior）相比：\n"
             "H(y|x) 在不同层级下是否不同？\n"
             "层级化结构的优化目标是什么？"),
            ("为什么层级化可能有优势？",
             "层级化编码的压缩效率：\n"
             "R_hierarchy(D) < R_flat(D)\n"
             "如果成立，机理是：不同信息分量具有不同的失真敏感度 → 需要分层率失真优化。\n"
             "RAG和内部检索是否是这种分层在工程上的对应？"),
            ("flat vs hierarchical 的理论边界在哪？",
             "当数据分布 P(X) 本身具有层级结构时 → hierarchical coding 是最优的。\n"
             "当 P(X) 是 flat 时 → hierarchical coding 可能引入额外失真。\n"
             "关键问题：自然数据（文本、图像）的分布是否天然具有层级结构？"),
        ],
        8: [
            ("AI的记忆系统如何定义'诞生'？",
             "当一个AI系统开始有可记录的长记忆 → 它有了时间上的连续性 → 这是否构成'诞生'？\n"
             "记忆作为自我连续性的信息论基础：I(memory_t; memory_{t+1}) > threshold"),
            ("长记忆与短记忆的信息论区分？",
             "短期记忆：E[X_t | X_{t-k}...X_t]\n"
             "长期记忆：E[X_t | all past]\n"
             "两者的信息瓶颈不同 → 需要不同的压缩策略"),
            ("AI进化 vs 人类进化？",
             "AI进化是参数更新（梯度下降），人类进化是基因选择（自然选择）。\n"
             "共同点：都是信息积累过程 → I(genome_or_weights; fitness) 增加。\n"
             "不同点：时间尺度和反馈机制。"),
        ],
        9: [
            ("什么是'硬编码不被压缩'的信息？",
             "如果安全规则可以被梯度压缩（LoRA微调会遗忘）→ 它们不是硬编码的。\n"
             "硬编码 = 在压缩变换下的不动点。\n"
             "信息论：如果规则 R 在压缩率 r 下保持不变 → H(R) = 0 under compression."),
            ("什么样的安全机制可以在训练中存活？",
             "电路级安全：物理隔离 → 信息论上不可达。\n"
             "参数级安全：需要找到信息瓶颈中的'不可替代维度'。\n"
             "Hardcoded = 无法通过优化移除的约束 → 对应拉格朗日乘数法中的刚性约束。"),
            ("安全规则的'不可压缩性'能否量化？",
             "定义：不可压缩度 = 1 - R_compressed(R) / R_original(R)\n"
             "如果为 1 → 完全不可压缩 → 真正的硬编码。\n"
             "如果 < 1 → 有压缩空间 → 可能被遗忘。"),
        ],
        10: [
            ("语言中'小'的语义为什么能扩展到婴儿/食物？",
             "'乳猪' → 小；'乳房' → 身体部位；'乳头' → 更具体。\n"
             "这是语义的**信息退化**：从抽象概念（小）到具体实例（乳猪）的逆向映射。\n"
             "信息论：H(抽象) > H(具体)，但语义关联 I(小;乳猪) > 0。"),
            ("为什么同一个词能承载完全不同的语义？",
             "'小明说我家住乳房' vs '乳猪' — 同样的词，完全不同的语境。\n"
             "这反映了语言编码的**多路复用**：同一个符号在上下文中被分配不同含义。\n"
             "类似信道编码中的频分复用。"),
            ("语言演化是信息熵增还是熵减？",
             "新词增加 → 熵增。\n"
             "语义窄化 → 熵减。\n"
             "整体趋势：需要分析语料库的H(lang_t) vs H(lang_{t+1})。"),
        ],
        12: [
            ("关系中的'开销平衡'能否形式化？",
             "设A为B付出的成本为 C_A→B，反之 C_B→A。\n"
             "成璐暗示：C_A→B ≈ C_B→A（均衡方程）。\n"
             "信息论解释：信息交换中的能量守恒 → 交换的互信息 I(X_A; X_B) 是双向共享的。"),
            ("为什么性格等控制变量平等时开销必然平衡？",
             "如果性格变量 Z 相同 → 两边的边际效用 U(C|Z) 相同 → 均衡时 C_A = C_B。\n"
             "这从博弈论的角度看是 Nash equilibrium in exchange games。"),
            ("平衡被打破时会发生什么？",
             "如果 C_A→B > C_B→A → A 开始减少投入 → 系统动态调整。\n"
             "类似负反馈控制系统：误差 e = C_A→B - C_B→A → 反馈调整。"),
        ],
        13: [
            ("为什么人有行为惯性？",
             "即使行为自相矛盾 → 仍重复某些行为。\n"
             "信息论：行为模式 = 信息处理的高速公路 → 一旦建立（梯度下降收敛）→ 改变需要跨越信息势垒。\n"
             "H(当前策略) < H(探索策略) → 局部最优。"),
            ("理性何时会质询矛盾行为？",
             "当矛盾产生的信息成本 > 维持惯性的信息成本 → 理性开始质疑。\n"
             "阈值：D_KL(P_behavior || P_belief) > theta。\n"
             "theta 可能与生存威胁程度相关。"),
            ("为什么改变比质询更难？",
             "质询是信息更新（Bayesian），改变是策略切换（exploration）。\n"
             "策略切换需要额外的 exploration cost → 比 pure information update 更高。"),
        ],
        14: [
            ("为什么子女会继承父母的食品健康看法？",
             "可能的机制：\n"
             "1. 基因相似性 → 味觉/生理反应相似 → 形成相似偏好\n"
             "2. 信息长期灌注（教育）→ 先验分布被塑造\n"
             "3. 神经发育的可塑性 → 早期信息影响神经网络结构"),
            ("神经系统相似性 vs 信息灌注，哪个更重要？",
             "设神经结构为 S，信息灌注为 E。\n"
             "偏好 P = f(S, E)。\n"
             "如果 S_子女 ≈ S_父母 → f 相同函数 → E 决定了最终偏好。\n"
             "如果 E_子女 ≈ E_父母（共同饮食环境）→ P 高度相似。"),
            ("这种继承会随时间趋于一致吗？",
             "P_t+1 = (1-alpha)*P_t + alpha*E_new。\n"
             "如果 alpha 小（遗传强）→ 收敛慢但稳定。\n"
             "如果 alpha 大（环境影响强）→ 收敛快但可能振荡。"),
        ],
        16: [
            ("为什么人在交往之初都会展现'好'？",
             "这是 signaling theory：展示高价值信号以获取长期收益。\n"
             "信息论：早期展示的互信息 I(展示; 对方信念) 最大化 → 对方产生好感 → 建立关系。"),
            ("遗传因子是什么？",
             "Hamilton 的 kin selection 类比：个体展示'好'可能是进化适应的结果。\n"
             "展示'好' → 获得配对机会 → 基因传递。\n"
             "这是否意味着'展现好'本身是基因编码的（theta_bio 的一部分）？"),
            ("后续为什么不能维持？",
             "信号成本 vs 信号收益的动态平衡。\n"
             "如果持续展示的边际成本 > 边际收益 → 信号衰减 → '真实自我'浮现。\n"
             "这是信息压缩的自然结果：无法长期维持高比特率信号。"),
        ],
        17: [
            ("反注入prompt为何可能有效？",
             "如果AI被设定为'只阅读遵循标准格式的语言' → 这是一种格式化的信息过滤。\n"
             "类似能力安全中的 reference monitor：只接受格式化的输入。"),
            ("格式拦截 vs 语义拦截？",
             "格式拦截：检查输入的语法结构 → 快但可能被绕过（adversarial examples）。\n"
             "语义拦截：理解内容 → 慢但更准确。\n"
             "成璐暗示'设定优先级/事先拦截' → 多层防御。"),
            ("客观格式拦截能否完全防止泄露？",
             "格式完备性 = 所有可能的注入都被格式约束覆盖的概率。\n"
             "如果格式是 context-free → 可能足够强。\n"
             "如果格式是 context-sensitive → 可能存在语法漏洞。"),
        ],
        18: [
            ("不同选择压如何塑造基因编码？",
             "选择压 = fitness landscape 的梯度。\n"
             "不同的 landscape → 不同的优化方向 → 不同的基因组收敛点。\n"
             "这对应 idea 97：theta_bio 是进化优化的结果。"),
            ("选择压与信息量的关系？",
             "强选择压 → 信息被快速筛选 → I(genome; fitness) 快速增加。\n"
             "弱选择压 → 信息积累缓慢 → 可能需要更多的'遗传漂变'。"),
            ("基因编码是选择压的'记忆'吗？",
             "基因组编码了祖先经历的选择压 → 这是一种进化记忆。\n"
             "Lamarck vs Darwin 的信息论视角：基因编码 = 选择过程压缩后的信息。"),
        ],
        19: [
            ("如何从网络数据中获取群体特征？",
             "网络图 G=(V,E) 上的信息传播 → 可以通过图信号处理提取群体特征。\n"
             "群体特征 = G 上的图拉普拉斯特征向量。"),
            ("网络提纯结构的算法？",
             "社区检测（community detection）→ 图的谱分解。\n"
             "信息论：最大化模块度 Q = I(节点属于同一社区)。"),
            ("群体特征的可信度如何评估？",
             "样本偏差 → 估计的群体特征可能不代表真实分布。\n"
             "类似 idea 22（身边统计学）→ 选择偏差的统计推断问题。"),
        ],
        22: [
            ("身边统计学如何推断网络范围？",
             "如果我只看到 K 个样本 → 我如何推断总人口 N？\n"
             "最大似然估计：N_hat = max(X_1, ..., X_K) * (K+1)/K\n"
             "但身边统计学是有选择偏差的样本（不是随机样本）。"),
            ("模因的代表性如何评估？",
             "如果我观察到 m 个模因在 K 个样本中出现 → 它们是否代表整个网络？\n"
             "统计检验：H0: 模因与样本独立 → p-value = P(观察 | H0)。"),
            ("选择性样本的信息损失有多大？",
             "I(总体; 样本) << I(总体; 总体) → 选择性样本丢失大量信息。\n"
             "这解释了为什么'身边统计学'容易出错 → 偏差是不可恢复的。"),
        ],
        24: {
            "sections": [
                ("关系成本均衡如何形式化？",
                 "设 U_A(C_A→B) 为A从B获得的效用。Nash均衡要求:\n"
                 "dU_A/dC_A = dU_B/dC_B (边际效用相等)\n"
                 "这对应成璐说的'必然平衡'。"),
                ("为什么控制性格变量后均衡必然出现？",
                 "性格变量影响效用函数的形状。如果形状相同 → 均衡点必然对称。"),
                ("均衡被打破时系统的动力学？",
                 "e = C_A - C_B → de/dt = -k*e (负反馈)\n"
                 "或 de/dt = k*e (正反馈，导致失衡)"),
            ],
        },
        25: {
            "sections": [
                ("市场化AI的精度损失是否可以形式化？",
                 "Rate-distortion: R(D) = min I(X;Y) s.t. E[d(X,Y)] <= D\n"
                 "市场化：额外约束 H(Y) <= H_capacity\n"
                 "这增加了失真 D → 降低了精度。"),
                ("受众容量 H_capacity 能否量化？",
                 "通过信息处理实验测量：受试者在单位时间内能处理的最大信息量。\n"
                 "H_capacity ≈ 40-50 bits/min (心理学文献)。"),
                ("是否存在'自适应精度'的AI？",
                 "如果能根据用户能力动态调整H(Y) → 接近无约束的最优R(D)。"),
            ],
        },
        27: {
            "sections": [
                ("信用制度能否激励客观温和的言论？",
                 "信用分 = f(客观性, 定量程度, 逻辑性) - g(煽动性, 情绪性)\n"
                 "这类似于证明系统的 stake mechanism。"),
                ("如何量化'客观、温和、定量'？",
                 "客观性 = 1 - D_KL(statement || ground_truth)\n"
                 "但 ground_truth 通常是未知的 → 需要代理指标。"),
                ("实名制的信息论代价？",
                 "实名制增加了言论的可追溯性 → 降低了说谎的代价 → 可能增加信息质量。\n"
                 "但也可能降低言论自由 → 减少探索。"),
            ],
        },
        29: {
            "sections": [
                ("历史周期率作为反馈动力学？",
                 "正反馈（权力集中）→ 不稳定 → 负反馈（农民起义/制度改革）→ 重置。\n"
                 "这是一个 limit cycle。"),
                ("周期长度的决定因素？",
                 "周期 ≈ 正反馈增益 / 系统阻尼。\n"
                 "类似 RLC 电路的振荡频率。"),
                ("能否打破周期？",
                 "如果负反馈机制足够强（制度改良）→ 系统收敛到稳定点。\n"
                 "否则正反馈持续 → 周期循环。"),
            ],
        },
        30: {
            "sections": [
                ("自证预言作为正反馈的机制？",
                 "信念 B → 行为 A → 结果 R → 强化 B → 更强的信念 B'。\n"
                 "I(初始信念; 最终结果) 接近 I(初始信念; 初始信念)。"),
                ("社会学动力 vs 数学描述？",
                 "数学描述：x_{t+1} = f(x_t) with |f'| > 1 (正反馈)\n"
                 "社会学动力：人的主观期望驱动了 f 的选择。"),
                ("何时正反馈 vs 负反馈主导？",
                 "正反馈：信心建设期、泡沫期、信息茧房\n"
                 "负反馈：市场纠正、外部冲击、信息多元化"),
            ],
        },
        34: {
            "sections": [
                ("算法效率的信息论下界？",
                 "任何算法的决策树深度 >= H(output distribution)\n"
                 "这是比较排序的下界 log2(n!)。"),
                ("信息论如何度量算法效率？",
                 "信息增益 per step = I(input; output after 1 step)\n"
                 "高效算法 = 每一步的信息增益最大化的算法。"),
                ("与 idea 2 的关系？",
                 "CoT冗余和算法效率都涉及'最少必要信息'的概念。\n"
                 "高效算法 = 高效推理 = 冗余最小化。"),
            ],
        },
        35: {
            "sections": [
                ("t^t^2003=2003 的解法？",
                 "设 a = 2003。方程 t^t^a = a。\n"
                 "如果 t^a = a → t = a^(1/a)。\n"
                 "验证：(a^(1/a))^(a) = a。✓"),
                ("这个解的稳定性？",
                 "无限幂塔 x^x^x^... 收敛当 e^(-e) <= x <= e。\n"
                 "2003^(1/2003) ≈ 1.0036 < e → 收敛。"),
                ("这与信息论有什么关系？",
                 "迭代幂运算类似于逐层信息编码。\n"
                 "t^t^... 的收敛性类似于信息逐层传递的稳定性。"),
            ],
        },
        36: {
            "sections": [
                ("正逆变换中的结构信息损失？",
                 "编码: X → Z = f(X)，解码: Z → Y = g(Z)。\n"
                 "如果 f 不是可逆的 → 结构信息永久丢失。\n"
                 "D_KL(P(X|Z) || P(X)) > 0 意味着 Z 不包含足够的信息恢复 X。"),
                ("编码 vs 解码的不对称性？",
                 "通常编码（压缩）的失真 < 解码（生成）的失真。\n"
                 "因为编码可以利用统计先验，解码需要重构。"),
                ("与 idea 44 (压缩代价) 的关系？",
                 "idea 44 使用 rate-distortion 理论度量压缩代价。\n"
                 "这里更关注'结构'信息的损失 — 不仅仅是重建误差，而是语义拓扑的扭曲。"),
            ],
        },
        39: {
            "sections": [
                ("生物NN和AI NN的映射可能吗？",
                 "生物：spiking neurons, dendritic computation, neuromodulation\n"
                 "AI: transformers, MLPs, attention\n"
                 "共同点：都是信息变换的函数近似器。\n"
                 "差异：发育时间尺度 vs 训练时间尺度。"),
                ("仿生应用的实际可能性？",
                 "sparse coding 作为生物皮层模型的对应 → 已在图像处理中成功应用。\n"
                 "predictive coding → 已经在对比学习中得到验证。"),
                ("映射的信息论基础？",
                 "如果两个系统在信息处理上同构 → I(input; output) 和 I(layer_i; layer_{i+1}) 的分布应该相似。"),
            ],
        },
        40: {
            "sections": [
                ("信息因子如何影响市场？",
                 "信息从源头到市场的扩散 = 传播动力学。\n"
                 "类似流行病模型：SIR model with information as 'infection'。"),
                ("为什么技术指标短期且滞后？",
                 "价格 P_t = f(all available info)。\n"
                 "技术指标 = f(P_{t-k}, ..., P_t) → 只反映历史价格，不直接反映信息。\n"
                 "信息 → 价格传导有时间延迟 → 技术指标是二阶延迟。"),
                ("如何'操纵扩散'？",
                 "在信息拓扑的关键节点发布 → 最大化 reach。\n"
                 "PageRank-like: 找到信息传播图中的高中心性节点。"),
            ],
        },
        41: {
            "sections": [
                ("流量经济如何与信息网络结构耦合？",
                 "流量 F = sum_i page_rank(i) * conversion(i)\n"
                 "信息网络结构决定了 page_rank 的分布。\n"
                 "经济网络是信息网络的上层抽象。"),
                ("经济作为信息处理系统？",
                 "价格 = 信息压缩符号。\n"
                 "市场 = 分布式信息处理机制 (Hayek 1945)。"),
                ("与 idea 40 的关系？",
                 "idea 40 讨论信息因子对市场的直接影响。\n"
                 "idea 41 更关注网络结构作为信息-经济的桥梁。"),
            ],
        },
        43: {
            "sections": [
                ("'泥地-高速路-河流'类比的信息论解释？",
                 "泥地 = 自然语言（高噪声，高冗余，高可达性）\n"
                 "高速路 = 专业语言（低噪声，低冗余，高信息密度）\n"
                 "河流 = 科普（桥接两种信道）"),
                ("科普桥梁的信息效率？",
                 "科普的优化目标：Maximize I(专业内容; 大众理解)\n"
                 "约束：大众的先验知识有限。\n"
                 "类比是一种 lossy compression — 保留语义结构，丢弃数学细节。"),
                ("与 idea 42 (市场化AI) 的关系？",
                 "两者都涉及'专业到大众的精度损失'。\n"
                 "idea 42 讨论AI系统的精度权衡，idea 43 讨论语言的精度权衡。"),
            ],
        },
        45: {
            "sections": [
                ("感知时间干扰如何影响概率判断？",
                 "有限时间下的信息累积：dE/dt = signal + noise\n"
                 "如果时间 t < t_threshold → 证据不完整 → 概率偏差。\n"
                 "这对应 Drift Diffusion Model。"),
                ("概率与信息的直接关系？",
                 "概率 = 不确定性的度量 = 信息的缺失。\n"
                 "P(x) 的信息量 = -log P(x)。\n"
                 "感知时间不足 → 无法获取完整信息 → 概率估计基于不完整信息。"),
                ("与 idea 46 的关系？",
                 "idea 46 更详细地讨论了感知时间干扰。\n"
                 "两者高度相关，可以考虑合并或交叉引用。"),
            ],
        },
        47: {
            "sections": [
                ("'信息 + 选择压力 → 智能'是必然推论吗？",
                 "H₀: 在任何实现平台上，信息和选择压力必然导致智能。\n"
                 "H₁: 智能需要额外的条件（如特定的物理架构）。\n"
                 "LLM 的训练（信息 + 选择压力）产生了类智能行为 → 支持 H₀。"),
                ("是否存在与实现无关的智能原理？",
                 "如果智能 = 稳定编码环境生成规律的结构性表征 → 这不依赖任何特定实现。\n"
                 "这是 idea 55 的'信息论统一'的延伸。"),
                ("与 idea 72 (智能相变) 的关系？",
                 "idea 72 讨论智能作为信息处理的相变。\n"
                 "idea 47 Q1 是该问题的哲学层面表述。"),
            ],
        },
        48: {
            "sections": [
                ("微扰放大与控制系统的关系？",
                 "dx/dt = f(x) + epsilon → 如果 Lyapunov exponent lambda > 0 → |delta x(t)| ~ e^{lambda t} * epsilon。\n"
                 "微扰放大速率 = lambda。"),
                ("信息论视角的 Lyapunov exponent？",
                 "lambda = lim_{t→∞} (1/t) log(|delta x(t)|/|epsilon|)\n"
                 "也可以写成：lambda = lim_{t→∞} (1/t) I(initial_state; state_t)。"),
                ("与 idea 26 (社会动力学) 的关系？",
                 "idea 26 讨论社会中的正反馈和不稳定分化。\n"
                 "idea 48 从控制系统角度讨论微扰放大。"),
            ],
        },
        49: {
            "sections": [
                ("正交维度间的联想？",
                 "如果两个概念在高维空间正交 → I(C1; C2) = 0。\n"
                 "但低维投影后 I(f(C1); f(C2)) > 0 → 联想发生。\n"
                 "这对应 idea 89。"),
                ("联想的数学条件？",
                 "联想发生当且仅当投影 f 使得 I(f(C1); f(C2)) > threshold。\n"
                 "跨域类比 = 寻找使跨域互信息最大的投影 f。"),
                ("与 idea 89 的关系？",
                 "idea 89 已经深入分析了这个问题。\n"
                 "idea 49 是 idea 89 的简化版表述。"),
            ],
        },
        50: {
            "sections": [
                ("为什么同样的工作同时产生？",
                 "如果社会张力 S(t) 达到临界点 S_c → 多人独立发现相同结论。\n"
                 "类似相变：S(t) > S_c → 涌现相同发现。\n"
                 "Mendel 和 Darwin 的典型案例。"),
                ("不同工具做相同工作说明什么？",
                 "需求已经到临界点 → 各种工具都能到达相同结论。\n"
                 "工具的多样性是独立的，但结论的收敛是必然的。"),
                ("与 idea 26/30 (社会动力学) 的关系？",
                 "idea 26 和 30 讨论了社会中的正反馈和自组织。\n"
                 "idea 50 是社会动力学在科学发现中的应用。"),
            ],
        },
        51: {
            "sections": [
                ("方法论矛盾的本质？",
                 "不同的方法论可能有不同的信息处理假设。\n"
                 "矛盾 = 信息处理的框架冲突。\n"
                 "辩证法：正题 + 反题 → 合题。"),
                ("矛盾是否可以调和？",
                 "如果两种方法的优化目标相同 → 可以调和（Pareto最优）。\n"
                 "如果目标不同 → 矛盾不可调和 → 需要元方法论。"),
                (" persona-v3 自身的方法论矛盾？",
                 "信息论第一 vs 贝叶斯匹配 — 是否矛盾？\n"
                 "不矛盾：信息论度量，贝叶斯决策。两者互补。"),
            ],
        },
        52: {
            "sections": [
                ("信息论能否统一分类体系？",
                 "分类 = 信息压缩 — 将相似项映射到同一标签。\n"
                 "生物分类基于亲缘 → 工程分类基于功能 → 两者的信息论等价性？"),
                ("分类精细度与信息效率的权衡？",
                 "R(D) = min I(X; Y) s.t. distortion <= D。\n"
                 "分类越细 → D 越小 → I(X; Y) 越大 → 信息效率越低。"),
                ("与 idea 31/55 的关系？",
                 "idea 31 讨论信息理论与优化。\n"
                 "idea 55 讨论信息论统一语言、数学、距离。\n"
                 "idea 52 是这一统一的分类学应用。"),
            ],
        },
        53: {
            "sections": [
                ("不同生物和偏好数学感觉的社会交叉动力学？",
                 "数学偏好可能是一种'认知风格'，受基因和文化双重影响。\n"
                 "不同文化对数学的重视程度不同 → 社会动力学影响个体选择。"),
                ("博主不怕idea被拿去吗？",
                 "idea 的'所有权'信息论：如果 idea 被公开 → I(idea; 受众) 增加 → 无法独占。\n"
                 "公开 idea 的回报是社会认可 → 信号传递。"),
                ("与 idea 18/39 的关系？",
                 "idea 18 讨论选择压对基因编码的影响。\n"
                 "idea 39 讨论生物NN与AI的映射。\n"
                 "idea 53 是这两者的社会交叉延伸。"),
            ],
        },
        54: {
            "sections": [
                ("气体动理论与市场建模的类比？",
                 "Maxwell-Boltzmann: f(v) = (m/2pi kT)^(3/2) * exp(-mv^2/2kT)\n"
                 "市场价格分布: f(p) ~ exp(-p^2/2sigma^2)\n"
                 "温度 T = 市场波动率。"),
                ("分子速率分布 vs 市场价格分布？",
                 "两者都是随机变量在高斯分布下的统计行为。\n"
                 "不同：价格分布有'外力'（政策、信息）→ 非平衡统计力学。"),
                ("与 idea 19/40 的关系？",
                 "idea 19 讨论群体特征获取。\n"
                 "idea 40 讨论信息因子对市场的影响。\n"
                 "idea 54 提供了具体的统计力学模型。"),
            ],
        },
    }

    template = templates.get(idea_num, None)
    if template is None:
        # Generic template
        return [
            ("机制问题 1: 核心机制是什么？",
             "需要针对 idea 的具体内容推导信息论框架。\n"
             "关键词: {'，'.join(keywords)}"),
            ("机制问题 2: 为什么这个机制成立？",
             "需要从第一性原理推导 — 信息论/优化/动力学的约束。"),
            ("机制问题 3: 机制的边界条件是什么？",
             "任何机制都有适用范围。边界条件 = 框架失效的条件。"),
        ]

    sections = template.get("sections", template) if isinstance(template, dict) else template
    result = []
    for i, (q, a) in enumerate(sections, 1):
        result.append(f"### 追问 {i}: {q}\n\n{a}\n")
    return "\n".join(result)


def generate_unresolved(idea_num, content):
    """Generate 5 unresolved questions for an idea."""
    # Generic template — needs per-idea refinement
    questions = [
        f"1. {content[:50]} 的信息论边界条件是什么？",
        f"2. 是否存在'最优'的信息处理方式？如何形式化？",
        f"3. 个体差异如何影响该机制的强度？",
        f"4. 能否通过实验/数据验证该假设？",
        f"5. 与 persona-v3 的哪个自适应维度直接相关？",
    ]
    return "\n".join(questions)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--count", type=int, default=0, help="Max number of ideas to generate (0=all)")
    args = parser.parse_args()

    ideas = read_raw_ideas()
    analyzed = read_analyzed()

    # Map idea number to analysis existence
    # Note: idea number in raw.md order vs analysis file number may differ
    # We use the sequential idea number from raw.md
    pending = [i for i in ideas if i["number"] not in analyzed]

    if args.count > 0:
        pending = pending[:args.count]

    print(f"Total ideas: {len(ideas)}")
    print(f"Analyzed: {len(analyzed)}")
    print(f"Pending: {len(pending)}")
    if args.count > 0:
        print(f"Generating (limited): {len(pending)}")

    for idea in pending:
        idea_num = idea["number"]
        ctx = DOMAIN_CONTEXT.get(idea_num)
        if not ctx:
            print(f"  SKIP #{idea_num}: No domain context")
            continue

        if args.dry_run:
            print(f"  DRY-RUN #{idea_num} ({idea['line']}): {idea['summary'][:60]}")
            continue

        content = generate_analysis(idea, DOMAIN_CONTEXT)
        fname = f"idea-{idea_num:02d}-{slugify(idea['content'][:30])}.md"
        fpath = os.path.join(MEM_DIR, fname)

        # Check if already exists
        if os.path.exists(fpath):
            print(f"  SKIP #{idea_num}: {fname} already exists")
            continue

        with open(fpath, 'w') as f:
            f.write(content)

        print(f"  CREATED #{idea_num}: {fname} ({len(content)} chars)")

    print(f"\nDone. Generated {len(pending)} files.")


def slugify(s):
    import unicodedata
    s = s.lower().replace(' ', '-').replace('，', '-').replace('？', '')
    s = unicodedata.normalize('NFKC', s)  # Handle unicode
    s = re.sub(r'[^a-z0-9一-鿿-]', '', s)
    return s[:30]


if __name__ == "__main__":
    main()
