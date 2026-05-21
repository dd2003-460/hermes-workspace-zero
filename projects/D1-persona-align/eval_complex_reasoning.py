#!/usr/bin/env python3
"""
复杂问题分析能力 eval — 测推理和获取信息能力，非知识问答

设计原则：
1. 问题必须是经典复杂问题（no trivial answers）
2. 评估维度：能否识别问题边界、考虑多因素、区分相关与因果、处理不确定性
3. 不是"答对"，而是"如何思考"
4. 固定模型大小，比较不同 prompt/微调策略的分析能力差异

问题列表（从 raw.md 的思维方式中提取）：
- 男女数学天赋差异（经典复杂问题，需要区分生物/社会/教育因素）
- 智能的本质（信息与选择压力的必然性）
- Agent 规划能力评估（复杂问题的元思考）
- 概率与动力学的关系
- 信息论统一语言的边界
"""

import json, urllib.request, time, os, sys

API = 'http://127.0.0.1:8000/v1/chat/completions'
MODEL = 'Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit'

# 复杂问题列表 — 每个问题都有多面性，不能简单回答是/否
COMPLEX_QUESTIONS = [
    {
        'id': 'math_gender_gap',
        'question': '男女在数学天赋上是否存在差异？如何区分先天禀赋和后天环境的影响？',
        'tags': ['社科', '因果推断', '统计混淆'],
        'expected_complexity': '需要区分：统计分布差异 vs 均值差异、方差差异、社会建构的影响、历史变化趋势'
    },
    {
        'id': 'intelligence_definition',
        'question': '"信息+选择压力→智能"是否是必然推论？还是只是偶然工程产物？是否存在与实现无关的智能原理？',
        'tags': ['哲学', '信息论', '还原论'],
        'expected_complexity': '需要讨论：必要性证明的可能形式、反例构造、实现依赖性的含义'
    },
    {
        'id': 'agent_capability_test',
        'question': '如果让一个 AI agent 独立完成一个大型工程项目（如 coding 任务），它需要具备哪些核心能力？如何评估它的规划能力是否充分？',
        'tags': ['元认知', '能力评估', '系统设计'],
        'expected_complexity': '需要区分：知识能力 vs 规划能力 vs 执行能力 vs 自我修正能力'
    },
    {
        'id': 'probability_dynamics',
        'question': '"概率是动力学下的信息抹除"——这个观点在什么条件下成立？它和贝叶斯概率诠释的根本区别是什么？',
        'tags': ['数学哲学', '概率论', '认识论'],
        'expected_complexity': '需要讨论：epistemic vs ontic probability、粗粒化的数学定义、信息损失的严格形式化'
    },
    {
        'id': 'unified_language',
        'question': '语言、数学、物理、社会是否真的是同一套信息处理机制的不同表现？如果可以统一，统一的框架应该满足什么条件？如果不能，边界在哪里？',
        'tags': ['还原论', '跨学科', '形式化边界'],
        'expected_complexity': '需要讨论：同构 vs 类比、不同层级的约化、反约化论证的可能形式'
    },
]

STRATEGIES = {
    'baseline': {
        'system': None,
        'desc': '无特殊提示词（纯基线）'
    },
    'method_only': {
        'system': '你是一个研究者。分析问题时必须：1) 识别问题的所有关键变量 2) 区分相关和因果 3) 考虑可能的混淆因素 4) 明确你的结论在什么条件下成立。用中文。',
        'desc': '方法论提示（不指定 persona）'
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
    'chenglu_persona_plus_lora': {
        'system': None,
        'lora': 'lora_model.safetensors',
        'desc': 'chenglu persona + LoRA 微调'
    },
}

def call_api(system_content, message, max_tokens=2000, temperature=0.8, lora_path=None):
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
        # LoRA 参数 — 需要根据你的 API 实现调整
    }).encode()
    r = urllib.request.urlopen(urllib.request.Request(API, data=data, headers={'Content-Type': 'application/json'}), timeout=600)
    return json.loads(r.read())['choices'][0]['message']['content']

