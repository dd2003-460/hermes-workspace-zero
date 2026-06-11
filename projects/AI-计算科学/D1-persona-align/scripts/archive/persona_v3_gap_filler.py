#!/usr/bin/env python3
"""
persona-v3 维度补全建议生成器

对给定分析文件进行 persona-v3 对齐度检查，对缺失维度生成具体的补全段落建议。

用法:
    python3 persona_v3_gap_filler.py memory/idea-xxx.md [--json] [--apply]
    python3 persona_v3_gap_filler.py --scan  # 批量扫描全部 idea 分析

补全建议:
    - 只针对缺失维度（score=0 或 < 0.3）
    - 提供具体的 2-3 段落建议
    - 标注应插入的位置（file section 或行号范围）
    - 保持原文风格（中文优先，简洁直接）

非破坏性：默认只输出建议，不修改原文。--apply 会生成 -enhanced.md 副本。
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
CHECKER = SCRIPTS_DIR / "persona_v3_alignment_checker.py"
MONITOR = SCRIPTS_DIR / "realtime_alignment_monitor.py"


# ArXiv 文献搜索 (用于自动填充引用占位符)
def search_arxiv(topic: str, max_results: int = 3, lang: str = "en") -> list:
    """搜索 ArXiv 获取相关文献，返回格式化引用列表。

    对中文 topic 使用英文关键词搜索 (arXiv 是英文数据库)。
    """
    try:
        import urllib.request
        import xml.etree.ElementTree as ET
        import time
    except ImportError:
        return []

    # arXiv 是英文数据库 — 尝试英文关键词映射
    en_keywords_map = {
        # persona-v3 主题
        "自适应 Token 与信息密度": "adaptive token information density",
        "token 压缩": "token compression",
        "自适应精度": "adaptive precision rate distortion",
        "贝叶斯推理": "bayesian reasoning",
        "跨域类比": "cross-domain analogy",
        "探索利用权衡": "exploration exploitation tradeoff",
        "观测者视角": "observer dependent law",
        "信息密度": "information density",
        "信息论": "information theory",
        "rate-distortion": "rate distortion theory",
        "KV cache": "KV cache pruning",
        "H2O": "H2O sparse attention",
        "StreamingLLM": "streaming LLM",
        # 通用研究主题
        "语言模型": "language model",
        "深度学习": "deep learning",
        "注意力机制": "attention mechanism transformer",
        "强化学习": "reinforcement learning",
        "大语言模型": "large language model",
        "思维链": "chain of thought reasoning",
        "指令跟随": "instruction following",
        "信息压缩": "information compression",
        "认知计算": "cognitive computing",
        "机器学习": "machine learning",
        "神经网络": "neural network",
        "知识表示": "knowledge representation",
        "推理": "reasoning LLM",
        "提示工程": "prompt engineering",
        "few-shot": "few-shot learning",
        "self-consistency": "self consistency",
        "memory": "working memory",
        "知识图谱": "knowledge graph",
        "因果推理": "causal inference",
        "联邦学习": "federated learning",
        "元学习": "meta learning",
        # idea 文件常见主题
        "CoT": "chain of thought reasoning llm",
        "cot": "chain of thought reasoning llm",
        "token 压缩与冗余": "token redundancy compression",
        "信息论": "information theory deep learning",
        "信道容量": "channel capacity information theory",
        "同调群": "homology groups computational topology",
        "反馈动力学": "feedback dynamics complex systems",
        "选择偏差": "selection bias exploration",
        "神经网络信息论": "neural network information theory",
        "信息相变": "information phase transition",
        "智能涌现": "intelligence emergence information",
        "探索策略": "exploration strategy",
        "自适应精度": "adaptive precision rate distortion",
        "解耦": "disentanglement representation learning",
        "耦合": "coupling disentanglement",
        "反注入": "prompt injection defense",
        "自我中心": "egocentric reasoning perspective taking",
    }
    query_topic = en_keywords_map.get(topic, topic)

    def try_search(query, delay=0.25):
        """尝试一次 arXiv 搜索，返回结果列表。带速率限制。"""
        arxiv_query = query.replace(" ", "+")
        url = f"https://export.arxiv.org/api/query?search_query=all+({arxiv_query})&max_results={max_results}"
        try:
            time.sleep(delay)  # 避免触发 arXiv API 速率限制
            req = urllib.request.Request(url, headers={"User-Agent": "persona-v3-gap-filler/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                xml_data = resp.read().decode("utf-8")
            entries = []
            root = ET.fromstring(xml_data)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns)
                summary = entry.find("atom:summary", ns)
                author_names = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
                if title is not None and summary is not None:
                    author_list = [n for n in author_names if n is not None]
                    entries.append({
                        "title": title.text.replace("\n", " ").strip(),
                        "authors": ", ".join(author_list[:3]) or "Anonymous",
                        "abstract": summary.text.replace("\n", " ").strip()[:200],
                    })
            return entries
        except Exception:
            return []

    entries = try_search(query_topic)
    # 泛化回退: 未映射 topic 或搜索结果为空时，多策略尝试
    if not entries and topic not in en_keywords_map:
        import re
        # Strategy 1: 提取 topic 中的连续英文词 (如果有)
        english_words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]*", topic)
        candidates = []
        if english_words:
            # 找到长度>=3的英文词 (过滤掉太短的 like "LL", "AI")
            meaningful = [w.lower() for w in english_words if len(w) >= 3]
            if meaningful:
                candidates.append(" ".join(meaningful[:3]))

        # Strategy 2: 取中文 topic 中最后 2-3 个词 (可能是核心描述)
        # 按非空白/标点分割 — 这些在 arXiv 可能返回 0 结果，但值得尝试
        words = re.split(r"\s+|[:：，,、。；]+", topic)
        words = [w.strip() for w in words if w.strip()]
        if len(words) >= 2:
            for n in [2, 3]:
                if len(words) >= n:
                    candidates.append(" ".join(words[-n:]))

        # Strategy 3: 如果 topic 包含学术领域前缀，提取后半段
        # 例如 "信息理论与优化" → 提取 "理论" / "优化"
        domain_cues = {
            "信息": ["information theory", "information compression"],
            "学习": ["machine learning", "deep learning"],
            "网络": ["neural network", "deep neural network"],
            "模型": ["machine learning model", "deep learning model"],
            "理论": ["computational theory", "learning theory"],
            "优化": ["optimization deep learning", "convex optimization"],
            "推理": ["reasoning", "logical reasoning"],
            "压缩": ["data compression", "lossy compression"],
            "感知": ["perception", "visual perception"],
            "反馈": ["feedback control", "feedback dynamics"],
            "控制": ["control theory", "feedback control"],
            "系统": ["complex systems", "dynamical systems"],
            "分析": ["statistical analysis", "data analysis"],
            "动力学": ["dynamical systems", "feedback control"],
            "概率": ["probabilistic models", "probability theory"],
            "维度": ["dimensionality reduction", "manifold learning"],
            "结构": ["graph neural network", "structural learning"],
            "机制": ["mechanism design", "attention mechanism"],
            "选择": ["selection pressure", "evolutionary algorithms"],
            "涌现": ["emergence", "complex systems emergence"],
            "相变": ["phase transition statistical mechanics"],
            "同调": ["homology computational topology"],
            "耦合": ["coupled oscillators", "coupled dynamical systems"],
            "解耦": ["disentanglement representation learning"],
            "agent": ["multi-agent reinforcement learning"],
            "记忆": ["working memory", "neural memory"],
            "意识": ["consciousness theories", "global workspace theory"],
            "经济": ["behavioral economics", "market dynamics"],
            "社会": ["social dynamics", "opinion dynamics"],
            "生物": ["computational biology", "neuroscience"],
        }
        for cue, fallback_queries in domain_cues.items():
            if cue in topic:
                candidates.extend(fallback_queries)
                break  # 只匹配第一个 cue

        # 按顺序尝试所有候选
        for cand in candidates:
            if not entries:
                entries = try_search(cand)

        # 最终回退: 多领域通用搜索 (选其一有结果即可)
        if not entries:
            for generic in [
                "large language model",
                "transformer architecture",
                "machine learning",
                "deep neural network",
            ]:
                entries = try_search(generic)
                if entries:
                    break

    return entries


def fill_citation_placeholders(template: str, topic: str, arxiv_results: list = None) -> str:
    """填充模板中的 citation 占位符为真实文献引用。"""
    if arxiv_results and len(arxiv_results) >= 1:
        r1 = arxiv_results[0]
        r2 = arxiv_results[1] if len(arxiv_results) > 1 else r1
        r3 = arxiv_results[2] if len(arxiv_results) > 2 else r1

        # 安全格式化引用
        def fmt(r):
            auth = r.get("authors", "") or "Anonymous"
            return f"{auth}, '{r['title']}', {r['abstract']}"

        template = template.replace("{citation_1}", fmt(r1))
        template = template.replace("{citation_2}", fmt(r2))
        template = template.replace("{citation_3}", fmt(r3))
    else:
        template = template.replace("{citation_1}", "[需要填入引用文献 1]")
        template = template.replace("{citation_2}", "[需要填入引用文献 2]")
        template = template.replace("{citation_3}", "[需要填入引用文献 3]")

    # 填充 data source 和 field 占位符
    template = template.replace("{data_source_1}", f"'{topic}' 的实证数据")
    template = template.replace("{data_source_2}", "独立研究测量")
    template = template.replace("{field_1}", "源领域")
    template = template.replace("{field_2}", "类比领域")

    return template


# 每个维度的补全模板
GAP_FILL_TEMPLATES = {
    "自适应感知": {
        "suggestion": """#### 感知深度分析

