#!/usr/bin/env python3
"""
思维引擎 v2 — 修正评分系统后重新评估

核心改进:
1. 评分系统修正 — 长度去偏化，引入 density 维度
2. 新增 strategy: thinking_engine_v2 + thinking_engine_v2_strict

修正的评分系统:
- length_reasonable → length_penalty 取代（>3000 字开始扣分）
- 移除 block_structure（纯长度相关）
- 移除 cross_domain（纯长度相关）
- 新增 density: 关键词数 / 字数 * 1000（信息密度）
- 新增 conciseness: 断言句 / 总句数（表达效率）
"""

import json, urllib.request, time, os, re, sys

API = 'http://127.0.0.1:8000/v1/chat/completions'
MODEL = 'Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit'

COMPLEX_QUESTIONS = [
    {
        'id': 'math_gender_gap',
        'question': '男女在数学天赋上是否存在差异？如何区分先天禀赋和后天环境的影响？',
        'tags': ['社科', '因果推断', '统计混淆'],
    },
    {
        'id': 'intelligence_definition',
        'question': '"信息+选择压力→智能"是否是必然推论？还是只是偶然工程产物？是否存在与实现无关的智能原理？',
        'tags': ['哲学', '信息论', '还原论'],
    },
    {
        'id': 'agent_capability_test',
        'question': '如果让一个 AI agent 独立完成一个大型工程项目（如 coding 任务），它需要具备哪些核心能力？如何评估它的规划能力是否充分？',
        'tags': ['元认知', '能力评估', '系统设计'],
    },
    {
        'id': 'probability_dynamics',
        'question': '"概率是动力学下的信息抹除"——这个观点在什么条件下成立？它和贝叶斯概率诠释的根本区别是什么？',
        'tags': ['数学哲学', '概率论', '认识论'],
    },
    {
        'id': 'unified_language',
        'question': '语言、数学、物理、社会是否真的是同一套信息处理机制的不同表现？如果可以统一，统一的框架应该满足什么条件？如果不能，边界在哪里？',
        'tags': ['还原论', '跨学科', '形式化边界'],
    },
]

# ============================================================
# 各策略的 system prompt
# ============================================================
STRATEGIES = {
    'method_only': {
        'system': '你是一个研究者。分析问题时必须：1) 识别问题的所有关键变量 2) 区分相关和因果 3) 考虑可能的混淆因素 4) 明确你的结论在什么条件下成立。用中文。',
        'desc': '方法论提示（基准）'
    },
    'chenglu_persona': {
        'system': '''你是成璐的AI助手。你的思维特征：
1. 贝叶斯思维：先验→证据→后验→新先验，闭环
2. 信息论视角：语言/数学/物理/社会都是同一信息处理机制的不同信道
3. 直觉是高维推理的压缩，追问"你说的意思是…？"
4. 概率是动力学下的信息抹除
5. 简洁直接，先证据后结论
6. 遇到复杂问题先拆解，考虑多路径，不急于下结论

用中文回答。''',
        'desc': '成璐 persona 提示词'
    },
    'thinking_engine_v2': {
        'system': '''分析复杂问题时，按以下框架工作：

1. 类型识别 → 选择分析工具
2. 变量分析 → 识别关键变量及关系
3. 因果推断 → 区分因果和相关
4. 边界追问 → 结论在什么条件下成立/失效
5. 不确定度 → 标注每个结论的可信度

用中文回答，简洁直接。不要废话。''',
        'desc': '思维引擎 v2（5 工具提示，非强制结构）'
    },
    'thinking_engine_v2_strict': {
        'system': '''分析时: ①识别变量 ②区分因果 ③边界追问 ④不确定度标注。用中文，简洁直接。''',
        'desc': '思维引擎 v2 strict（极简提示）'
    },
}


def call_api(system_content, message, max_tokens=3000, temperature=0.8):
    msgs = []
    if system_content:
        msgs.append({'role': 'system', 'content': system_content})
    msgs.append({'role': 'user', 'content': message})
    data = json.dumps({
        'model': MODEL,
        'messages': msgs,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'stream': False,
    }).encode()
    r = urllib.request.urlopen(urllib.request.Request(API, data=data, headers={'Content-Type': 'application/json'}), timeout=600)
    return json.loads(r.read())['choices'][0]['message']['content']