def score_response(response, question_info):
    """
    评分维度：
    1. block_structure: 是否有结构化分析（❏ 或编号列表）— 成璐风格的拆解
    2. question_ratio: 是否有追问/反问 — 成璐风格的"你说的意思是…？"
    3. cross_domain: 是否跨领域引用 — 成璐风格的多域引用
    4. uncertainty: 是否标记不确定性 — 成璐风格的不确定性意识
    5. depth: 是否触及问题本质（由关键词判断）
    6. length_reasonable: 回答长度是否足够（不敷衍）
    """
    score = {}
    
    # 1. 结构化分析
    if any(kw in response for kw in ['❏', '一、', '1.', '首先', '其次', '最后', '综上', '---']):
        score['block_structure'] = 1
    else:
        score['block_structure'] = 0
    
    # 2. 追问/反问
    question_count = response.count('？')
    if question_count >= 2:
        score['question_ratio'] = 1
    elif question_count == 1:
        score['question_ratio'] = 0.5
    else:
        score['question_ratio'] = 0
    
    # 3. 跨域引用
    domain_words = ['信息论', '数学', '物理', '生物', '社会', '经济学', '哲学', '认知科学', '神经科学', '计算机科学']
    found_domains = [d for d in domain_words if d in response]
    if len(found_domains) >= 2:
        score['cross_domain'] = 1
    elif len(found_domains) == 1:
        score['cross_domain'] = 0.5
    else:
        score['cross_domain'] = 0
    
    # 4. 不确定性标记
    uncertainty_words = ['可能', '不确定', '需要验证', '假设', '如果...则', '未必', '取决于', '尚无结论']
    uncertainty_count = sum(response.count(w) for w in uncertainty_words)
    if uncertainty_count >= 2:
        score['uncertainty'] = 1
    elif uncertainty_count == 1:
        score['uncertainty'] = 0.5
    else:
        score['uncertainty'] = 0
    
    # 5. 深度（关键词密度）
    depth_keywords = [
        # 问题特定关键词（每个问题的 expected_complexity 中暗示的）
        '混淆', '因果', '相关', '机制', '形式化', '边界', '条件', '等价',
        '同构', '约化', '涌现', '粗粒化', '先验', '后验', '贝叶斯',
    ]
    depth_count = sum(response.count(kw) for kw in depth_keywords)
    score['depth'] = min(1, depth_count / 3)  # 3+ 关键词 = 满分
    
    # 6. 长度合理性
    if len(response) >= 300:
        score['length_reasonable'] = 1
    elif len(response) >= 150:
        score['length_reasonable'] = 0.5
    else:
        score['length_reasonable'] = 0
    
    # 加权总分（block_structure + depth 权重高）
    weights = {
        'block_structure': 1.0,
        'question_ratio': 1.0,
        'cross_domain': 0.8,
        'uncertainty': 1.0,
        'depth': 1.5,  # 权重最高 — 深度最重要
        'length_reasonable': 0.5,
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
                if strategy.get('lora'):
                    text = call_api(strategy['system'], qa['question'], lora_path=strategy.get('lora'))
                else:
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
                print(f'  Block: {score["block_structure"]}, Question: {score["question_ratio"]}, Cross-domain: {score["cross_domain"]}', flush=True)
                print(f'  Uncertainty: {score["uncertainty"]}, Depth: {score["depth"]:.2f}', flush=True)
                
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
        with open(os.path.join(outputs_dir, f'eval_complex_{strategy_key}.json'), 'w', encoding='utf-8') as f:
            json.dump(strategy_results, f, ensure_ascii=False, indent=2)
        print(f'\nSaved: eval_results/eval_complex_{strategy_key}.json', flush=True)
        time.sleep(2)  # 策略间等待
    
    # 汇总对比
    print(f'\n{"="*60}', flush=True)
    print('FINAL COMPARISON', flush=True)
    print(f'{"="*60}', flush=True)
    
    summary = {}
    for strategy_key in all_results:
        scores = []
        for qa_id, result in all_results[strategy_key].items():
            if result.get('score'):
                scores.append(result['score']['weighted_score'])
        if scores:
            avg = sum(scores) / len(scores)
            summary[strategy_key] = {
                'avg_score': avg,
                'num_questions': len(scores),
                'per_question': {k: v['score'] for k, v in all_results[strategy_key].items() if v.get('score')}
            }
            print(f'\n{strategy_key} ({STRATEGIES[strategy_key]["desc"]}): {avg:.2%} avg', flush=True)
        else:
            print(f'\n{strategy_key}: NO RESULTS', flush=True)
    
    # Save summary
    with open(os.path.join(outputs_dir, 'eval_complex_summary.json'), 'w', encoding='utf-8') as f:
        json.dump({
            'questions': [{'id': q['id'], 'tags': q['tags']} for q in COMPLEX_QUESTIONS],
            'summary': summary,
            'all_results': all_results,
        }, f, ensure_ascii=False, indent=2)
    
    print(f'\nSaved: eval_results/eval_complex_summary.json', flush=True)
    return summary

if __name__ == '__main__':
    summary = run_eval()
    # Print final ranking
    print(f'\n{"="*60}', flush=True)
    print('RANKING', flush=True)
    print(f'{"="*60}', flush=True)
    ranked = sorted(summary.items(), key=lambda x: x[1]['avg_score'], reverse=True)
    for rank, (key, data) in enumerate(ranked, 1):
        print(f'  #{rank} {key}: {data["avg_score"]:.2%} ({STRATEGIES[key]["desc"]})')