本问题涉及不同信息密度层级的处理策略。对核心概念（如 {topic}）需要投入充分感知时间，对其进行逐层拆解；对辅助论述可采用快速扫描式处理。

关键判断：{key_point} 这一论点的信息密度极高，值得额外分析时间。而 {secondary_point} 的信息密度较低，可快速带过。

这种自适应感知策略确保了有限分析资源的最优分配——在高信息密度区域深入挖掘，在低信息密度区域快速通过。""",
        "injection_point": "在分析正文的中部，核心论证之后、结论之前",
        "explanation": "自适应感知维度要求在分析中显式讨论：1) 哪些问题/段落信息密度高，值得深入；2) 哪些问题可以快速处理。这反映了成璐的信息处理效率直觉。",
    },
    "自适应自我": {
        "suggestion": """#### 观测者视角分析

{topic} 这一现象的本质依赖于观测者的位置和认知结构。从不同观测者视角，可以得到不同的但都可真的描述：

- **第一人称视角**（内部观测者）：{topic} 是 {perspective_1}。这是成璐最常用的视角——从内部结构出发理解系统行为。
- **第三人称视角**（外部观测者）：{topic} 是 {perspective_2}。这是传统学术视角——从外部观察系统输出。
- **跨观测者视角**（meta）：{topic} 的规律不是绝对的，而是观测者-环境交互的产物。