def sentence_split(text):
    """分割中文句子"""
    # 按中文标点分割
    sentences = re.split(r'[。！？；\n]', text)
    return [s.strip() for s in sentences if s.strip()]


def score_response(response, question_info):
    """
    修正后的评分系统（长度去偏化）:
    1. depth: 关键词密度 / 3, 上限 1.0（不变，但与长度无关）
    2. uncertainty: 不确定性标记，上限 1.0（不变）
    3. question_ratio: 反问/追问，上限 1.0（不变）
    4. density: 信息密度 = 关键词数 / 字数 * 1000，上限 1.0（新增）
    5. conclusion_density: 断言句比例，最佳区间 0.2-0.5（新增）
    6. length_penalty: 超过 2500 字开始线性扣分（修正）
    7. block_structure 和 cross_domain 已移除（纯长度相关）
    """
    score = {}
    text_len = len(response)

    # 关键词列表
    depth_keywords = [
        '混淆', '因果', '相关', '机制', '形式化', '边界', '条件', '等价',
        '同构', '约化', '涌现', '粗粒化', '先验', '后验', '贝叶斯',
        '变量', '假设', '推断', '证明', '充分', '必要', '映射', '结构',
    ]

    uncertainty_words = [
        '可能', '不确定', '需要验证', '假设', '如果...则', '未必',
        '取决于', '尚无结论', '高置信', '中置信', '低置信', '未必',
        '不一定', '在...条件下', '除非', '仅当',
    ]

    # 1. depth（关键词密度）
    depth_count = sum(response.count(kw) for kw in depth_keywords)
    score['depth'] = min(1, depth_count / 3)

    # 2. uncertainty
    uncertainty_count = sum(response.count(w) for w in uncertainty_words)
    score['uncertainty'] = min(1, uncertainty_count / 2)

    # 3. question_ratio
    question_count = response.count('？')
    score['question_ratio'] = min(1, question_count / 2)

    # 4. density（新增：信息密度 = 关键词数 / 字数 * 1000）
    density = depth_count / max(1, text_len) * 1000
    score['density'] = min(1, density / 2)  # 2+ keywords per 1000 chars = perfect

    # 5. conclusion_density（新增：断言句比例）
    sentences = sentence_split(response)
    num_sentences = max(1, len(sentences))
    # 断言句 = 包含判断性词汇的句子
    assertive_keywords = ['是', '不是', '意味着', '反映', '源于', '取决于', '本质上', '关键在于']
    assertive_count = sum(1 for s in sentences if any(kw in s for kw in assertive_keywords))
    assertive_ratio = assertive_count / num_sentences
    # 最佳区间 0.2-0.5
    if 0.2 <= assertive_ratio <= 0.5:
        score['conclusion_density'] = 1.0
    elif 0.1 <= assertive_ratio < 0.2 or 0.5 < assertive_ratio <= 0.7:
        score['conclusion_density'] = 0.7
    else:
        score['conclusion_density'] = max(0.3, 1.0 - abs(assertive_ratio - 0.35) * 2)

    # 6. length_penalty（修正：>2500 字开始线性扣分）
    if text_len <= 2500:
        score['length_penalty'] = 1.0
    elif text_len <= 4000:
        score['length_penalty'] = 1.0 - (text_len - 2500) / 3000  # 2500-4000: 1.0 → 0.5
    else:
        score['length_penalty'] = max(0.3, 0.5 - (text_len - 4000) / 6000)  # 4000+: 最低 0.3

    # 加权总分 — 移除了 block_structure (1.0) 和 cross_domain (0.8)
    weights = {
        'depth': 1.5,
        'uncertainty': 1.0,
        'question_ratio': 1.0,
        'density': 1.0,       # 新增
        'conclusion_density': 0.8,  # 新增
        'length_penalty': 0.3,  # 降低权重
    }

    total_weighted = sum(score[k] * weights[k] for k in score)
    max_weighted = sum(weights[k] for k in score)
    score['weighted_score'] = total_weighted / max_weighted

    return score