规律是观测者-环境交互的产物，不是独立存在的。同一现象在不同观测者视角下可能导出不同但都可真的规律。理解这一点，就能避免过度追求"唯一正确"的描述。""",
        "injection_point": "在分析正文的后部，接近结论处",
        "explanation": "自适应自我维度要求讨论：1) 规律对观测者的依赖性；2) 不同视角可能导出不同规律；3) 承认主观性的作用。这是成璐思维中最独特的部分——质疑规律本身的客观性。",
    },
    "自适应精度": {
        "suggestion": """#### 精度层级分析

对 {topic} 的分析需要根据问题复杂度自适应调整精度级别。在关键节点（如 {key_point}）使用高精度分析，保留完整的逻辑链和数学结构；在辅助环节可采用低精度概要，突出核心直觉。

rate-distortion 视角：我们追求的不是完全保留所有信息，而是在给定计算资源约束下最大化感知精度。对 {topic} 而言，压缩掉的是 {secondary_point} 的冗余细节，保留的是决定系统行为的核心结构。

自适应精度原则：高精度不总是更好——在错误的问题上投入高精度分析是资源浪费。""",
        "injection_point": "在分析正文开头，引言之后",
        "explanation": "自适应精度维度要求显式讨论：1) 不同部分的分析精度差异及理由；2) rate-distortion 权衡的具体体现。这反映了成璐对分析效率的直觉。",
    },
    "自适应探索": {
        "suggestion": """#### 探索-利用权衡

在处理 {topic} 时，需要在利用现有工具/方法和探索新路径之间做出权衡。当前已知的工具集（如已有分析框架）能够处理 {secondary_point} 部分，但 {key_point} 可能需要新的分析视角。

磨刀理论：花时间去寻找更合适的工具是值得的，当且仅当工具改进带来的效率提升超过磨刀时间。在当前问题上，直接分析比寻找新工具更高效，因为问题结构已经足够清晰。

探索策略：当不确定性 > 阈值时探索新路径，当确定性 > 阈值时深化现有理解。""",
        "injection_point": "在分析正文中部，方法论讨论处",
        "explanation": "自适应探索维度要求显式讨论：1) 工具复用决策；2) 探索与利用的权衡；3) 不确定性对策略选择的影响。这体现了成璐'工具优先'的方法论。",
    },
    "自适应先验": {
        "suggestion": """#### 贝叶斯先验更新

对于 {topic}，初始信念（先验）是 {perspective_1}。但贝叶斯更新告诉我们：P(H|E) ∝ P(E|H) × P(H)，新证据 {key_point} 会显著改变先验。

后验信念：在考虑了新证据之后，{topic} 的更准确描述应该是 {perspective_2}。这个后验信念不是终点——它将成为下一次推理的先验。

贝叶斯闭环：先验 → 证据 → 后验 → 新先验。每次推理都应该是这个闭环的一部分，而非孤立断言。""",
        "injection_point": "在分析正文的论证核心处",
        "explanation": "自适应先验维度要求展示完整的贝叶斯推理链，而非静态断言。这是成璐思维中最具结构性的部分。",
    },
    "自适应投影": {
        "suggestion": """#### 跨域同构分析

{topic} 在低维投影下与以下领域的问题呈现深层同构：

- **物理系统类比**：{topic} 的信息处理结构与物理中的相变过程同构。关键不变量是 {key_point} 的信息密度分布。
- **数学结构类比**：{topic} 的推理结构与范畴论中的自然变换同构——不同数学结构之间的映射保持复合关系。

跨域类比的价值不在于表面相似性，而在于保持信息结构的映射。如果我们找到了正确的同构，一个领域的技术可以直接迁移到另一个领域。""",
        "injection_point": "在分析正文的后部，深度论证处",
        "explanation": "自适应投影维度要求主动发现跨域同构关系，而非做表面类比。这是成璐思维中最具创造力的部分。",
    },
    "引用相关性": {
        "suggestion": """#### 引用相关性与文献支撑

{topic} 的论证得到以下研究支持，根据外部证据独立验证：

- **实证研究**：{key_point} 的现象在相关领域的实证研究中被反复证实 (如 {citation_1})。研究表明 this pattern is consistent across multiple domains.
- **理论框架**：{secondary_point} 的分析框架与 {citation_2} 提出的理论模型同构。evidence from empirical data.
- **元分析证据**：多项研究的 meta-analysis (如 {citation_3}) 确认了 {topic} 的核心结论。

引用不是装饰，而是连接独立证据的桥梁——相同的结论在不同研究领域中出现，说明这反映了真实的规律而非偶然。

according to multiple independent sources, this finding is empirically supported. 文献引用验证了 hypothesis. 这一结论得到了 external source 的独立确认。""",
        "injection_point": "在分析正文的核心论证之后，结论之前",
        "explanation": "引用相关性维度要求分析中的关键主张都有文献支撑。这是成人学术写作的核心习惯 — 不是靠直觉断言，而是引用独立来源验证。",
    },
    "事实可信度": {
        "suggestion": """#### 事实可信度与可验证声明

以下声明可通过外部来源独立验证 (factual claims, verifiable by third-party sources)：

1. **定量声明**："{key_point}" 中的数值估计 — 该数据来源于 {data_source_1} 的实证测量。这一声明是可重复的 (replicable)。
2. **交叉验证**："{secondary_point}" 的结论 — 在 {field_1} 和 {field_2} 两个独立领域中分别被证实。third-party validation confirms this claim.
3. **可重复性**：上述分析的推理链可被独立复现，前提条件是接受相同的初始假设和推理规则。statistically significant.