def run_eval():
    outputs_dir = '/Users/a1-6/Desktop/workspace/projects/D1-persona-align/eval_results'
    os.makedirs(outputs_dir, exist_ok=True)

    all_results = {}

    for strategy_key, strategy in STRATEGIES.items():
        print(f'\n{"="*60}', flush=True)
        print(f'Strategy: {strategy_key} — {strategy["desc"]}', flush=True)
        print(f'{"="*60}', flush=True)

        strategy_results = {}

        for qi, qa in enumerate(COMPLEX_QUESTIONS):
            print(f'\n[{qi+1}/{len(COMPLEX_QUESTIONS)}] {qa["id"]}: {qa["question"][:50]}...', flush=True)

            try:
                text = call_api(strategy['system'], qa['question'])

                # 剥离 thinking tags
                if '</think>' in text:
                    text = text.split('</think>', 1)[1].strip()

                score = score_response(text, qa)

                strategy_results[qa['id']] = {
                    'score': score,
                    'response_length': len(text),
                    'question': qa['question'][:80],
                    'tags': qa['tags'],
                }

                print(f'  Score: {score["weighted_score"]:.2%} | Length: {len(text)} chars', flush=True)
                print(f'  Depth: {score["depth"]:.2f}, Uncertainty: {score["uncertainty"]:.2f}, Question: {score["question_ratio"]:.2f}', flush=True)
                print(f'  Density: {score["density"]:.2f}, ConclusionDensity: {score["conclusion_density"]:.2f}, LenPenalty: {score["length_penalty"]:.2f}', flush=True)

            except Exception as e:
                strategy_results[qa['id']] = {
                    'score': None,
                    'error': str(e),
                    'response_length': 0,
                }
                print(f'  ERROR: {e}', flush=True)

            time.sleep(1)

        all_results[strategy_key] = strategy_results

        # Save per-strategy results
        with open(os.path.join(outputs_dir, f'eval_v2_{strategy_key}.json'), 'w', encoding='utf-8') as f:
            json.dump(strategy_results, f, ensure_ascii=False, indent=2)
        print(f'\nSaved: eval_results/eval_v2_{strategy_key}.json', flush=True)
        time.sleep(2)

    # Summary
    print(f'\n{"="*60}', flush=True)
    print('FINAL COMPARISON (修正评分系统)', flush=True)
    print(f'{"="*60}', flush=True)

    summary = {}
    for strategy_key in all_results:
        scores = []
        for qa_id, result in all_results[strategy_key].items():
            if result.get('score'):
                scores.append(result['score']['weighted_score'])
        if scores:
            avg = sum(scores) / len(scores)
            avg_len = sum(r['response_length'] for r in all_results[strategy_key].values() if 'response_length' in r) / len(scores)
            summary[strategy_key] = {
                'avg_score': avg,
                'avg_length': avg_len,
                'num_questions': len(scores),
                'per_question': {k: v['score'] for k, v in all_results[strategy_key].items() if v.get('score')}
            }
            print(f'\n{strategy_key} ({STRATEGIES[strategy_key]["desc"]}): {avg:.2%} avg | {avg_len:.0f} chars avg', flush=True)
        else:
            print(f'\n{strategy_key}: NO RESULTS', flush=True)

    # Save summary
    with open(os.path.join(outputs_dir, 'eval_v2_summary.json'), 'w', encoding='utf-8') as f:
        json.dump({
            'questions': [{'id': q['id'], 'tags': q['tags']} for q in COMPLEX_QUESTIONS],
            'summary': summary,
            'all_results': all_results,
        }, f, ensure_ascii=False, indent=2)

    # Print ranking
    print(f'\n{"="*60}', flush=True)
    print('RANKING (修正评分系统)', flush=True)
    print(f'{"="*60}', flush=True)
    ranked = sorted(summary.items(), key=lambda x: x[1]['avg_score'], reverse=True)
    for rank, (key, data) in enumerate(ranked, 1):
        print(f'  #{rank} {key}: {data["avg_score"]:.2%} avg ({STRATEGIES[key]["desc"]}) | avg length: {data["avg_length"]:.0f} chars', flush=True)

    print(f'\nSaved: eval_results/eval_v2_summary.json', flush=True)
    return summary


if __name__ == '__main__':
    summary = run_eval()
    print(f'\nRanking:')
    ranked = sorted(summary.items(), key=lambda x: x[1]['avg_score'], reverse=True)
    for rank, (key, data) in enumerate(ranked, 1):
        print(f'  #{rank} {key}: {data["avg_score"]:.2%} ({STRATEGIES[key]["desc"]})')