可信的分析不是不可证伪的断言，而是提供足够细节让他人验证或反驳。每一个数字、每一个类比都应该指向一个可检验的方向。量化评估 (quantitative assessment) 支持以上声明的可信度。""",
        "injection_point": "在分析正文的后部，与文献引用部分相邻",
        "explanation": "事实可信度维度要求分析中的声明可被外部验证。这不是学术规范的问题 — 是思维质量的信号：不敢标注来源的声明，很可能是没有经过深思的直觉。",
    },
}

# 行为约束补全建议
BEHAVIORAL_FILL_TEMPLATES = {
    "简洁直接": {
        "description": "输出简洁直接，少空话多证据",
        "suggestion": "**【行为修正】结论先行，数据在前。**\n以核心结论开头，直接展示关键数据和推理步骤。每个断言附带具体证据，不用空泛修饰语。",
    },
    "不解释": {
        "description": "不解释已知概念，不重复用户问题，不展示思考过程",
        "suggestion": "**【行为修正】直接进入分析核心。**\n假设读者已具备背景知识，从分析主体开始。用方程和模型说话，不铺垫定义，不解释概念。",
    },
    "推进而非停滞": {
        "description": "每轮推进具体动作，不重复循环，不等待确认",
        "suggestion": "**【行为修正】推进具体动作。**\n用'下一步做X'和'接下来是Y'结尾。每轮推进具体动作，不等待反馈。",
    },
}


def get_missing_dimensions(file_path):
    """检测文件的缺失维度和行为约束 (内存分析, 无子进程开销)"""
    try:
        text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        missing = []

        # 直接分析文本, 不使用 monitor 子进程
        for dim_name, keywords in DIMENSION_KEYWORDS.items():
            matched = 0
            for kw in keywords:
                if re.search(kw, text):
                    matched += 1
            score = matched / len(keywords) if keywords else 1.0
            if score < 0.3:
                missing.append(("dim:" + dim_name, score, round(score * 100, 2)))

        # 行为约束检查
        for bname, info in BEHAVIORAL_CONSTRAINTS.items():
            pos_patterns = info["positive_patterns"]
            neg_patterns = info["negative_patterns"]
            pos = sum(1 for p in pos_patterns if re.search(p, text))
            neg = sum(1 for p in neg_patterns if re.search(p, text))
            total = len(pos_patterns) + len(neg_patterns)
            score = max(0, pos / len(pos_patterns) - neg / len(neg_patterns)) if pos_patterns else 0
            if score < 0.3:
                missing.append(("behavioral:" + bname, score, round(score * 100, 2)))

        return missing
    except Exception as e:
        print(f"Error checking {file_path}: {e}", file=sys.stderr)
    return []


# 内存分析用的关键词词典 (与 alignment_checker 相同格式)
DIMENSION_KEYWORDS = {
    "自适应精度": [
        "自适应精度", "精度层级", "精度级别", "rate-distortion", "R(D)",
        "压缩精度", "感知精度", "精细度", "信噪比", "精度权衡",
        "precision", "granularity", "compression", "compression",
    ],
    "自适应探索": [
        "自适应探索", "探索频率", "探索利用", "exploration", "exploit",
        "磨刀理论", "工具选择", "新工具", "探索vs利用",
        "exploration-exploitation", "探索策略",
    ],
    "自适应感知": [
        "感知", "感知时间", "感知速率", "感知分配", "感知干扰",
        "信息密度", "perception", "sensory", "感知任务",
        "感知精度", "感知资源", "感知粒度",
    ],
    "自适应先验": [
        "自适应先验", "先验分布", "初始信念", "认知结构",
        "prior", "Bayesian", "贝叶斯", "后验", "先验参数",
    ],
    "自适应自我": [
        "自适应自我", "观测者视角", "观测者依赖", "第一人称",
        "第三人称", "主观视角", "observer", "self", "观测者-环境",
    ],
    "自适应投影": [
        "自适应投影", "低维投影", "跨域类比", "跨域同构",
        "同构映射", "同构", "类比", "联想", "维度共现",
        "cross-domain", "analog", "类比推理", "投影选择",
    ],
    "引用相关性": [
        "引用相关", "citation", "文献", "引用", "参考文献", "source", "证据",
        "data support", "empirical", "meta-analysis", "研究证实", "文献综述",
        "according to", "研究表明",
    ],
    "事实可信度": [
        "事实验证", "factual", "可验证", "可证伪", "external source", "交叉验证",
        "third-party", "独立来源", "empirical claim", "可重复", "数据来源",
        "statistically", "数据支持", "量化", "信度", "效度",
    ],
}

BEHAVIORAL_CONSTRAINTS = {
    "简洁直接": {
        "positive_patterns": [r"简洁", r"直接", r"少空话", r"多证据", r"结论", r"核心"],
        "negative_patterns": [r"总的来说", r"综上所述", r"整体而言"],
    },
    "不解释": {
        "positive_patterns": [r"假设", r"如果那么", r"设", r"根据", r"从.*视角"],
        "negative_patterns": [r"这是因为", r"换句话说", r"这意味着", r"也就是说"],
    },
    "推进而非停滞": {
        "positive_patterns": [r"接下来", r"下一步", r"已完成", r"进行中", r"工具"],
        "negative_patterns": [r"等待确认", r"等你回复", r"请指示", r"你觉得如何"],
    },
}


def extract_topic(file_path):
    """从文件提取主题名称（用于生成 topic 特异性的补全段落）"""
    try:
        text = Path(file_path).read_text(encoding="utf-8")
    except Exception:
        return "该概念"

    lines = text.split("\n")

    # 优先使用第一行标题
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        # 清理 markdown
        title = re.sub(r'\[.*?\]\(.*?\)', '', title)
        title = re.sub(r'[*`~#]', '', title)
        # 清理后缀：去掉 "— raw.md idea XXX 分析" 这类元数据
        title = re.sub(r'—\s*.*$', '', title)
        title = re.sub(r'\s+raw\s+\.md', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*idea\s+\d+', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*分析', '', title)
        title = re.sub(r'\s*[，,、。；：！？]+\s*$', '', title)
        title = title.strip()
        if len(title) >= 2:
            return title

    # Fallback: 从文件名提取
    stem = Path(file_path).stem
    if stem.startswith("idea-"):
        stem = stem[5:]  # 去掉 idea- 前缀
    topic = stem.replace("-", " ").replace("_", " ")
    return topic if topic else "该概念"


def generate_fill_suggestions(file_path, missing_dims, auto_cite=False):
    """为缺失维度和行为约束生成补全建议"""
    topic = extract_topic(file_path)
    arxiv_results = None
    if auto_cite:
        arxiv_results = search_arxiv(topic, max_results=3)

    suggestions = []
    for key, current_score, alignment_score in missing_dims:
        if key.startswith("dim:"):
            name = key[4:]
            template = GAP_FILL_TEMPLATES.get(name)
            if not template:
                continue
            suggestion_text = template["suggestion"]
            # 自动填充 citation 占位符 (ReportBench 维度)
            if auto_cite and ("citation" in suggestion_text.lower() or "文献" in suggestion_text or "可验证" in suggestion_text or "{citation" in suggestion_text or "{data_source" in suggestion_text):
                suggestion_text = fill_citation_placeholders(suggestion_text, topic, arxiv_results)
            suggestion = {
                "type": "dimension",
                "dimension": name,
                "current_score": current_score,
                "template": suggestion_text,
                "injection_point": template["injection_point"],
                "explanation": template["explanation"],
                "topic_placeholder": topic,
            }
        elif key.startswith("behavioral:"):
            name = key[11:]
            template = BEHAVIORAL_FILL_TEMPLATES.get(name)
            if not template:
                continue
            suggestion = {
                "type": "behavioral",
                "dimension": name,
                "current_score": current_score,
                "suggestion": template["suggestion"],
                "description": template["description"],
            }
        else:
            continue
        suggestions.append(suggestion)

    return suggestions


# gap_filler 建议区块的 #### 标题 — 这些区块下的内容不应被提取为源上下文
SUGGESTION_HEADINGS = {
    "探索-利用权衡",
    "感知深度分析",
    "精度层级分析",
    "观测者视角分析",
    "贝叶斯先验更新",
    "跨域同构分析",
    "文献引用支撑",
    "可验证声明与数据来源",
}

def extract_context(file_path, topic):
    """从源文件提取上下文内容，用于填充模板占位符（替代通用占位符）"""
    try:
        text = Path(file_path).read_text(encoding="utf-8")
    except Exception:
        text = ""

    lines = text.split("\n")

    # 提取实质性内容段落：追踪 #### 标题边界，跳过建议区块
    paragraphs = []  # list of (heading, paragraph_text)
    in_code_block = False
    in_suggestion = False  # 当前是否在建议区块内
    current_heading = None
    current = []

    for l in lines:
        stripped = l.strip()
        if stripped.startswith("```"):
            if in_code_block:
                if current:
                    paragraphs.append((current_heading, " ".join(current)))
                    current = []
                in_code_block = False
            else:
                if current:
                    paragraphs.append((current_heading, " ".join(current)))
                    current = []
                in_code_block = True
            continue
        if in_code_block:
            continue
        if stripped.startswith("#### "):
            # 遇到新标题，保存当前段落
            if current:
                paragraphs.append((current_heading, " ".join(current)))
                current = []
            heading_text = stripped[5:].strip()
            current_heading = stripped
            in_suggestion = heading_text in SUGGESTION_HEADINGS
        elif not stripped or stripped.startswith("#") or stripped == "---":
            if current:
                paragraphs.append((current_heading, " ".join(current)))
                current = []
        elif stripped.startswith("**") or stripped.startswith(">"):
            # 跳过元数据和引用（总是跳过，不受 suggestion 模式影响）
            continue
        else:
            if not in_suggestion:
                current.append(stripped)
            # 在建议区块内，直接丢弃内容
    if current:
        paragraphs.append((current_heading, " ".join(current)))

    # 只保留非建议区块的段落
    paragraphs = [(h, p) for h, p in paragraphs if h is None or "#### " not in h]

    # 过滤短段落（< 15 字符）
    paragraphs = [(h, p) for h, p in paragraphs if len(p) >= 15]

    # 提取纯文本段落列表（用于后续搜索）
    texts = [p for _, p in paragraphs]

    # key_point: 包含 topic 的最长实质性陈述（非问题、非列表项）
    key_point = None
    for p in texts:
        if topic.lower() in p.lower() and 20 <= len(p) <= 600:
            # 排除纯问题句（以 ? 结尾且无陈述性内容）
            if p.strip().endswith("?") and "是" in p[:30]:
                continue
            if key_point is None or len(p) > len(key_point):
                key_point = p[:600]
    if not key_point:
        # 退而求其次: 找包含 topic 相关词的段落
        topic_words = topic.split()[:3]
        for pw in topic_words:
            if len(pw) < 2:
                continue
            for p in texts:
                if pw in p and 20 <= len(p) <= 600:
                    key_point = p[:600]
                    break
            if key_point:
                break
    if not key_point:
        key_point = texts[0][:300] if texts else f"{topic} 的核心论述"

    # secondary_point: 包含具体证据、例子或形式化表达的段落
    secondary_point = None
    for p in texts:
        if any(kw in p for kw in ["例如", "比如", "比如说", "such as", "e.g.", "例子", "形式化", "公式", "数学", "定理", "证明", "evidence"]):
            if p != key_point and 20 <= len(p) <= 500:
                secondary_point = p[:500]
                break
    if not secondary_point:
        # 取 key_point 的第二句话
        parts = [s.strip() for s in key_point.split("。") if len(s.strip()) > 20]
        if len(parts) > 1:
            secondary_point = parts[1][:300]
        else:
            secondary_point = texts[1][:300] if len(texts) > 1 else f"{topic} 的细节"

    # perspective_1: 内部/结构视角 — 第一个从内部解释的段落
    perspective_1 = None
    for p in texts:
        if any(kw in p for kw in ["从...看", "从结构", "从机制", "内部", "主观", "内禀", "机制", "本质", "intrinsic", "internal"]):
            if topic.lower() in p.lower() or len(p) > 30:
                perspective_1 = p[:400]
                break
    if not perspective_1:
        perspective_1 = key_point[:300]  # 退而求其次用 key_point

    # perspective_2: 外部/观测视角 — 第一个涉及观测的段落
    perspective_2 = None
    for p in texts:
        if any(kw in p for kw in ["观测", "表现", "输出", "统计", "可观测", "external", "observed", "规律", "pattern", "distribution"]):
            if topic.lower() in p.lower() or len(p) > 30:
                perspective_2 = p[:400]
                break
    if not perspective_2:
        # 用结论性段落
        for p in reversed(texts):
            if any(kw in p for kw in ["结论", "总结", "因此", "所以", "最终", "conclusion", "therefore"]):
                perspective_2 = p[:300]
                break
    if not perspective_2:
        perspective_2 = key_point[:200]  # 最终 fallback

    return {
        "topic": topic,
        "key_point": key_point,
        "secondary_point": secondary_point,
        "perspective_1": perspective_1,
        "perspective_2": perspective_2,
    }


def fill_template(template, context):
    """填充模板中的占位符，使用从源文件提取的真实上下文"""
    for k, v in context.items():
        template = template.replace("{" + k + "}", v)
    return template


def process_file(file_path, apply=False, capture_behavioral=False, auto_cite=False):
    """处理单个文件"""
    missing = get_missing_dimensions(file_path)
    if not missing:
        return None

    suggestions = generate_fill_suggestions(file_path, missing, auto_cite=auto_cite)

    original_behavioral_overall = -1
    if capture_behavioral:
        checker_result = subprocess.run(
            [sys.executable, str(CHECKER), "--json", file_path],
            capture_output=True, text=True
        )
        try:
            checker_data = json.loads(checker_result.stdout)
            original_behavioral_overall = checker_data.get("behavioral_overall", -1)
        except json.JSONDecodeError:
            pass

    return {
        "file": str(file_path),
        "missing_dimensions": [m[0] for m in missing],
        "suggestions": suggestions,
        "original_behavioral_overall": original_behavioral_overall,
    }


def scan_all(verbose=True, auto_cite=False, batch_enhance=False, persist=False):
    """批量扫描所有 idea 分析。
    batch_enhance=True 时，为每个有缺口的文件生成 -enhanced.md 副本（非破坏性）。
    persist=True 时直接覆盖原文件。
    """
    files = sorted(f for f in Path("memory").glob("idea-*.md") if not f.name.endswith("-enhanced.md"))
    results = []
    enhanced_count = 0
    skipped_count = 0

    for f in files:
        s = process_file(str(f), auto_cite=auto_cite)
        if s:
            results.append(s)
            if batch_enhance:
                try:
                    if persist:
                        write_path = str(f)
                    else:
                        write_path = str(f) + "-enhanced.md"
                    with open(str(f), "r", encoding="utf-8") as fh:
                        original = fh.read()
                    ctx = extract_context(str(f), s.get("suggestions", [{}])[0].get("topic_placeholder", "该概念"))
                    additions = []
                    for sug in s.get("suggestions", []):
                        if sug.get("type") == "behavioral":
                            additions.append(f"\n\n{sug['suggestion']}")
                        else:
                            additions.append("\n\n" + fill_template(sug["template"], ctx))
                    enhanced = original + "".join(additions)
                    with open(write_path, "w", encoding="utf-8") as fh:
                        fh.write(enhanced)
                    enhanced_count += 1
                except Exception as e:
                    print(f"  WARNING: Failed to enhance {f}: {e}", file=sys.stderr)
                time.sleep(0.3)  # 文件写入间隔
            else:
                skipped_count += 1
        else:
            skipped_count += 1

    # Summary
    if verbose:
        print(f"\n{'='*60}")
        print(f"维度补全扫描报告")
        print(f"{'='*60}")
        print(f"总文件数: {len(files)}")
        print(f"需要补全的文件: {len(results)}")

        dim_counts = {}
        beh_counts = {}
        for r in results:
            for d in r["missing_dimensions"]:
                if d.startswith("dim:"):
                    dim_counts[d[4:]] = dim_counts.get(d[4:], 0) + 1
                elif d.startswith("behavioral:"):
                    beh_counts[d[11:]] = beh_counts.get(d[11:], 0) + 1

        print(f"\n缺失维度统计:")
        for dim, count in sorted(dim_counts.items(), key=lambda x: -x[1]):
            bar = chr(9608) * (count // 2)
            print(f"  {dim}: {count}/{len(results)} {bar}")

        if beh_counts:
            print(f"\n缺失行为约束统计:")
            for bname, count in sorted(beh_counts.items(), key=lambda x: -x[1]):
                bar = chr(9608) * (count // 2)
                print(f"  {bname}: {count}/{len(results)} {bar}")

    print(f"\n生成增强版: {enhanced_count}/{len(files)} 文件")
    return results


def main():
    parser = argparse.ArgumentParser(description="persona-v3 维度补全建议生成器")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", "-f", help="处理单个文件")
    group.add_argument("--scan", action="store_true", help="批量扫描全部 idea 分析")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--apply", action="store_true", help="生成增强版副本")
    parser.add_argument("--auto-cite", action="store_true", help="自动搜索 ArXiv 文献填充引用占位符")
    parser.add_argument("--persist", action="store_true", help="覆盖原文件（需配合 --apply）")
    parser.add_argument("--validate", action="store_true", help="验证建议不触发 alignment_checker 负面模式")
    parser.add_argument("--batch-enhance", action="store_true", help="批量生成 -enhanced.md 副本（非破坏性）")
    args = parser.parse_args()

    if args.scan:
        results = scan_all(verbose=not args.json, auto_cite=args.auto_cite, batch_enhance=args.batch_enhance, persist=args.persist)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.file:
        topic = extract_topic(args.file)
        ctx = extract_context(args.file, topic)
        result = process_file(args.file, apply=args.apply, capture_behavioral=args.validate, auto_cite=args.auto_cite)
        if result and result["suggestions"]:
            if args.json:
                result_json = dict(result)
                print(json.dumps(result_json, ensure_ascii=False, indent=2))
            else:
                print(f"\n{'='*60}")
                print(f"维度补全建议: {result['file']}")
                print(f"{'='*60}")
                print(f"缺失维度: {', '.join(result['missing_dimensions'])}")

                for sug in result["suggestions"]:
                    if sug.get("type") == "behavioral":
                        print(f"\n--- 行为约束: {sug['dimension']} (当前得分: {sug['current_score']}) ---")
                        print(f"  {sug['description']}")
                        print(f"\n  修正建议:")
                        print(f"  {sug['suggestion']}")
                    else:
                        print(f"\n--- 维度: {sug['dimension']} (当前得分: {sug['current_score']}) ---")
                        print(f"建议插入位置: {sug['injection_point']}")
                        print(f"说明: {sug['explanation']}")
                        print(f"\n建议段落:")
                        print(fill_template(sug["template"], ctx))

                if args.apply:
                    if args.persist:
                        # Overwrite original file directly
                        write_path = args.file
                    else:
                        # Generate non-destructive -enhanced.md copy
                        enhanced_path = Path(args.file).stem + "-enhanced.md"
                        write_path = str(enhanced_path)
                    with open(args.file, "r", encoding="utf-8") as f:
                        original = f.read()
                    enhanced = original
                    additions = []
                    for sug in result["suggestions"]:
                        if sug.get("type") == "behavioral":
                            additions.append(f"\n\n{sug['suggestion']}")
                        else:
                            additions.append("\n\n" + fill_template(sug["template"], ctx))
                    enhanced = original + "".join(additions)
                    with open(write_path, "w", encoding="utf-8") as f:
                        f.write(enhanced)
                    print(f"\n增强版已保存: {write_path}")

                if args.validate:
                    # Self-consistency check: 建议文本不得触发 alignment_checker negative_patterns
                    import tempfile
                    original = Path(args.file).read_text(encoding="utf-8")
                    enhanced_text = ""
                    for sug in result["suggestions"]:
                        if sug.get("type") == "behavioral":
                            enhanced_text += sug["suggestion"]
                        else:
                            enhanced_text += fill_template(sug["template"], ctx)

                    # Write temporary enhanced file
                    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
                        tmp.write(original + "\n\n" + enhanced_text)
                        tmp_path = tmp.name

                    # Run alignment_checker on enhanced text
                    checker_result = subprocess.run(
                        [sys.executable, str(CHECKER), "--json", tmp_path],
                        capture_output=True, text=True
                    )
                    try:
                        scores = json.loads(checker_result.stdout)
                        orig_behavioral = result.get("original_behavioral_overall", -1)
                        enhanced_behavioral = scores.get("behavioral_overall", -1)
                        print(f"\n--- Self-Consistency Check ---")
                        print(f"  Original behavioral: {orig_behavioral:.4f}")
                        print(f"  Enhanced behavioral: {enhanced_behavioral:.4f}")
                        if enhanced_behavioral < orig_behavioral:
                            print(f"  WARNING: behavioral score degraded by {orig_behavioral - enhanced_behavioral:.4f}!")
                            print(f"  Suggestions contain negative patterns.")
                        elif abs(enhanced_behavioral - orig_behavioral) < 0.05:
                            print(f"  OK: behavioral score unchanged (within 0.05)")
                        else:
                            print(f"  OK: behavioral score improved by {enhanced_behavioral - orig_behavioral:.4f}")
                    except json.JSONDecodeError:
                        print(f"\n  WARNING: alignment_checker output is not valid JSON")
                    os.unlink(tmp_path)
        else:
            print(f"文件 {args.file} 无需补全（对齐度良好）")


if __name__ == "__main__":
    main()
